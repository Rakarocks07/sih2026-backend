from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data_loader import load_forecast, load_plumes
from grap import get_grap_stage

app = FastAPI(
    title="Delhi NCR Coupled AQI API",
    description="72-hour coupled weather + pollution AQI forecast for Delhi NCR (SIH 2026).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this once M6's real site address is known
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Delhi NCR Coupled AQI API is running",
        "docs": "/docs",
        "endpoints": [
            "/api/v1/forecast",
            "/api/v1/plumes",
            "/inversion",
            "/compare",
            "/grap/status",
        ],
    }


@app.get("/health")
def health():
    return {"status": "the front desk is open"}


# ---------------------------------------------------------------
# Member 4 asked for these two to be served exactly as their files
# are written, with no reshaping — so no Pydantic model here, just
# the raw dict / GeoJSON, straight from disk (through the cache).
# ---------------------------------------------------------------

@app.get("/api/v1/forecast")
def forecast_v1(station: str | None = None):
    data = load_forecast()
    if station is None:
        return data
    matches = [s for s in data["stations"] if s["station_id"].lower() == station.lower()]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Unknown station '{station}'")
    return {"meta": data["meta"], "stations": matches}


@app.get("/api/v1/plumes")
def plumes_v1():
    return load_plumes()


# Old paths kept as aliases, so Member 6's current frontend doesn't
# break while they migrate to the new /api/v1/... paths.
app.add_api_route("/forecast", forecast_v1, methods=["GET"])
app.add_api_route("/plumes", plumes_v1, methods=["GET"])


@app.get("/inversion")
def inversion():
    # still a placeholder — waiting on a dedicated inversion feed from Member 2
    return {"region": "NCR", "inversion_strength": "moderate", "delta_t": 3.2}


@app.get("/compare")
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


@app.get("/grap/status")
def grap_status():
    data = load_forecast()

    # "Right now" per station comes straight from Member 4's own
    # current_conditions block plus hour-0 AQI — not recomputed here.
    now_by_station = [
        {
            "station_id": s["station_id"],
            "station_name": s["station_name"],
            "aqi_now": s["hourly"][0]["aqi_coupled"],
            "grap_stage": s["hourly"][0]["grap_stage"],
            "grap_action": s["hourly"][0]["grap_action"],
            "current_conditions": s.get("current_conditions"),
        }
        for s in data["stations"]
    ]
    worst_now = max(now_by_station, key=lambda r: r["aqi_now"])

    # Worst moment anywhere in the 72-hour window
    peak_aqi, peak_hour, peak_station = 0, 0, None
    for s in data["stations"]:
        for hr in s["hourly"]:
            if hr["aqi_coupled"] > peak_aqi:
                peak_aqi, peak_hour, peak_station = hr["aqi_coupled"], hr["h"], s["station_id"]

    return {
        "worst_current_aqi": worst_now["aqi_now"],
        "worst_current_station": worst_now["station_id"],
        "triggered_stage": get_grap_stage(worst_now["aqi_now"]),
        "peak_72h_aqi": peak_aqi,
        "peak_hour": peak_hour,
        "peak_station": peak_station,
        "peak_stage": get_grap_stage(peak_aqi),
        "stations_now": now_by_station,
    }
