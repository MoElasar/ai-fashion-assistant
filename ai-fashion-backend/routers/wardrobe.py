"""
Wardrobe Router
Handles clothing item management, image upload, and AI analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import json

from database import get_db
from models.user import User
from models.clothing_item import ClothingItem
from schemas.clothing import (
    ClothingItemResponse, 
    ClothingItemListResponse, 
    ClothingItemUpdate,
    ImageUploadResponse
)
from schemas.auth import MessageResponse
from utils.auth import get_current_user
from services.image_processing import image_processor
from services.color_extraction import color_extractor
from services.gemini_service import gemini_service


router = APIRouter()


# =============================================================================
# UPLOAD NEW CLOTHING ITEM
# =============================================================================

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_clothing_item(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new clothing item image.
    Automatically processes: background removal, color extraction, AI detection.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/heic", "image/heif"]
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]
    
    # Check by content type or file extension
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file.content_type not in allowed_types and file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # 1. Process image (save original + remove background)
    try:
        original_path, processed_path = image_processor.process_image(
            file_content, 
            file.filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )
    
    # 2. Extract colors using K-Means
    primary_color_hex = None
    secondary_color_hex = None
    try:
        primary_color_hex, secondary_color_hex = color_extractor.get_primary_and_secondary(
            processed_path
        )
    except Exception as e:
        print(f"Color extraction failed: {e}")
    
    # 3. Analyze with Gemini Vision
    clothing_type = "unknown"
    layer_type = "top"
    attributes = []
    confidence_score = None
    analysis_result = None
    
    try:
        analysis_result = gemini_service.analyze_clothing(processed_path)
        if analysis_result:
            clothing_type = analysis_result.get("clothing_type", "unknown")
            layer_type = analysis_result.get("layer_type", "top")
            attributes = analysis_result.get("attributes", [])
            confidence_score = analysis_result.get("confidence")
    except Exception as e:
        print(f"Gemini analysis failed: {e}")
    
    # 4. Create database record
    new_item = ClothingItem(
        user_id=current_user.id,
        image_path=processed_path,
        clothing_type=clothing_type,
        layer_type=layer_type,
        primary_color_hex=primary_color_hex,
        secondary_color_hex=secondary_color_hex,
        attributes=json.dumps(attributes) if attributes else None,
        confidence_score=confidence_score
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return ImageUploadResponse(
        message="Clothing item uploaded and analyzed successfully",
        clothing_item=ClothingItemResponse.model_validate(new_item),
        analysis=analysis_result
    )


# =============================================================================
# GET ALL CLOTHING ITEMS
# =============================================================================

@router.get("/items", response_model=ClothingItemListResponse)
def get_all_items(
    layer_type: Optional[str] = None,
    clothing_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all clothing items for the current user.
    Optional filters: layer_type, clothing_type
    """
    query = db.query(ClothingItem).filter(ClothingItem.user_id == current_user.id)
    
    if layer_type:
        query = query.filter(ClothingItem.layer_type == layer_type)
    
    if clothing_type:
        query = query.filter(ClothingItem.clothing_type.ilike(f"%{clothing_type}%"))
    
    items = query.order_by(ClothingItem.created_at.desc()).all()
    
    return ClothingItemListResponse(
        items=[ClothingItemResponse.model_validate(item) for item in items],
        total=len(items)
    )


# =============================================================================
# GET SINGLE CLOTHING ITEM
# =============================================================================

@router.get("/items/{item_id}", response_model=ClothingItemResponse)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific clothing item by ID."""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clothing item not found"
        )
    
    return ClothingItemResponse.model_validate(item)


# =============================================================================
# UPDATE CLOTHING ITEM
# =============================================================================

@router.put("/items/{item_id}", response_model=ClothingItemResponse)
def update_item(
    item_id: int,
    update_data: ClothingItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a clothing item's details."""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clothing item not found"
        )
    
    # Update fields if provided
    if update_data.clothing_type is not None:
        item.clothing_type = update_data.clothing_type
    if update_data.layer_type is not None:
        item.layer_type = update_data.layer_type
    if update_data.primary_color_hex is not None:
        item.primary_color_hex = update_data.primary_color_hex
    if update_data.secondary_color_hex is not None:
        item.secondary_color_hex = update_data.secondary_color_hex
    if update_data.attributes is not None:
        item.attributes = json.dumps(update_data.attributes)
    
    db.commit()
    db.refresh(item)
    
    return ClothingItemResponse.model_validate(item)


# =============================================================================
# DELETE CLOTHING ITEM
# =============================================================================

@router.delete("/items/{item_id}", response_model=MessageResponse)
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a clothing item and its image."""
    item = db.query(ClothingItem).filter(
        ClothingItem.id == item_id,
        ClothingItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clothing item not found"
        )
    
    # Delete image files
    try:
        image_processor.delete_images(item.image_path, item.image_path)
    except Exception as e:
        print(f"Failed to delete image files: {e}")
    
    # Delete from database
    db.delete(item)
    db.commit()
    
    return MessageResponse(
        message="Clothing item deleted successfully",
        success=True
    )


# =============================================================================
# GET ITEMS BY LAYER
# =============================================================================

@router.get("/layers/{layer_type}", response_model=ClothingItemListResponse)
def get_items_by_layer(
    layer_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all clothing items for a specific layer type."""
    valid_layers = ["top", "bottom", "outerwear", "footwear", "socks"]
    if layer_type not in valid_layers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid layer type. Must be one of: {', '.join(valid_layers)}"
        )
    
    items = db.query(ClothingItem).filter(
        ClothingItem.user_id == current_user.id,
        ClothingItem.layer_type == layer_type
    ).order_by(ClothingItem.created_at.desc()).all()
    
    return ClothingItemListResponse(
        items=[ClothingItemResponse.model_validate(item) for item in items],
        total=len(items)
    )