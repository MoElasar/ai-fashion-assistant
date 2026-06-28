"""
Clothing item schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class ClothingItemUpdate(BaseModel):
    """Schema for updating a clothing item."""
    clothing_type: Optional[str] = None
    layer_type: Optional[str] = None
    primary_color_hex: Optional[str] = None
    secondary_color_hex: Optional[str] = None
    attributes: Optional[List[str]] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ClothingItemResponse(BaseModel):
    """Schema for clothing item in responses."""
    id: int
    user_id: int
    image_path: str
    clothing_type: str
    layer_type: str
    primary_color_hex: Optional[str] = None
    secondary_color_hex: Optional[str] = None
    attributes: Optional[str] = None  # JSON string
    confidence_score: Optional[float] = None
    times_worn: int = 0
    last_worn_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClothingItemListResponse(BaseModel):
    """Schema for list of clothing items."""
    items: List[ClothingItemResponse]
    total: int


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""
    message: str
    clothing_item: ClothingItemResponse
    analysis: Optional[dict] = None


class ColorAnalysisResponse(BaseModel):
    """Schema for color analysis response."""
    primary_color: dict
    secondary_color: Optional[dict] = None
    all_colors: List[dict]