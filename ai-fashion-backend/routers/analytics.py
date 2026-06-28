"""
Analytics Router
Provides wardrobe usage statistics and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from collections import Counter

from database import get_db
from models.user import User
from models.clothing_item import ClothingItem
from models.outfit import Outfit, OutfitItem
from models.usage_history import UsageHistory
from schemas.analytics import (
    ItemStats,
    OverviewStats,
    ColorDistribution,
    AnalyticsOverviewResponse,
    ItemStatsResponse,
    ItemListStatsResponse
)
from utils.auth import get_current_user
from services.color_extraction import FASHION_COLORS

import numpy as np


router = APIRouter()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def item_to_stats(item: ClothingItem) -> ItemStats:
    """Convert clothing item to stats object."""
    return ItemStats(
        id=item.id,
        clothing_type=item.clothing_type,
        layer_type=item.layer_type,
        image_path=item.image_path,
        primary_color_hex=item.primary_color_hex,
        times_worn=item.times_worn,
        last_worn_date=item.last_worn_date
    )


def get_color_name(hex_color: str) -> str:
    """Get closest fashion color name for hex value."""
    if not hex_color:
        return "unknown"
    
    try:
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        color_names = list(FASHION_COLORS.keys())
        color_values = np.array(list(FASHION_COLORS.values()))
        
        rgb_array = np.array(rgb)
        distances = np.sqrt(np.sum((color_values - rgb_array) ** 2, axis=1))
        closest_idx = np.argmin(distances)
        
        return color_names[closest_idx]
    except:
        return "unknown"


# =============================================================================
# GET OVERVIEW STATISTICS
# =============================================================================

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete wardrobe analytics overview.
    Includes item counts, usage stats, and color distribution.
    """
    # Get all user's items
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id
    ).all()
    
    # Get outfit count
    outfit_count = db.query(Outfit).filter(
        Outfit.user_id == current_user.id
    ).count()
    
    # Calculate stats
    total_items = len(items)
    total_times_worn = sum(item.times_worn for item in items)
    
    # Items by layer
    items_by_layer: Dict[str, int] = {}
    for item in items:
        layer = item.layer_type
        items_by_layer[layer] = items_by_layer.get(layer, 0) + 1
    
    # Most/least worn items
    most_worn = None
    least_worn = None
    
    if items:
        worn_items = [item for item in items if item.times_worn > 0]
        if worn_items:
            most_worn_item = max(worn_items, key=lambda x: x.times_worn)
            most_worn = item_to_stats(most_worn_item)
            least_worn_item = min(worn_items, key=lambda x: x.times_worn)
            least_worn = item_to_stats(least_worn_item)
    
    # Color distribution
    color_counts: Dict[str, Dict] = {}
    for item in items:
        if item.primary_color_hex:
            hex_color = item.primary_color_hex
            color_name = get_color_name(hex_color)
            
            if color_name not in color_counts:
                color_counts[color_name] = {
                    "hex": hex_color,
                    "count": 0
                }
            color_counts[color_name]["count"] += 1
    
    color_distribution = []
    for name, data in sorted(color_counts.items(), key=lambda x: x[1]["count"], reverse=True):
        percentage = (data["count"] / total_items * 100) if total_items > 0 else 0
        color_distribution.append(ColorDistribution(
            color_hex=data["hex"],
            color_name=name,
            count=data["count"],
            percentage=round(percentage, 1)
        ))
    
    return AnalyticsOverviewResponse(
        overview=OverviewStats(
            total_items=total_items,
            total_outfits=outfit_count,
            total_times_worn=total_times_worn,
            items_by_layer=items_by_layer,
            most_worn_item=most_worn,
            least_worn_item=least_worn
        ),
        color_distribution=color_distribution
    )


# =============================================================================
# GET MOST WORN ITEMS
# =============================================================================

@router.get("/most-worn", response_model=ItemListStatsResponse)
def get_most_worn(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get most frequently worn items."""
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id,
        ClothingItem.times_worn > 0
    ).order_by(ClothingItem.times_worn.desc()).limit(limit).all()
    
    return ItemListStatsResponse(
        items=[item_to_stats(item) for item in items],
        total=len(items)
    )


# =============================================================================
# GET LEAST WORN ITEMS
# =============================================================================

@router.get("/least-worn", response_model=ItemListStatsResponse)
def get_least_worn(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get least frequently worn items (excluding never worn)."""
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id,
        ClothingItem.times_worn > 0
    ).order_by(ClothingItem.times_worn.asc()).limit(limit).all()
    
    return ItemListStatsResponse(
        items=[item_to_stats(item) for item in items],
        total=len(items)
    )


# =============================================================================
# GET NEVER WORN ITEMS
# =============================================================================

@router.get("/never-worn", response_model=ItemListStatsResponse)
def get_never_worn(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items that have never been worn."""
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id,
        ClothingItem.times_worn == 0
    ).order_by(ClothingItem.created_at.desc()).all()
    
    return ItemListStatsResponse(
        items=[item_to_stats(item) for item in items],
        total=len(items)
    )


# =============================================================================
# GET SINGLE ITEM STATISTICS
# =============================================================================

@router.get("/items/{item_id}/stats", response_model=ItemStatsResponse)
def get_item_stats(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a single item."""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clothing item not found"
        )
    
    # Get usage history
    usage_records = db.query(UsageHistory).filter(
        UsageHistory.clothing_item_id == item_id
    ).order_by(UsageHistory.worn_date.desc()).limit(10).all()
    
    usage_history = [
        {
            "date": record.worn_date.isoformat(),
            "outfit_id": record.outfit_id
        }
        for record in usage_records
    ]
    
    # Get frequently paired items
    paired_item_ids = []
    for record in usage_records:
        if record.outfit_id:
            # Get other items in the same outfit
            outfit_items = db.query(OutfitItem).filter(
                OutfitItem.outfit_id == record.outfit_id,
                OutfitItem.clothing_item_id != item_id
            ).all()
            paired_item_ids.extend([oi.clothing_item_id for oi in outfit_items])
    
    # Count paired items
    paired_counts = Counter(paired_item_ids)
    top_paired_ids = [item_id for item_id, count in paired_counts.most_common(5)]
    
    paired_items = []
    for paired_id in top_paired_ids:
        paired_item = db.query(ClothingItem).filter(
            ClothingItem.id == paired_id
        ).first()
        if paired_item:
            paired_items.append(item_to_stats(paired_item))
    
    return ItemStatsResponse(
        item=item_to_stats(item),
        paired_with=paired_items,
        usage_history=usage_history
    )


# =============================================================================
# GET COLOR DISTRIBUTION
# =============================================================================

@router.get("/color-distribution", response_model=list[ColorDistribution])
def get_color_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get color distribution of wardrobe."""
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id
    ).all()
    
    total_items = len(items)
    if total_items == 0:
        return []
    
    color_counts: Dict[str, Dict] = {}
    for item in items:
        if item.primary_color_hex:
            hex_color = item.primary_color_hex
            color_name = get_color_name(hex_color)
            
            if color_name not in color_counts:
                color_counts[color_name] = {
                    "hex": hex_color,
                    "count": 0
                }
            color_counts[color_name]["count"] += 1
    
    distribution = []
    for name, data in sorted(color_counts.items(), key=lambda x: x[1]["count"], reverse=True):
        percentage = (data["count"] / total_items * 100)
        distribution.append(ColorDistribution(
            color_hex=data["hex"],
            color_name=name,
            count=data["count"],
            percentage=round(percentage, 1)
        ))
    
    return distribution