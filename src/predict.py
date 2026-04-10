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
    return payload["model"], payload["feature_columns"]