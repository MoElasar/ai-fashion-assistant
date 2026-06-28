"""
Chat Service
AI Fashion Assistant using Google Gemini LLM.
"""

import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import json
import math

from config import settings
from models.clothing_item import ClothingItem


# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


# =============================================================================
# COLOR NAME MAPPING
# =============================================================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    """Convert RGB to HSL."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0
    
    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        
        if max_c == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_c == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h /= 6.0
    
    return (h * 360, s * 100, l * 100)


def get_color_name(hex_color: str) -> str:
    """Convert hex color to a human-readable color name."""
    if not hex_color:
        return "unknown"
    
    try:
        r, g, b = hex_to_rgb(hex_color)
        h, s, l = rgb_to_hsl(r, g, b)
        
        # Check for achromatic colors first (black, white, gray)
        if s < 10:
            if l < 15:
                return "black"
            elif l < 35:
                return "charcoal gray"
            elif l < 55:
                return "gray"
            elif l < 75:
                return "light gray"
            elif l < 90:
                return "off-white"
            else:
                return "white"
        
        # Check for very light colors (pastels)
        if l > 80:
            if h < 15 or h >= 345:
                return "light pink"
            elif h < 45:
                return "peach"
            elif h < 70:
                return "cream"
            elif h < 150:
                return "mint"
            elif h < 200:
                return "light blue"
            elif h < 260:
                return "lavender"
            elif h < 310:
                return "light purple"
            else:
                return "light pink"
        
        # Check for very dark colors
        if l < 20:
            if h < 30 or h >= 330:
                return "dark red"
            elif h < 70:
                return "dark brown"
            elif h < 150:
                return "dark green"
            elif h < 260:
                return "navy blue"
            elif h < 310:
                return "dark purple"
            else:
                return "burgundy"
        
        # Main color categories
        if h < 15 or h >= 345:
            if s > 70 and l > 40:
                return "red"
            elif l < 40:
                return "maroon"
            else:
                return "coral"
        elif h < 30:
            if l > 60:
                return "orange"
            else:
                return "rust"
        elif h < 45:
            if s > 80:
                return "orange"
            else:
                return "tan"
        elif h < 65:
            if s > 70:
                return "yellow"
            elif l < 50:
                return "olive"
            else:
                return "mustard"
        elif h < 80:
            return "lime green"
        elif h < 150:
            if s > 60 and l > 35:
                return "green"
            elif l < 35:
                return "forest green"
            else:
                return "sage green"
        elif h < 180:
            return "teal"
        elif h < 200:
            return "cyan"
        elif h < 230:
            if s > 60 and l > 40:
                return "blue"
            elif l < 35:
                return "navy blue"
            else:
                return "sky blue"
        elif h < 260:
            return "indigo"
        elif h < 290:
            if s > 60:
                return "purple"
            else:
                return "violet"
        elif h < 310:
            return "magenta"
        elif h < 330:
            if s > 50:
                return "pink"
            else:
                return "mauve"
        else:
            return "red"
            
    except Exception:
        return "unknown"


