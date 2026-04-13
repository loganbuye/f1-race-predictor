from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.features import build_features
from src.predict import predict_race
from collections import defaultdict

app = FastAPI(title = "F1 Race Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")

async def build_history():
    global g_driver_history, g_constructor_history
    g_driver_history = defaultdict(list)
    g_constructor_history = defaultdict(list)

    print("Building historical data...")
    df = build_features([2023, 2024])

    for _, row in df.iterrows():
        g_driver_history[row['driver_number']].append(int(row['finish_position']))
        g_constructor_history[row['team_name']].append(int(row['finish_position']))

    print("History ready.")

@app.get("/")
def root():
    return {"status": "ok", "message": "F1 Race Predictor"}

@app.get("/predict/{year}")
def predict(year: int):
    if year < 2026:
        raise HTTPException(status_code=400, detail="Predictions are only available for 2026 and beyond.")
    
    results = predict_race(year, driver_history = g_driver_history, constructor_history = g_constructor_history)

    if not results:
        raise HTTPException(status_code=404, detail="No upcoming races found with qualifying data.")
    
    return {
        "year": year,
        "predictions": results
    }

@app.get("/history/{driver_number}")
def driver_history_endpoint(driver_number: int):
    history = g_driver_history.get(driver_number, [])

    if not history:
        raise HTTPException(status_code=404, detail="No history found for the specified driver number.")
    
    return {
        "driver_number": driver_number,
        "finish_history": history,
        "avg_finish": round(sum(history) / len(history), 2),
        "races": len(history)
    }
