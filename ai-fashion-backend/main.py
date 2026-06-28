from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from config import settings
import os

# Import all models to register them with Base
from models import User, ClothingItem, Outfit, OutfitItem, ScheduledOutfit, UsageHistory, UserPreferences

# Import routers
from routers import auth
from routers import wardrobe
from routers import weather
from routers import recommendations
from routers import outfits
from routers import schedule
from routers import analytics
from routers import chat

# Create upload directories if they don't exist
os.makedirs("uploads/original", exist_ok=True)
os.makedirs("uploads/processed", exist_ok=True)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Fashion API",
    description="AI-powered wardrobe management and outfit recommendation system",
    version="1.0.0"
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads folder for serving images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(wardrobe.router, prefix="/api/wardrobe", tags=["Wardrobe"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(outfits.router, prefix="/api/outfits", tags=["Outfits"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI-Fashion API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)