import pandas as pd
from collections import defaultdict
from src.fetch import get_race_data

def get_final_positions(position_records: list, driver_number: int) -> int | None:
    driver_records = [p for p in position_records if p["driver_number"] == driver_number]
    if not driver_records:
        return None
    return driver_records[-1]["position"]

def get_grid_position(quali_records: list, driver_number: int) -> int | None:
    driver_records = [p for p in quali_records if p["driver_number"] == driver_number]
    if not driver_records:
        return None
    return driver_records[-1]["position"]

def build_features(years: list[int]) -> pd.DataFrame:
    all_rows = []
    
    driver_finish_history = defaultdict(list)
    constructor_finish_history = defaultdict(list)
    circuit_finish_history = defaultdict(list)

    for year in years:
        print(f"Building features for {year}...")
        races = get_race_data(year)

        for race in races:
            session = race["session"]
            session_key = session["session_key"]
            circuit_key = session.get("circuit_key", "Unknown")
            meeting_key = session["meeting_key"]

            drivers = race["drivers"]
            race_positions = race["race_positions"]
            quali_positions = race["quali_positions"]

            driver_team = {d["driver_number"]: d["team_name"] for d in drivers}

            champ_points = {}
            for dn, history in driver_finish_history.items():
                champ_points[dn] = sum(1 for f in history if f <= 10)
            
            sorted_champ = sorted(champ_points.items(), key= lambda x: -x[1])
            champ_position_lookup = {dn: i + 1 for i, (dn, _) in enumerate(sorted_champ)}

            for driver in drivers:
                dn = driver["driver_number"]
                team = driver["team_name"]

                finish_position = get_final_positions(race_positions, dn)
                grid_position = get_grid_position(quali_positions, dn)

                if finish_position is None:
                    continue

                recent_finishes = driver_finish_history[dn][-5:]
                driver_avg = sum(recent_finishes) / len(recent_finishes) if recent_finishes else 10.0

                recent_constructor = constructor_finish_history[team][-10:]
                constructor_avg = sum(recent_constructor) / len(recent_constructor) if recent_constructor else 10.0

                circuit_key_driver = (dn, circuit_key)
                circuit_finishes = circuit_finish_history[circuit_key_driver]
                circuit_avg = sum(circuit_finishes) / len(circuit_finishes) if circuit_finishes else 10.0

                champ_position = champ_position_lookup.get(dn, 20)

                all_rows.append({
                    "session_key": session_key,
                    "meeting_key": meeting_key,
                    "circuit_key": circuit_key,
                    "year": year,
                    "driver_number": dn,
                    "driver_name": driver["name_acronym"],
                    "team_name": team,
                    "grid_position": grid_position,
                    "driver_avg_finish_last5": driver_avg,
                    "constructor_avg_finish_last5": constructor_avg,
                    "driver_circuit_avg_finish": circuit_avg,
                    "championship_position": champ_position,
                    "finish_position": finish_position,
                    "top10": 1 if finish_position <= 10 else 0,
                })

                driver_finish_history[dn].append(finish_position)
                constructor_finish_history[team].append(finish_position)
                circuit_finish_history[circuit_key_driver].append(finish_position)

    df = pd.DataFrame(all_rows)
    print(f"Built {len(df)} rows across {df['session_key'].nunique()} races.")
    return df

if __name__ == "__main__":
    df = build_features([2023, 2024])
    print(df.head(20).to_string())
    print(f"\nFeature Columns: {list(df.columns)}")
    print(f"\nTop10 Balance: {df['top10'].value_counts().to_dict()}")

