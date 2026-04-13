import pickle
import pandas as pd
from pathlib import Path
from src.fetch import (
    get_sessions,
    get_drivers,
    get_positions,
    get_qualifying_session
)
from src.features import (
    get_final_positions,
    get_grid_position
)

MODEL_PATH = Path("models/rf_model.pkl")

def load_model():
    with open(MODEL_PATH, "rb") as f:
        payload = pickle.load(f)
    return payload["model"], payload["feature_cols"]

def get_upcoming_race(year: int) -> dict | None:
    sessions = get_sessions(year)

    for session in sessions:
        session_key = session["session_key"]
        meeting_key = session["meeting_key"]

        quali_session = get_qualifying_session(year, meeting_key)
        if not quali_session:
            continue
        
        try:
            quali_positions = get_positions(quali_session["session_key"])
        except Exception:
            continue

        if not quali_positions:
            continue
        
        try:    
            race_positions = get_positions(session_key)
        except Exception:
            continue

        if race_positions:
            continue

        try:
            drivers = get_drivers(session_key)
        except Exception:
            continue

        return {
            "session": session,
            "quali_positions": quali_positions,
            "drivers": get_drivers(session_key)
        }
    return None

def predict_race(year: int, driver_history: dict, constructor_history: dict) -> list:
    model, feature_cols = load_model()

    race = get_upcoming_race(year)
    if not race:
        print("No upcoming race found with qualifying data available.")
        return []
    
    session = race["session"]
    circuit = session.get("circuit_short_name", "Unknown")
    print(f"Predicting: {circuit} {year}")

    drivers = race["drivers"]
    quali_positions = race["quali_positions"]

    rows = []
    for driver in drivers:
        dn = driver["driver_number"]
        team = driver["team_name"]

        grid_pos = get_grid_position(quali_positions, dn)

        recent_finishes = driver_history.get(dn, [])[-5:]
        driver_avg = sum(recent_finishes) / len(recent_finishes) if recent_finishes else 10

        recent_constructor = constructor_history.get(team, [])[-10:]
        constructor_avg = sum(recent_constructor) / len(recent_constructor) if recent_constructor else 10

        rows.append({
            "driver_number": dn,
            "driver_name": driver["name_acronym"],
            "team_name": team,
            "grid_position": grid_pos if grid_pos is not None else 15,
            "driver_avg_finish_last5": driver_avg,
            "constructor_avg_finish_last5": constructor_avg,
            "driver_circuit_avg_finish": driver_avg,
            "championship_position": 10
        })
    
    df = pd.DataFrame(rows)
    X = df[feature_cols]

    probabilities = model.predict_proba(X)[:, 1]
    df["top10_probability"] = probabilities

    results = df[["driver_name", "team_name", "grid_position", "top10_probability"]]
    results = results.sort_values("top10_probability", ascending=False).reset_index(drop=True)
    results.index += 1 #Start index at 1

    return results.to_dict(orient="records")

if __name__ == "__main__":
    results = predict_race(2026, driver_history={}, constructor_history={})

    if results:
        print(f"\n{'Rank':<6}{'Driver':<8}{'Team':<25}{'Grid':<8}{'Top10 Prob'}")
        print("-" * 55)
        for i, r in enumerate(results, 1):
            prob_bar = "#" * int(r["top10_probability"] * 20)
            print(
                f"{i:<6}{r['driver_name']:<8}{r['team_name']:<25}"
                f"{r['grid_position']:<8}{r['top10_probability']:.3f} {prob_bar}"
            )



