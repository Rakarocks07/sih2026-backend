from typing import Literal
from pydantic import BaseModel, Field


# ---------- Forecast (real data from Member 4) ----------
class HourlyPoint(BaseModel):
    h: int = Field(ge=0, le=72)
    time: str
    pm25_uncoupled: float = Field(ge=0)
    pm25_coupled: float = Field(ge=0)
    aqi_uncoupled: int = Field(ge=0, le=500)
    aqi_coupled: int = Field(ge=0, le=500)
    aqi_source: Literal["ml_real", "derived_from_pm25"]
    o3_uncoupled: float
    o3_coupled: float
    sw_clear: float
    sw_dimmed: float
    dimming_pct: float
    pbl_uncoupled: float
    pbl_coupled: float
    T2m_uncoupled: float
    T2m_coupled: float
    wind: float
    ventilation_uncoupled: float
    ventilation_coupled: float
    stagnation_coupled: bool
    inversion_gamma: float
    grap_stage: int = Field(ge=0, le=4)
    grap_action: str


class Station(BaseModel):
    station_id: str
    station_name: str
    coordinates: list[float] = Field(min_length=2, max_length=2)  # [lon, lat]
    hourly: list[HourlyPoint]


class ForecastMeta(BaseModel):
    domain: str
    bounding_box: str
    init_time: str
    forecast_horizon_hours: int
    coord_order: str
    note: str


class ForecastResponse(BaseModel):
    meta: ForecastMeta
    stations: list[Station]


# ---------- Compare ----------
class CompareRow(BaseModel):
    h: int = Field(ge=0, le=72)
    time: str
    aqi_coupled: int = Field(ge=0, le=500)
    aqi_uncoupled: int = Field(ge=0, le=500)
    difference: int


class CompareStation(BaseModel):
    station_id: str
    station_name: str
    rows: list[CompareRow]


class CompareResponse(BaseModel):
    stations: list[CompareStation]


# ---------- Inversion (still mock until Member 2 sends real data) ----------
class InversionReading(BaseModel):
    region: str
    inversion_strength: Literal["none", "weak", "moderate", "strong"]
    delta_t: float


# ---------- Plumes (still mock until Member 2 sends real data) ----------
class Plume(BaseModel):
    source: str
    frp: float = Field(ge=0)
    direction: str


class PlumesResponse(BaseModel):
    plumes: list[Plume]


# ---------- GRAP ----------
class GrapStatus(BaseModel):
    worst_current_aqi: int
    triggered_stage: str
    peak_72h_aqi: int
    peak_hour: int
    peak_stage: str
