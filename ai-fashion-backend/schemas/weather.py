"""
Weather schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class WeatherRequest(BaseModel):
    """Request with coordinates for weather."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ClothingSuggestions(BaseModel):
    """Clothing suggestions based on weather."""
    needs_outerwear: bool
    needs_warm_outerwear: bool
    needs_rain_protection: bool
    light_clothing: bool
    warm_clothing: bool
    recommended_layers: List[str]
    outerwear_type: Optional[str] = None


class CurrentWeatherResponse(BaseModel):
    """Response for current weather."""
    temperature: float
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    condition: str
    suggestions: Dict[str, Any]
    fetched_at: str


class DayForecast(BaseModel):
    """Single day forecast."""
    date: str
    temp_max: float
    temp_min: float
    temp_avg: float
    condition: str
    precipitation_probability: Optional[int] = None
    suggestions: Dict[str, Any]


class ForecastResponse(BaseModel):
    """Response for weather forecast."""
    forecast: List[DayForecast]
    fetched_at: str