from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mock_data import sample_forecast
from grap import get_grap_stage
from models import (
    ForecastResponse,
    InversionReading,
    PlumesResponse,
    CompareResponse,
    GrapStatus,
)

app = FastAPI(title="Delhi NCR Coupled AQI API")

# CORS: this is a permission slip that lets M6's website (running on a
# different address) be allowed to ask your front desk questions.
# Without this, browsers block the request for security reasons.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for Day 1 testing only — tighten this on Day 2
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "the front desk is open"}

@app.get("/forecast", response_model=ForecastResponse)
def forecast():
    return {"stations": sample_forecast}

@app.get("/inversion", response_model=InversionReading)
def inversion():
    # fake placeholder until Member 2/4 give you real data
    return {"region": "NCR", "inversion_strength": "moderate", "delta_t": 3.2}

@app.get("/plumes", response_model=PlumesResponse)
def plumes():
    # fake placeholder until Member 2 gives you real smoke-trajectory data
    return {"plumes": [{"source": "Punjab", "frp": 145.2, "direction": "SE"}]}

@app.get("/compare", response_model=CompareResponse)
def compare():
    # this endpoint shows coupled vs uncoupled AQI side by side —
    # the core "why our model is better" evidence for judges
    return {
        "stations": [
            {
                "station_name": s["station_name"],
                "hour": s["hour"],
                "coupled_aqi": s["coupled_aqi"],
                "uncoupled_aqi": s["uncoupled_aqi"],
                "difference": s["coupled_aqi"] - s["uncoupled_aqi"],
            }
            for s in sample_forecast
        ]
    }

@app.get("/grap/status", response_model=GrapStatus)
def grap_status():
    # takes the worst (highest) coupled AQI across all stations right now
    worst_aqi = max(s["coupled_aqi"] for s in sample_forecast)
    return {
        "worst_current_aqi": worst_aqi,
        "triggered_stage": get_grap_stage(worst_aqi),
    }