class ChatService:
    """
    AI Fashion Assistant powered by Gemini LLM.
    Provides personalized fashion advice based on user's wardrobe.
    """
    
    def __init__(self):
        """Initialize the Gemini model for chat."""
        self.model = None
        self.initialized = False
        
        if settings.gemini_api_key:
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.initialized = True
                print("✓ Chat model initialized successfully")
            except Exception as e:
                print(f"✗ Failed to initialize chat model: {e}")
    
    def _get_wardrobe_context(self, db: Session, user_id: int) -> str:
        """Build wardrobe context string for the AI."""
        items = db.query(ClothingItem).filter(
            ClothingItem.user_id == user_id
        ).all()
        
        if not items:
            return "The user's wardrobe is empty. They haven't added any clothing items yet."
        
        wardrobe_text = f"User's wardrobe contains {len(items)} items:\n"
        
        # Group by layer type
        layers = {}
        for item in items:
            layer = item.layer_type
            if layer not in layers:
                layers[layer] = []
            
            # Parse attributes
            attributes = []
            if item.attributes:
                try:
                    attributes = json.loads(item.attributes)
                except:
                    pass
            
            # Convert hex to color name
            color_name = get_color_name(item.primary_color_hex) if item.primary_color_hex else "unknown color"
            secondary_color = get_color_name(item.secondary_color_hex) if item.secondary_color_hex else None
            
            # Build item description
            item_desc = f"  • {item.clothing_type.title()}"
            
            # Add color info
            if secondary_color and secondary_color != "unknown":
                item_desc += f" ({color_name} with {secondary_color} accents)"
            else:
                item_desc += f" ({color_name})"
            
            # Add attributes
            if attributes:
                attr_str = ", ".join(attributes[:3])
                item_desc += f" - {attr_str}"
            
            # Add wear count
            if item.times_worn > 0:
                item_desc += f" [worn {item.times_worn}x]"
            else:
                item_desc += " [never worn]"
            
            layers[layer].append(item_desc)
        
        # Format output
        layer_order = ["top", "bottom", "outerwear", "footwear", "socks"]
        for layer in layer_order:
            if layer in layers:
                wardrobe_text += f"\n{layer.upper()}S ({len(layers[layer])} items):\n"
                wardrobe_text += "\n".join(layers[layer])
        
        return wardrobe_text
    
    def _format_weather_info(self, weather_info: Dict) -> str:
        """Format weather info for the prompt."""
        if not weather_info:
            return ""
        
        temp = weather_info.get('temperature', 'N/A')
        condition = weather_info.get('condition', 'unknown').replace('_', ' ')
        humidity = weather_info.get('humidity', 'N/A')
        
        # Get weather suggestions
        suggestions = weather_info.get('suggestions', {})
        needs_outerwear = suggestions.get('needs_outerwear', False)
        outerwear_type = suggestions.get('outerwear_type', 'jacket')
        light_clothing = suggestions.get('light_clothing', False)
        
        weather_text = f"""
Current Weather:
  • Temperature: {temp}°C
  • Conditions: {condition}
  • Humidity: {humidity}%
"""
        
        if needs_outerwear:
            weather_text += f"  • Recommendation: Bring a {outerwear_type}\n"
        elif light_clothing:
            weather_text += "  • Recommendation: Light, breathable clothing\n"
        
        return weather_text
    
    def _build_system_prompt(
        self,
        wardrobe_context: str,
        weather_info: Optional[Dict] = None
    ) -> str:
        """Build the system prompt with context."""
        prompt = f"""You are Style, a friendly AI Fashion Assistant. Be warm, helpful, and specific.

{wardrobe_context}
"""

        if weather_info:
            prompt += self._format_weather_info(weather_info)

        prompt += """
When suggesting outfits:
- Be specific with items from their wardrobe
- Explain why colors/styles work together
- Use color names (not hex codes)
- Keep responses complete and concise
"""

        return prompt
    
    def chat(
        self,
        db: Session,
        user_id: int,
        message: str,
        weather_info: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the AI fashion assistant.
        """
        if not self.initialized:
            return {
                "success": False,
                "response": "I'm having trouble connecting right now. Please check if the API is configured correctly.",
                "error": "Model not initialized"
            }
        
        try:
            # Build context
            wardrobe_context = self._get_wardrobe_context(db, user_id)
            system_prompt = self._build_system_prompt(wardrobe_context, weather_info)
            
            # Build conversation
            messages = [system_prompt]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = "User" if msg.get("role") == "user" else "Style"
                    messages.append(f"{role}: {msg.get('content', '')}")
            
            # Add current message
            messages.append(f"User: {message}")
            messages.append("Style:")
            
            full_prompt = "\n\n".join(messages)
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_output_tokens": 2048,  # Increased for longer responses
                }
            )

            # Get the response text
            response_text = response.text.strip() if response.text else ""

            # Log for debugging
            print(f"Chat response length: {len(response_text)} chars")

            return {
                "success": True,
                "response": response_text,
                "error": None
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Chat error: {error_msg}")
            
            # Handle quota errors gracefully
            if "429" in error_msg or "quota" in error_msg.lower():
                return {
                    "success": False,
                    "response": "I'm taking a quick break! 😅 The style service is a bit busy right now. Please try again in a minute.",
                    "error": "Rate limit exceeded"
                }
            
            return {
                "success": False,
                "response": "Oops! I had a little fashion malfunction. 👗 Please try again!",
                "error": error_msg
            }
    
    def get_quick_suggestion(
        self,
        db: Session,
        user_id: int,
        suggestion_type: str,
        weather_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get a quick outfit suggestion based on type.
        """
        prompts = {
            "today": "What should I wear today? Please consider the current weather and suggest a complete outfit from my wardrobe.",
            "casual": "I want a relaxed, casual outfit for just hanging out. What do you suggest from my wardrobe?",
            "formal": "I need to dress professionally for an important meeting. What's the best formal outfit I can put together?",
            "date": "I have a date tonight! Help me pick something attractive and stylish from my wardrobe.",
            "sport": "I'm going to work out. What athletic or sporty outfit should I wear?",
            "party": "I'm going to a party tonight! What's the most stylish outfit I can wear?"
        }
        
        message = prompts.get(suggestion_type, prompts["today"])
        
        return self.chat(
            db=db,
            user_id=user_id,
            message=message,
            weather_info=weather_info
        )


# Global instance
chat_service = ChatService()