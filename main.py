from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data_loader import load_forecast
from grap import get_grap_stage
from models import (
    ForecastResponse,
    InversionReading,
    PlumesResponse,
    CompareResponse,
    GrapStatus,
)

app = FastAPI(
    title="Delhi NCR Coupled AQI API",
    description="72-hour coupled weather + pollution AQI forecast for Delhi NCR (SIH 2026).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Delhi NCR Coupled AQI API is running",
        "docs": "/docs",
        "endpoints": ["/forecast", "/inversion", "/plumes", "/compare", "/grap/status"],
    }


@app.get("/health")
def health():
    return {"status": "the front desk is open"}


@app.get("/forecast", response_model=ForecastResponse)
def forecast(station: str | None = None):
    data = load_forecast()
    if station is None:
        return data
    matches = [s for s in data["stations"] if s["station_id"].lower() == station.lower()]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Unknown station '{station}'")
    return {"meta": data["meta"], "stations": matches}


@app.get("/inversion", response_model=InversionReading)
def inversion():
    # still fake until Member 2 sends real data
    return {"region": "NCR", "inversion_strength": "moderate", "delta_t": 3.2}


@app.get("/plumes", response_model=PlumesResponse)
def plumes():
    # still fake until Member 2 sends real data
    return {"plumes": [{"source": "Punjab", "frp": 145.2, "direction": "SE"}]}


@app.get("/compare", response_model=CompareResponse)
def compare():
    data = load_forecast()
    return {
        "stations": [
            {
                "station_id": s["station_id"],
                "station_name": s["station_name"],
                "rows": [
                    {
                        "h": hr["h"],
                        "time": hr["time"],
                        "aqi_coupled": hr["aqi_coupled"],
                        "aqi_uncoupled": hr["aqi_uncoupled"],
                        "difference": hr["aqi_coupled"] - hr["aqi_uncoupled"],
                    }
                    for hr in s["hourly"]
                ],
            }
            for s in data["stations"]
        ]
    }


@app.get("/grap/status", response_model=GrapStatus)
def grap_status():
    data = load_forecast()

    # "Right now" = hour 0, worst station
    worst_now = max(s["hourly"][0]["aqi_coupled"] for s in data["stations"])

    # Worst moment in the whole 72 hours, across all stations
    peak_aqi, peak_hour = 0, 0
    for s in data["stations"]:
        for hr in s["hourly"]:
            if hr["aqi_coupled"] > peak_aqi:
                peak_aqi, peak_hour = hr["aqi_coupled"], hr["h"]

    return {
        "worst_current_aqi": worst_now,
        "triggered_stage": get_grap_stage(worst_now),
        "peak_72h_aqi": peak_aqi,
        "peak_hour": peak_hour,
        "peak_stage": get_grap_stage(peak_aqi),
    }

