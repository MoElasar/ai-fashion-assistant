"""
Recommendation schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class RecommendationRequest(BaseModel):
    """Request for outfit recommendation."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    occasion: str = Field(default="casual", description="Occasion type")


class OutfitItem(BaseModel):
    """Single item in outfit."""
    id: int
    clothing_type: str
    image_path: str
    primary_color_hex: Optional[str] = None
    secondary_color_hex: Optional[str] = None
    attributes: List[str] = []


class ColorHarmony(BaseModel):
    """Color harmony analysis."""
    score: float
    harmony: str
    details: List[Dict[str, Any]] = []


class OutfitRecommendationResponse(BaseModel):
    """Response for outfit recommendation."""
    success: bool
    message: Optional[str] = None
    occasion: Optional[str] = None
    weather: Optional[Dict[str, Any]] = None
    outfit: Optional[Dict[str, OutfitItem]] = None
    color_harmony: Optional[ColorHarmony] = None
    missing_layers: List[str] = []
    complete: bool = False


class OccasionResponse(BaseModel):
    """Single occasion option."""
    id: str
    name: str
    description: str


class OccasionsListResponse(BaseModel):
    """List of available occasions."""
    occasions: List[OccasionResponse]