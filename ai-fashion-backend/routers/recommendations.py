"""
Recommendations Router
Generates outfit recommendations based on weather, occasion, and color rules.
Now supports multiple outfit options with detailed explanations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.user import User
from utils.auth import get_current_user
from services.weather_service import weather_service
from services.recommendation_engine import recommendation_engine


router = APIRouter()


# =============================================================================
# GENERATE OUTFIT RECOMMENDATION (Multiple Options)
# =============================================================================

@router.post("/generate")
async def generate_recommendation(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate outfit recommendations based on:
    - Current weather at given location
    - Selected occasion
    - Color harmony rules (Goldilocks Principle)
    
    Returns multiple outfit options (default 3) ranked by score.
    """
    latitude = request.get("latitude", 41.0082)
    longitude = request.get("longitude", 28.9784)
    occasion = request.get("occasion", "casual")
    num_options = request.get("num_options", 3)
    
    # Get current weather
    weather = await weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    # Generate outfits (multiple options)
    result = recommendation_engine.generate_outfit(
        db=db,
        user_id=current_user.id,
        weather_suggestions=weather["suggestions"],
        occasion=occasion,
        num_options=num_options
    )
    
    if not result["success"]:
        return {
            "success": False,
            "message": result.get("message", "Could not generate outfit"),
            "weather": weather,
            "outfit": None,
            "outfits": []
        }
    
    # Return both formats for compatibility
    best_outfit = result.get("best_outfit", {})
    
    return {
        "success": True,
        "occasion": result.get("occasion", occasion),
        "weather": weather,
        # Legacy format (single outfit - the best one)
        "outfit": best_outfit.get("outfit") if best_outfit else None,
        "color_harmony": best_outfit.get("color_harmony") if best_outfit else None,
        "explanation": best_outfit.get("explanation") if best_outfit else None,
        "missing_layers": best_outfit.get("missing_layers", []) if best_outfit else [],
        "complete": best_outfit.get("complete", False) if best_outfit else False,
        # New format (multiple outfits)
        "total_options": result.get("total_options", 1),
        "outfits": result.get("outfits", [])
    }


# =============================================================================
# GET AVAILABLE OCCASIONS
# =============================================================================

@router.get("/occasions")
def get_occasions(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available occasion types for recommendations.
    """
    occasions = recommendation_engine.get_occasions()
    
    return {
        "occasions": occasions
    }


# =============================================================================
# GET COLOR STRATEGIES
# =============================================================================

@router.get("/color-strategies")
def get_color_strategies(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of winning color strategies with explanations.
    """
    strategies = recommendation_engine.get_color_strategies()
    
    return {
        "strategies": strategies
    }


# =============================================================================
# GENERATE FOR SPECIFIC DATE (USING FORECAST)
# =============================================================================

@router.post("/generate-for-date")
async def generate_recommendation_for_date(
    request: dict,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate outfit recommendation for a future date using forecast.
    Used for outfit scheduling.
    """
    latitude = request.get("latitude", 41.0082)
    longitude = request.get("longitude", 28.9784)
    occasion = request.get("occasion", "casual")
    
    # Get forecast
    forecast_data = await weather_service.get_forecast(
        latitude,
        longitude,
        days=7
    )
    
    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch forecast data"
        )
    
    # Find the specific date in forecast
    day_forecast = None
    for day in forecast_data["forecast"]:
        if day["date"] == date:
            day_forecast = day
            break
    
    if not day_forecast:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date not found in forecast (must be within 7 days)"
        )
    
    # Generate outfit using forecast suggestions
    result = recommendation_engine.generate_outfit(
        db=db,
        user_id=current_user.id,
        weather_suggestions=day_forecast["suggestions"],
        occasion=occasion,
        num_options=1  # Single outfit for scheduling
    )
    
    if not result["success"]:
        return {
            "success": False,
            "message": result.get("message", "Could not generate outfit"),
            "weather": day_forecast,
            "outfit": None
        }
    
    best_outfit = result.get("best_outfit", {})
    
    return {
        "success": True,
        "occasion": result.get("occasion", occasion),
        "weather": day_forecast,
        "outfit": best_outfit.get("outfit") if best_outfit else None,
        "color_harmony": best_outfit.get("color_harmony") if best_outfit else None,
        "explanation": best_outfit.get("explanation") if best_outfit else None,
        "missing_layers": best_outfit.get("missing_layers", []) if best_outfit else [],
        "complete": best_outfit.get("complete", False) if best_outfit else False
    }


# =============================================================================
# GENERATE BY COLOR
# =============================================================================

@router.post("/generate-by-color")
async def generate_recommendation_by_color(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate outfit recommendation starting from a specific color.
    User specifies a color they want to wear.
    """
    latitude = request.get("latitude", 41.0082)
    longitude = request.get("longitude", 28.9784)
    occasion = request.get("occasion", "casual")
    base_color = request.get("base_color")
    
    if not base_color:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="base_color is required (hex format, e.g., '#FF5733')"
        )
    
    # Get current weather
    weather = await weather_service.get_current_weather(latitude, longitude)
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch weather data"
        )
    
    # Generate outfit by color
    result = recommendation_engine.generate_by_color(
        db=db,
        user_id=current_user.id,
        base_color_hex=base_color,
        weather_suggestions=weather["suggestions"],
        occasion=occasion
    )
    
    if not result["success"]:
        return {
            "success": False,
            "message": result.get("message", "Could not generate outfit"),
            "weather": weather,
            "outfit": None
        }
    
    return {
        "success": True,
        "occasion": result.get("occasion", occasion),
        "base_color": result.get("base_color"),
        "base_color_name": result.get("base_color_name"),
        "weather": weather,
        "outfit": result.get("outfit"),
        "color_harmony": result.get("color_harmony"),
        "explanation": result.get("explanation"),
        "colors_used": result.get("colors_used", []),
        "missing_layers": result.get("missing_layers", []),
        "complete": result.get("complete", False)
    }