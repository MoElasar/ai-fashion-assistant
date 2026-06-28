"""
Weather Router
Provides weather data for outfit recommendations and scheduling.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from models.user import User
from schemas.weather import CurrentWeatherResponse, ForecastResponse
from utils.auth import get_current_user
from services.weather_service import weather_service


router = APIRouter()


# =============================================================================
# GET CURRENT WEATHER
# =============================================================================

@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    current_user: User = Depends(get_current_user)
):
    """
    Get current weather for given coordinates.
    Results are cached for 30 minutes.
    """
    weather = await weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    return weather


# =============================================================================
# GET WEATHER FORECAST
# =============================================================================

@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days"),
    current_user: User = Depends(get_current_user)
):
    """
    Get weather forecast for up to 7 days.
    Results are cached for 2 hours.
    Used for outfit scheduling.
    """
    forecast = await weather_service.get_forecast(latitude, longitude, days)
    
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch forecast data"
        )
    
    return forecast