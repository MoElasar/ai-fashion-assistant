"""
Schedule Router
Manages weekly outfit scheduling.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional

from database import get_db
from models.user import User
from models.clothing_item import ClothingItem
from models.outfit import Outfit
from models.schedule import ScheduledOutfit
from models.usage_history import UsageHistory
from schemas.schedule import (
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
    ScheduledOutfitResponse,
    WeekScheduleResponse,
    WeekScheduleDay
)
from schemas.outfit import OutfitItemDetail
from schemas.auth import MessageResponse
from utils.auth import get_current_user
from services.weather_service import weather_service


router = APIRouter()


# =============================================================================
# HELPER FUNCTION
# =============================================================================

def get_scheduled_outfit_response(
    scheduled: ScheduledOutfit, 
    db: Session
) -> ScheduledOutfitResponse:
    """Convert scheduled outfit to response with details."""
    outfit = db.query(Outfit).filter(Outfit.id == scheduled.outfit_id).first()
    
    items = []
    if outfit:
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
    
    return ScheduledOutfitResponse(
        id=scheduled.id,
        user_id=scheduled.user_id,
        outfit_id=scheduled.outfit_id,
        scheduled_date=scheduled.scheduled_date,
        notes=scheduled.notes,
        is_worn=scheduled.is_worn,
        created_at=scheduled.created_at,
        outfit_name=outfit.name if outfit else None,
        outfit_items=items
    )


# =============================================================================
# GET WEEK SCHEDULE
# =============================================================================

@router.get("/week", response_model=WeekScheduleResponse)
async def get_week_schedule(
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scheduled outfits for the next 7 days.
    Includes weather forecast if coordinates provided.
    """
    today = date.today()
    end_date = today + timedelta(days=6)
    
    # Get forecast if coordinates provided
    forecast_data = None
    if latitude is not None and longitude is not None:
        forecast_data = await weather_service.get_forecast(latitude, longitude, 7)
    
    # Get all scheduled outfits for the week
    scheduled_outfits = db.query(ScheduledOutfit).filter(
        ScheduledOutfit.user_id == current_user.id,
        ScheduledOutfit.scheduled_date >= today,
        ScheduledOutfit.scheduled_date <= end_date
    ).all()
    
    # Create lookup by date
    schedule_by_date = {
        s.scheduled_date: s for s in scheduled_outfits
    }
    
    # Build week response
    week = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i in range(7):
        current_date = today + timedelta(days=i)
        day_name = day_names[current_date.weekday()]
        
        # Get weather for this day
        day_weather = None
        if forecast_data and forecast_data.get("forecast"):
            for forecast_day in forecast_data["forecast"]:
                if forecast_day["date"] == current_date.isoformat():
                    day_weather = forecast_day
                    break
        
        # Get scheduled outfit for this day
        scheduled = schedule_by_date.get(current_date)
        scheduled_response = None
        if scheduled:
            scheduled_response = get_scheduled_outfit_response(scheduled, db)
        
        week.append(WeekScheduleDay(
            date=current_date,
            day_name=day_name,
            is_today=(current_date == today),
            weather_forecast=day_weather,
            scheduled_outfit=scheduled_response
        ))
    
    return WeekScheduleResponse(
        week=week,
        start_date=today,
        end_date=end_date
    )


# =============================================================================
# SCHEDULE OUTFIT
# =============================================================================

