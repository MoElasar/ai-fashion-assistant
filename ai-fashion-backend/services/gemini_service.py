"""
Gemini Vision Service
Uses Google Gemini to detect clothing type, attributes, and confidence.
"""

import google.generativeai as genai
from PIL import Image
from typing import Dict, Any, Optional
import json
import re
import time

from config import settings


# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


# =============================================================================
# CLOTHING ANALYSIS PROMPT
# =============================================================================

CLOTHING_ANALYSIS_PROMPT = """Analyze this clothing image. Return ONLY this JSON format:
{"clothing_type":"type","layer_type":"top","attributes":["attr1","attr2"],"confidence":0.9}

layer_type must be: top, bottom, outerwear, footwear, or socks
Return ONLY the JSON, no markdown, no explanation."""


class GeminiService:
    """
    Uses Google Gemini Vision to analyze clothing images
    and extract type, attributes, and confidence score.
    """
    
    def __init__(self):
        """Initialize the Gemini model."""
        self.model = None
        self.initialized = False
        
        if settings.gemini_api_key:
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.initialized = True
                print("✓ Gemini model initialized successfully")
            except Exception as e:
                print(f"✗ Failed to initialize Gemini model: {e}")
    
    def _clean_json_response(self, text: str) -> str:
        """Clean up Gemini response to extract valid JSON."""
        text = text.strip()

        # Remove markdown code blocks - handle various formats
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        # Find JSON object boundaries
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]

        return text
    
    def _parse_json_safely(self, text: str) -> Optional[Dict[str, Any]]:
        """Try multiple methods to parse JSON."""
        # First clean the text
        cleaned = self._clean_json_response(text)
        print(f"Cleaned JSON: {cleaned}")

        # Method 1: Direct parse of cleaned text
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")

        # Method 2: Try to fix common issues
        try:
            # Fix trailing commas
            fixed = re.sub(r',\s*}', '}', cleaned)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
        except:
            pass

        # Method 3: Extract with regex as last resort
        try:
            clothing_match = re.search(r'"clothing_type"\s*:\s*"([^"]+)"', text)
            layer_match = re.search(r'"layer_type"\s*:\s*"([^"]+)"', text)

            if clothing_match:
                layer = layer_match.group(1) if layer_match else "top"
                return {
                    "clothing_type": clothing_match.group(1),
                    "layer_type": layer,
                    "attributes": [],
                    "confidence": 0.8
                }
        except:
            pass

        return None
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix the result."""
        # Ensure required fields exist
        if "clothing_type" not in result or not result["clothing_type"]:
            result["clothing_type"] = "unknown"
        
        # Validate layer_type
        valid_layers = ["top", "bottom", "outerwear", "footwear", "socks"]
        if result.get("layer_type") not in valid_layers:
            # Try to infer from clothing_type
            clothing = result.get("clothing_type", "").lower()
            
            if any(x in clothing for x in ["shirt", "t-shirt", "tee", "polo", "blouse", "top", "sweater", "hoodie", "tank"]):
                result["layer_type"] = "top"
            elif any(x in clothing for x in ["pants", "jeans", "shorts", "skirt", "trousers", "leggings"]):
                result["layer_type"] = "bottom"
            elif any(x in clothing for x in ["jacket", "coat", "blazer", "cardigan", "vest", "parka"]):
                result["layer_type"] = "outerwear"
            elif any(x in clothing for x in ["shoe", "sneaker", "boot", "sandal", "loafer", "heel", "slipper"]):
                result["layer_type"] = "footwear"
            elif any(x in clothing for x in ["sock", "socks"]):
                result["layer_type"] = "socks"
            else:
                result["layer_type"] = "top"  # Default
        
        # Ensure attributes is a list
        if "attributes" not in result:
            result["attributes"] = []
        elif isinstance(result["attributes"], str):
            result["attributes"] = [result["attributes"]]
        
        # Ensure confidence is valid
        if "confidence" not in result:
            result["confidence"] = 0.8
        else:
            try:
                result["confidence"] = float(result["confidence"])
                result["confidence"] = max(0.0, min(1.0, result["confidence"]))
            except:
                result["confidence"] = 0.8
        
        return result
    
    def analyze_clothing(self, image_path: str, max_retries: int = 2) -> Optional[Dict[str, Any]]:
        """
        Analyze a clothing image and extract attributes.
        
        Args:
            image_path: Path to the clothing image
            max_retries: Number of retries on failure
            
        Returns:
            Dictionary with clothing_type, layer_type, attributes, confidence
            or None if failed
        """
        if not self.initialized:
            print("Gemini model not initialized - check API key")
            return self._get_fallback_result()
        
        for attempt in range(max_retries + 1):
            try:
                # Load image
                image = Image.open(image_path)
                
                # Generate content with image
                response = self.model.generate_content(
                    [CLOTHING_ANALYSIS_PROMPT, image],
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "max_output_tokens": 1024,  # Increased
                    }
                )
                
                # Extract response text
                response_text = response.text.strip()
                print(f"Gemini raw response: {response_text}")
                
                # Parse JSON
                result = self._parse_json_safely(response_text)
                
                if result:
                    result = self._validate_result(result)
                    print(f"✓ Detected: {result['clothing_type']} ({result['layer_type']})")
                    return result
                else:
                    print(f"Failed to parse response on attempt {attempt + 1}")
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Error on attempt {attempt + 1}: {error_msg}")
                
                # Check for quota/rate limit errors
                if "429" in error_msg or "quota" in error_msg.lower():
                    print("Rate limited - waiting before retry...")
                    time.sleep(2)
                elif "403" in error_msg or "leaked" in error_msg.lower():
                    print("API key issue - please check your key")
                    return self._get_fallback_result()
            
            # Wait before retry
            if attempt < max_retries:
                time.sleep(1)
        
        # All retries failed - return fallback
        print("All attempts failed - returning fallback result")
        return self._get_fallback_result()
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Return a fallback result when detection fails."""
        return {
            "clothing_type": "unknown",
            "layer_type": "top",
            "attributes": [],
            "confidence": 0.0
        }


# Global instance
gemini_service = GeminiService()