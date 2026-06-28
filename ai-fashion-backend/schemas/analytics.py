"""
Analytics schemas for request/response validation.
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ItemStats(BaseModel):
    """Statistics for a single clothing item."""
    id: int
    clothing_type: str
    layer_type: str
    image_path: str
    primary_color_hex: Optional[str] = None
    times_worn: int
    last_worn_date: Optional[date] = None


class OverviewStats(BaseModel):
    """Overview statistics for wardrobe."""
    total_items: int
    total_outfits: int
    total_times_worn: int
    items_by_layer: Dict[str, int]
    most_worn_item: Optional[ItemStats] = None
    least_worn_item: Optional[ItemStats] = None


class ColorDistribution(BaseModel):
    """Color distribution in wardrobe."""
    color_hex: str
    color_name: str
    count: int
    percentage: float


class AnalyticsOverviewResponse(BaseModel):
    """Full analytics overview response."""
    overview: OverviewStats
    color_distribution: List[ColorDistribution]


class ItemStatsResponse(BaseModel):
    """Response for single item stats."""
    item: ItemStats
    paired_with: List[ItemStats] = []
    usage_history: List[Dict[str, Any]] = []


class ItemListStatsResponse(BaseModel):
    """Response for list of item stats."""
    items: List[ItemStats]
    total: int