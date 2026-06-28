"""
Chat Router
AI Fashion Assistant conversation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.user import User
from schemas.chat import ChatRequest, ChatResponse, QuickSuggestionRequest
from utils.auth import get_current_user
from services.chat_service import chat_service
from services.weather_service import weather_service


router = APIRouter()


# =============================================================================
# CHAT MESSAGE
# =============================================================================

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI Fashion Assistant.
    
    The assistant knows your wardrobe and can:
    - Suggest outfits based on weather, occasion, or style
    - Answer fashion questions
    - Help you style specific items
    - Give advice on what to wear
    
    Optionally provide coordinates for weather-aware suggestions.
    """
    # Get weather if coordinates provided
    weather_info = None
    if request.latitude is not None and request.longitude is not None:
        weather_info = await weather_service.get_current_weather(
            request.latitude,
            request.longitude
        )
    
    # Convert conversation history
    history = None
    if request.conversation_history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
    
    # Get response from chat service
    result = chat_service.chat(
        db=db,
        user_id=current_user.id,
        message=request.message,
        weather_info=weather_info,
        conversation_history=history
    )
    
    return ChatResponse(**result)


# =============================================================================
# QUICK SUGGESTION
# =============================================================================

@router.post("/quick-suggestion", response_model=ChatResponse)
async def get_quick_suggestion(
    request: QuickSuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a quick outfit suggestion.
    
    Available types:
    - **today**: Based on current weather
    - **casual**: Casual hangout outfit
    - **formal**: Formal/business outfit
    - **date**: Date night outfit
    - **sport**: Athletic/exercise outfit
    - **party**: Party/night out outfit
    """
    valid_types = ["today", "casual", "formal", "date", "sport", "party"]
    
    if request.suggestion_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid suggestion type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Get weather if coordinates provided
    weather_info = None
    if request.latitude is not None and request.longitude is not None:
        weather_info = await weather_service.get_current_weather(
            request.latitude,
            request.longitude
        )
    
    result = chat_service.get_quick_suggestion(
        db=db,
        user_id=current_user.id,
        suggestion_type=request.suggestion_type,
        weather_info=weather_info
    )
    
    return ChatResponse(**result)


# =============================================================================
# GET SUGGESTION TYPES
# =============================================================================

@router.get("/suggestion-types")
def get_suggestion_types():
    """Get available quick suggestion types."""
    return {
        "types": [
            {"id": "today", "name": "Today's Outfit", "description": "Based on current weather"},
            {"id": "casual", "name": "Casual", "description": "Relaxed everyday wear"},
            {"id": "formal", "name": "Formal", "description": "Business or formal events"},
            {"id": "date", "name": "Date Night", "description": "Romantic occasions"},
            {"id": "sport", "name": "Sport", "description": "Exercise or athletic activities"},
            {"id": "party", "name": "Party", "description": "Night out or celebrations"}
        ]
    }