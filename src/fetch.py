import requests
import json
import os
import time
from pathlib import Path

BASE_URL = "https://api.openf1.org/v1"
CACHE_DIR = Path("data/raw")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(name: str) -> Path:
    return CACHE_DIR / f"{name}.json"

def _get(endpoint: str, params:dict, cache_key: str, force_refresh: bool = False) -> list:
    """
    Core fetch helper. Checks the local cache first, then hits the API.
    Retries once on rate limit (429).
    """
    path = _cache_path(cache_key)

    if path.exists() and not force_refresh:
        with open(path, "r") as f:
            return json.load(f)
        
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(2):
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            with open(path, "w") as f:
                json.dump(data, f)
            return data
        elif response.status_code == 429:
            print(f"Rate limit hit. Waiting 10s before retrying...")
            time.sleep(10)
        else:
            response.raise_for_status()
    raise Exception(f"Failed to fetch {endpoint} after retries.")

def get_sessions(year: int) -> list:
    data = _get(
        endpoint="sessions",
        params={"year": year, "session_name": "Race"},
        cache_key=f"sessions_{year}"
    )
    return data

def get_drivers(session_key: int) -> list:
    return _get(
        endpoint="drivers",
        params={"session_key": session_key},
        cache_key=f"drivers_{session_key}"
    )

def get_positions(session_key: int) -> list:
    return _get(
        endpoint="position",
        params={"session_key": session_key},
        cache_key=f"position_{session_key}"
    )

def get_qualifying_results(session_key: int) -> list:
    return _get(
        endpoint="position",
        params={"session_key": session_key},
        cache_key=f"qualifying_{session_key}"
    )

def get_qualifying_session(year: int, meeting_key: int) -> dict | None:
    data = _get(
        endpoint="sessions",
        params={"year": year, "meeting_key": meeting_key, "session_name": "Qualifying"},
        cache_key=f"quali_session_{meeting_key}"
    )
    return data[0] if data else None

def get_race_data(year: int) -> list:
    sessions = get_sessions(year)
    races = []

    for session in sessions:
        session_key = session["session_key"]
        meeting_key = session["meeting_key"]
        circuit = session.get("circuit_short_name", session.get("circuit_key", "Unknown"))
        print(f"Fetching data for: {circuit} {year}...")

        try:
            drivers = get_drivers(session_key)
            if not drivers:
                print(f"  Skipping {circuit} — no driver data (likely cancelled).")
                continue

            race_positions = get_positions(session_key)

            quali_session = get_qualifying_session(year, meeting_key)
            quali_positions = get_positions(quali_session["session_key"]) if quali_session else []

            races.append({
                "session": session,
                "drivers": drivers,
                "race_positions": race_positions,
                "quali_positions": quali_positions,
            })

        except Exception as e:
            print(f"  Skipping {circuit} — error: {e}")
            continue

        time.sleep(0.5)

    return races

if __name__ == "__main__":
    races = get_race_data(2023)
    print(f"\nFetched {len(races)} races.")
    if races:
        first = races[0]
        print(f"First race: {first['session'].get('meeting_name')}")
        print(f"Drivers: {len(first['drivers'])}")
        print(f"Race position records: {len(first['race_positions'])}")
        print(f"Qualifying position records: {len(first['quali_positions'])}")