@router.post("/", response_model=ScheduledOutfitResponse, status_code=status.HTTP_201_CREATED)
def schedule_outfit(
    request: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule an outfit for a specific date.
    Can only schedule up to 7 days in advance.
    """
    # Validate date is within range
    today = date.today()
    max_date = today + timedelta(days=7)
    
    if request.scheduled_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule outfits for past dates"
        )
    
    if request.scheduled_date > max_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule more than 7 days in advance"
        )
    
    # Verify outfit belongs to user
    outfit = db.query(Outfit).filter(
        Outfit.id == request.outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    # Check if date already has scheduled outfit
    existing = db.query(ScheduledOutfit).filter(
        ScheduledOutfit.user_id == current_user.id,
        ScheduledOutfit.scheduled_date == request.scheduled_date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An outfit is already scheduled for this date. Delete it first or update it."
        )
    
    # Create scheduled outfit
    scheduled = ScheduledOutfit(
        user_id=current_user.id,
        outfit_id=request.outfit_id,
        scheduled_date=request.scheduled_date,
        notes=request.notes
    )
    
    db.add(scheduled)
    db.commit()
    db.refresh(scheduled)
    
    return get_scheduled_outfit_response(scheduled, db)


# =============================================================================
# UPDATE SCHEDULED OUTFIT
# =============================================================================

@router.put("/{schedule_id}", response_model=ScheduledOutfitResponse)
def update_scheduled_outfit(
    schedule_id: int,
    request: ScheduleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a scheduled outfit's date or notes."""
    scheduled = db.query(ScheduledOutfit).filter(
        ScheduledOutfit.id == schedule_id,
        ScheduledOutfit.user_id == current_user.id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled outfit not found"
        )
    
    if request.scheduled_date is not None:
        # Validate new date
        today = date.today()
        max_date = today + timedelta(days=7)
        
        if request.scheduled_date < today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reschedule to past dates"
            )
        
        if request.scheduled_date > max_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot schedule more than 7 days in advance"
            )
        
        # Check for conflict
        existing = db.query(ScheduledOutfit).filter(
            ScheduledOutfit.user_id == current_user.id,
            ScheduledOutfit.scheduled_date == request.scheduled_date,
            ScheduledOutfit.id != schedule_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An outfit is already scheduled for this date"
            )
        
        scheduled.scheduled_date = request.scheduled_date
    
    if request.notes is not None:
        scheduled.notes = request.notes
    
    db.commit()
    db.refresh(scheduled)
    
    return get_scheduled_outfit_response(scheduled, db)


# =============================================================================
# DELETE SCHEDULED OUTFIT
# =============================================================================

@router.delete("/{schedule_id}", response_model=MessageResponse)
def delete_scheduled_outfit(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a scheduled outfit."""
    scheduled = db.query(ScheduledOutfit).filter(
        ScheduledOutfit.id == schedule_id,
        ScheduledOutfit.user_id == current_user.id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled outfit not found"
        )
    
    db.delete(scheduled)
    db.commit()
    
    return MessageResponse(
        message="Scheduled outfit removed",
        success=True
    )


# =============================================================================
# MARK SCHEDULED OUTFIT AS WORN
# =============================================================================

@router.post("/{schedule_id}/confirm-worn", response_model=MessageResponse)
def confirm_scheduled_worn(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm that a scheduled outfit was worn.
    Updates usage history for all items.
    """
    scheduled = db.query(ScheduledOutfit).filter(
        ScheduledOutfit.id == schedule_id,
        ScheduledOutfit.user_id == current_user.id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled outfit not found"
        )
    
    if scheduled.is_worn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Outfit already marked as worn"
        )
    
    # Get outfit and update all items
    outfit = db.query(Outfit).filter(Outfit.id == scheduled.outfit_id).first()
    
    if outfit:
        for outfit_item in outfit.items:
            clothing = db.query(ClothingItem).filter(
                ClothingItem.id == outfit_item.clothing_item_id
            ).first()
            
            if clothing:
                clothing.times_worn += 1
                clothing.last_worn_date = scheduled.scheduled_date
                
                # Create usage history
                usage = UsageHistory(
                    clothing_item_id=clothing.id,
                    outfit_id=outfit.id,
                    worn_date=scheduled.scheduled_date
                )
                db.add(usage)
    
    # Mark as worn
    scheduled.is_worn = True
    db.commit()
    
    return MessageResponse(
        message="Outfit marked as worn. Usage history updated.",
        success=True
    )