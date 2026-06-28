"""
Chat schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class ChatMessage(BaseModel):
    """Single message in conversation history."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    conversation_history: Optional[List[ChatMessage]] = None


class QuickSuggestionRequest(BaseModel):
    """Request for quick suggestion."""
    suggestion_type: str = Field(..., description="today, casual, formal, date, sport, party")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    success: bool
    response: str
    error: Optional[str] = None