from typing import Literal
from pydantic import BaseModel, Field


# ---------- Forecast ----------
class StationForecast(BaseModel):
    station_name: str
    hour: int = Field(ge=0, le=72)
    pm25: float = Field(ge=0)
    coupled_aqi: int = Field(ge=0, le=500)
    uncoupled_aqi: int = Field(ge=0, le=500)

class ForecastResponse(BaseModel):
    stations: list[StationForecast]


# ---------- Inversion ----------
class InversionReading(BaseModel):
    region: str
    inversion_strength: Literal["none", "weak", "moderate", "strong"]
    delta_t: float


# ---------- Plumes ----------
class Plume(BaseModel):
    source: str
    frp: float = Field(ge=0)
    direction: str

class PlumesResponse(BaseModel):
    plumes: list[Plume]


# ---------- Compare ----------
class CompareRow(BaseModel):
    station_name: str
    hour: int = Field(ge=0, le=72)
    coupled_aqi: int = Field(ge=0, le=500)
    uncoupled_aqi: int = Field(ge=0, le=500)
    difference: int

class CompareResponse(BaseModel):
    stations: list[CompareRow]


# ---------- GRAP ----------
class GrapStatus(BaseModel):
    worst_current_aqi: int
    triggered_stage: str