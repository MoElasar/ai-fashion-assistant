"""
Outfits Router
Manages saved outfit combinations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models.user import User
from models.clothing_item import ClothingItem
from models.outfit import Outfit, OutfitItem
from models.usage_history import UsageHistory
from schemas.outfit import (
    OutfitCreateRequest,
    OutfitUpdateRequest,
    OutfitResponse,
    OutfitListResponse,
    OutfitItemDetail
)
from schemas.auth import MessageResponse
from utils.auth import get_current_user


router = APIRouter()


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def get_outfit_with_items(outfit: Outfit, db: Session) -> OutfitResponse:
    """Convert outfit model to response with item details."""
    items = []
    for outfit_item in outfit.items:
        clothing = db.query(ClothingItem).filter(
            ClothingItem.id == outfit_item.clothing_item_id
        ).first()
        if clothing:
            items.append(OutfitItemDetail(
                id=clothing.id,
                clothing_type=clothing.clothing_type,
                layer_type=clothing.layer_type,
                image_path=clothing.image_path,
                primary_color_hex=clothing.primary_color_hex
            ))
    
    return OutfitResponse(
        id=outfit.id,
        user_id=outfit.user_id,
        name=outfit.name,
        occasion=outfit.occasion,
        created_at=outfit.created_at,
        items=items
    )


# =============================================================================
# CREATE OUTFIT
# =============================================================================

@router.post("/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
def create_outfit(
    request: OutfitCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new outfit from selected clothing items.
    """
    # Verify all items belong to user
    for item_id in request.item_ids:
        item = db.query(ClothingItem).filter(
            ClothingItem.id == item_id,
            ClothingItem.user_id == current_user.id
        ).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clothing item {item_id} not found"
            )
    
    # Create outfit
    new_outfit = Outfit(
        user_id=current_user.id,
        name=request.name,
        occasion=request.occasion
    )
    db.add(new_outfit)
    db.flush()  # Get the outfit ID
    
    # Add outfit items
    for item_id in request.item_ids:
        outfit_item = OutfitItem(
            outfit_id=new_outfit.id,
            clothing_item_id=item_id
        )
        db.add(outfit_item)
    
    db.commit()
    db.refresh(new_outfit)
    
    return get_outfit_with_items(new_outfit, db)


# =============================================================================
# GET ALL OUTFITS
# =============================================================================

@router.get("/", response_model=OutfitListResponse)
def get_all_outfits(
    occasion: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved outfits for current user.
    Optional filter by occasion.
    """
    query = db.query(Outfit).filter(Outfit.user_id == current_user.id)
    
    if occasion:
        query = query.filter(Outfit.occasion == occasion)
    
    outfits = query.order_by(Outfit.created_at.desc()).all()
    
    return OutfitListResponse(
        outfits=[get_outfit_with_items(outfit, db) for outfit in outfits],
        total=len(outfits)
    )


# =============================================================================
# GET SINGLE OUTFIT
# =============================================================================

@router.get("/{outfit_id}", response_model=OutfitResponse)
def get_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific outfit by ID."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    return get_outfit_with_items(outfit, db)


# =============================================================================
# UPDATE OUTFIT
# =============================================================================

@router.put("/{outfit_id}", response_model=OutfitResponse)
def update_outfit(
    outfit_id: int,
    request: OutfitUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update outfit name or occasion."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    if request.name is not None:
        outfit.name = request.name
    if request.occasion is not None:
        outfit.occasion = request.occasion
    
    db.commit()
    db.refresh(outfit)
    
    return get_outfit_with_items(outfit, db)


# =============================================================================
# DELETE OUTFIT
# =============================================================================

@router.delete("/{outfit_id}", response_model=MessageResponse)
def delete_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an outfit."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    db.delete(outfit)
    db.commit()
    
    return MessageResponse(
        message="Outfit deleted successfully",
        success=True
    )


# =============================================================================
# MARK OUTFIT AS WORN
# =============================================================================

@router.post("/{outfit_id}/wear", response_model=MessageResponse)
def mark_outfit_worn(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark outfit as worn today.
    Updates usage history for all items in the outfit.
    """
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    today = date.today()
    
    # Update each clothing item in the outfit
    for outfit_item in outfit.items:
        clothing = db.query(ClothingItem).filter(
            ClothingItem.id == outfit_item.clothing_item_id
        ).first()
        
        if clothing:
            # Update clothing item stats
            clothing.times_worn += 1
            clothing.last_worn_date = today
            
            # Create usage history entry
            usage = UsageHistory(
                clothing_item_id=clothing.id,
                outfit_id=outfit.id,
                worn_date=today
            )
            db.add(usage)
    
    db.commit()
    
    return MessageResponse(
        message=f"Outfit marked as worn. Updated {len(outfit.items)} items.",
        success=True
    )