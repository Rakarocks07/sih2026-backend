from pydantic import BaseModel, Field

class StationForecast(BaseModel):
    station_name: str
    hour: int = Field(ge=0, le=72)             # must be between 0 and 72
    pm25: float = Field(ge=0)                  # can't be negative
    coupled_aqi: int = Field(ge=0, le=500)     # AQI scale is 0 to 500
    uncoupled_aqi: int = Field(ge=0, le=500)

class ForecastResponse(BaseModel):
    stations: list[StationForecast]

class GrapStatus(BaseModel):
    worst_current_aqi: int
    triggered_stage: str