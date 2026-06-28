# Models package
# Import all models here for easy access and to ensure they are registered with Base

from database import Base

from models.user import User
from models.clothing_item import ClothingItem
from models.outfit import Outfit, OutfitItem
from models.schedule import ScheduledOutfit
from models.usage_history import UsageHistory
from models.user_preferences import UserPreferences

__all__ = [
    "Base",
    "User",
    "ClothingItem",
    "Outfit",
    "OutfitItem",
    "ScheduledOutfit",
    "UsageHistory",
    "UserPreferences",
]