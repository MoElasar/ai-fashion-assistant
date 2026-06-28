"""
Recommendation Engine
Research-backed outfit recommendations using the Goldilocks Principle.

References:
- Gray et al. (2014) "The Science of Style" - PLOS ONE
- Li et al. (2025) "Colour harmony evaluation" - Fashion and Textiles

Key Insight: Maximum fashionableness is achieved with MODERATE color coordination.
- Too similar ("matchy-matchy") = unfashionable
- Too different ("clashing") = unfashionable
- Moderate coordination = OPTIMAL
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import json
import random

from models.clothing_item import ClothingItem
from services.color_matching import color_matcher


# =============================================================================
# COLOR NAME MAPPING (for explanations)
# =============================================================================

def get_color_name(hex_color: str) -> str:
    """Convert hex color to human-readable name."""
    if not hex_color:
        return "unknown"
    
    hex_color = hex_color.lstrip('#').lower()
    
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except:
        return "unknown"
    
    # Convert to HSL for better classification
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2 / 255
    
    if max_c == min_c:
        s = 0
        h = 0
    else:
        d = (max_c - min_c) / 255
        s = d / (1 - abs(2 * l - 1)) if l != 0 and l != 1 else 0
        
        if max_c == r:
            h = 60 * (((g - b) / (max_c - min_c)) % 6)
        elif max_c == g:
            h = 60 * (((b - r) / (max_c - min_c)) + 2)
        else:
            h = 60 * (((r - g) / (max_c - min_c)) + 4)
    
    if h < 0:
        h += 360
    
    # Determine color name
    if s < 0.1:
        if l < 0.15:
            return "black"
        elif l < 0.35:
            return "charcoal"
        elif l < 0.65:
            return "gray"
        elif l < 0.85:
            return "light gray"
        else:
            return "white"
    
    if l < 0.15:
        return "black"
    if l > 0.9:
        return "white"
    
    # Check for browns/beiges
    if 15 <= h <= 45 and s < 0.5:
        if l < 0.3:
            return "dark brown"
        elif l < 0.5:
            return "brown"
        elif l < 0.7:
            return "tan"
        else:
            return "beige"
    
    # Main colors
    if h < 15 or h >= 345:
        if l < 0.3:
            return "dark red"
        elif l > 0.7:
            return "light pink"
        elif s > 0.7:
            return "red"
        else:
            return "burgundy"
    elif h < 30:
        return "coral" if l > 0.5 else "rust"
    elif h < 45:
        return "orange"
    elif h < 65:
        if l > 0.7:
            return "cream"
        return "yellow" if s > 0.5 else "mustard"
    elif h < 80:
        return "lime green"
    elif h < 150:
        if l < 0.3:
            return "forest green"
        elif s < 0.4:
            return "olive" if l < 0.5 else "sage"
        return "green"
    elif h < 180:
        return "teal"
    elif h < 200:
        return "cyan"
    elif h < 240:
        if l < 0.25:
            return "navy"
        elif l > 0.7:
            return "sky blue"
        return "blue"
    elif h < 280:
        if l < 0.3:
            return "indigo"
        return "purple"
    elif h < 320:
        return "magenta" if s > 0.6 else "mauve"
    else:
        return "pink"


# =============================================================================
# OCCASIONS
# =============================================================================

OCCASIONS = {
    "casual": {
        "name": "Casual",
        "description": "Everyday relaxed wear",
        "preferred_attributes": ["casual", "relaxed", "comfortable", "cotton", "denim"],
        "avoid_attributes": ["formal", "business", "suit", "tie"],
        "color_preference": "any",
        "formality": 0.3
    },
    "formal": {
        "name": "Formal / Business",
        "description": "Professional or formal events",
        "preferred_attributes": ["formal", "business", "elegant", "professional", "dress"],
        "avoid_attributes": ["casual", "sporty", "athletic", "ripped", "distressed"],
        "color_preference": "neutral_base",
        "formality": 0.9
    },
    "sport": {
        "name": "Sport / Athletic",
        "description": "Exercise or sports activities",
        "preferred_attributes": ["sporty", "athletic", "performance", "breathable", "stretch"],
        "avoid_attributes": ["formal", "dress", "suit", "delicate"],
        "color_preference": "any",
        "formality": 0.1
    },
    "party": {
        "name": "Party / Night Out",
        "description": "Evening events and parties",
        "preferred_attributes": ["stylish", "trendy", "elegant", "fashion", "statement"],
        "avoid_attributes": ["sporty", "athletic", "work", "plain"],
        "color_preference": "bold_accent",
        "formality": 0.6
    },
    "date": {
        "name": "Date",
        "description": "Romantic occasions",
        "preferred_attributes": ["stylish", "elegant", "smart", "attractive", "fitted"],
        "avoid_attributes": ["sporty", "worn", "casual", "baggy"],
        "color_preference": "balanced",
        "formality": 0.7
    },
    "home": {
        "name": "Home / Loungewear",
        "description": "Comfortable home wear",
        "preferred_attributes": ["comfortable", "soft", "relaxed", "cozy", "loose"],
        "avoid_attributes": ["formal", "tight", "restrictive"],
        "color_preference": "any",
        "formality": 0.1
    }
}


# =============================================================================
# FASHION RULES
# =============================================================================

FASHION_RULES = {
    "neutral_base": {
        "description": "60%+ neutral colors create a solid foundation",
        "bonus": 0.15
    },
    "single_accent": {
        "description": "One statement color maximizes impact",
        "bonus": 0.12
    },
    "avoid_matchy": {
        "description": "Avoid identical colors (matchy-matchy)",
        "penalty": -0.20
    },
    "temperature_consistency": {
        "description": "Keep warm with warm, cool with cool",
        "bonus": 0.08
    },
    "max_two_bold": {
        "description": "No more than 2 bold/saturated colors",
        "penalty": -0.15
    },
    "dark_bottom_light_top": {
        "description": "Classic proportion - darker on bottom",
        "bonus": 0.05
    }
}


# =============================================================================
# EXPLANATION TEMPLATES
# =============================================================================

STRATEGY_EXPLANATIONS = {
    "neutral_plus_accent": {
        "title": "Neutral Base + Accent",
        "explanation": "This classic combination uses neutral colors as a foundation with one statement color for visual interest. It's sophisticated and always works.",
        "tip": "The accent color draws the eye without overwhelming."
    },
    "neutral_monochrome": {
        "title": "Neutral Palette",
        "explanation": "An all-neutral outfit is timeless and elegant. Black, white, gray, navy, and beige create a refined, professional look.",
        "tip": "Add texture variety to keep it interesting."
    },
    "monochromatic": {
        "title": "Monochromatic",
        "explanation": "Using different shades of the same color creates a sleek, elongating effect. Very sophisticated when done right.",
        "tip": "Vary the lightness and saturation for depth."
    },
    "analogous": {
        "title": "Analogous Harmony",
        "explanation": "Colors next to each other on the color wheel naturally complement each other, creating a harmonious, pleasing look.",
        "tip": "These colors share undertones, so they blend seamlessly."
    },
    "complementary": {
        "title": "Complementary Contrast",
        "explanation": "Opposite colors on the color wheel create bold, eye-catching contrast. Great for making a statement.",
        "tip": "Best when one color dominates and the other accents."
    },
    "triadic": {
        "title": "Triadic Balance",
        "explanation": "Three colors equally spaced on the color wheel create a vibrant, dynamic look. Bold but balanced.",
        "tip": "Let one color lead, use others as accents."
    },
    "split_complementary": {
        "title": "Split Complementary",
        "explanation": "A base color plus two colors adjacent to its complement. Offers contrast without the intensity of direct complements.",
        "tip": "More versatile than pure complementary."
    },
    "mixed": {
        "title": "Eclectic Mix",
        "explanation": "A creative color combination that doesn't follow traditional rules. Can work if balanced well.",
        "tip": "Consider adding more neutrals to ground the look."
    },
    "single_item": {
        "title": "Single Item",
        "explanation": "Just one piece - no color coordination needed!",
        "tip": ""
    }
}

HARMONY_DESCRIPTIONS = {
    "excellent": "Perfectly coordinated - research shows this combination is highly fashionable",
    "good": "Well-balanced colors that work nicely together",
    "acceptable": "A workable combination with room for improvement",
    "poor": "These colors may clash - consider swapping an item"
}


class RecommendationEngine:
    """
    Research-backed outfit recommendation engine.
    
    Features:
    - Goldilocks Principle scoring (moderate coordination is best)
    - Multiple outfit options (3 alternatives)
    - Detailed explanations for each recommendation
    """
    
    def __init__(self):
        self.color_matcher = color_matcher
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _parse_attributes(self, attributes_str: Optional[str]) -> List[str]:
        """Parse attributes JSON string to list."""
        if not attributes_str:
            return []
        try:
            return json.loads(attributes_str)
        except:
            return []
    
    def _get_items_by_layer(
        self, 
        items: List[ClothingItem], 
        layer_type: str
    ) -> List[ClothingItem]:
        """Get all items of a specific layer type."""
        return [item for item in items if item.layer_type == layer_type]
    
    # =========================================================================
    # COLOR SCORING (Goldilocks Principle)
    # =========================================================================
    
    def _calculate_color_score(
        self, 
        item: ClothingItem, 
        selected_colors: List[str],
        outfit_context: Dict[str, Any]
    ) -> float:
        """Calculate color compatibility using Goldilocks principle."""
        if not item.primary_color_hex:
            return 0.6
        
        if not selected_colors:
            is_neutral = self.color_matcher.is_neutral(item.primary_color_hex)
            is_bold = self.color_matcher.is_bold_color(item.primary_color_hex)
            
            if is_neutral:
                return 0.85
            elif is_bold:
                return 0.90
            else:
                return 0.75
        
        item_color = item.primary_color_hex
        
        scores = []
        relationships = []
        
        for selected_color in selected_colors:
            score = self.color_matcher.calculate_match_score(item_color, selected_color)
            relationship = self.color_matcher.get_color_relationship(item_color, selected_color)
            scores.append(score)
            relationships.append(relationship)
        
        base_score = sum(scores) / len(scores)
        
        neutral_count = outfit_context.get("neutral_count", 0)
        bold_count = outfit_context.get("bold_count", 0)
        
        if self.color_matcher.is_neutral(item_color) and bold_count > 0:
            base_score += 0.08
        
        if self.color_matcher.is_bold_color(item_color) and neutral_count >= 2 and bold_count == 0:
            base_score += 0.12
        
        if self.color_matcher.is_bold_color(item_color) and bold_count >= 2:
            base_score -= 0.15
        
        if "identical" in relationships:
            base_score -= 0.20
        
        return max(0.0, min(1.0, base_score))
    
    # =========================================================================
    # WEATHER SCORING
    # =========================================================================
    
    def _calculate_weather_score(
        self, 
        item: ClothingItem, 
        weather_suggestions: Dict[str, Any]
    ) -> float:
        """Calculate weather appropriateness score."""
        score = 1.0
        attributes = self._parse_attributes(item.attributes)
        attributes_lower = [a.lower() for a in attributes]
        clothing_type = item.clothing_type.lower()
        
        needs_warm = weather_suggestions.get("warm_clothing", False)
        light_clothing = weather_suggestions.get("light_clothing", False)
        needs_rain = weather_suggestions.get("needs_rain_protection", False)
        
        if light_clothing:
            heavy_terms = ["wool", "heavy", "thick", "warm", "fleece", "knit", "leather", "sweater", "hoodie"]
            for term in heavy_terms:
                if any(term in a for a in attributes_lower) or term in clothing_type:
                    score -= 0.15
        
        if needs_warm:
            light_terms = ["thin", "light", "sleeveless", "mesh", "sheer", "linen", "tank"]
            for term in light_terms:
                if any(term in a for a in attributes_lower) or term in clothing_type:
                    score -= 0.15
            
            warm_terms = ["wool", "fleece", "warm", "knit", "sweater", "hoodie"]
            for term in warm_terms:
                if any(term in a for a in attributes_lower) or term in clothing_type:
                    score += 0.10
                    break
        
        if needs_rain:
            rain_terms = ["waterproof", "water-resistant", "rain", "nylon", "gore-tex"]
            for term in rain_terms:
                if any(term in a for a in attributes_lower):
                    score += 0.10
                    break
        
        return max(0.0, min(1.0, score))
    
    # =========================================================================
    # OCCASION SCORING
    # =========================================================================
    
    def _calculate_occasion_score(
        self, 
        item: ClothingItem, 
        occasion: str
    ) -> float:
        """Calculate occasion suitability score."""
        if occasion not in OCCASIONS:
            return 1.0
        
        score = 1.0
        occasion_config = OCCASIONS[occasion]
        preferred = occasion_config["preferred_attributes"]
        avoid = occasion_config["avoid_attributes"]
        
        attributes = self._parse_attributes(item.attributes)
        attributes_lower = [a.lower() for a in attributes]
        clothing_type = item.clothing_type.lower()
        
        all_text = attributes_lower + [clothing_type]
        
        for attr in preferred:
            if any(attr in text for text in all_text):
                score += 0.08
        
        for attr in avoid:
            if any(attr in text for text in all_text):
                score -= 0.15
        
        return max(0.0, min(1.0, score))
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def _calculate_total_score(
        self,
        item: ClothingItem,
        selected_colors: List[str],
        weather_suggestions: Dict[str, Any],
        occasion: str,
        outfit_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate total score with Goldilocks-based color matching."""
        color_score = self._calculate_color_score(item, selected_colors, outfit_context)
        weather_score = self._calculate_weather_score(item, weather_suggestions)
        occasion_score = self._calculate_occasion_score(item, occasion)
        
        total_score = (
            color_score * 0.60 +
            weather_score * 0.20 +
            occasion_score * 0.20
        )
        
        return {
            "total": round(total_score, 3),
            "color": round(color_score, 3),
            "weather": round(weather_score, 3),
            "occasion": round(occasion_score, 3)
        }
    
    # =========================================================================
    # ITEM SELECTION (with exclusion for multiple outfits)
    # =========================================================================
    
    def _select_base_item(
        self,
        items: List[ClothingItem],
        weather_suggestions: Dict[str, Any],
        occasion: str,
        exclude_ids: List[int] = None
    ) -> Optional[ClothingItem]:
        """Select the base item, optionally excluding certain items."""
        exclude_ids = exclude_ids or []
        
        tops = [i for i in self._get_items_by_layer(items, "top") if i.id not in exclude_ids]
        bottoms = [i for i in self._get_items_by_layer(items, "bottom") if i.id not in exclude_ids]
        
        candidates = tops if tops else bottoms
        if not candidates:
            return None
        
        scored = []
        for item in candidates:
            score = 0.5
            
            has_color = item.primary_color_hex is not None
            
            if has_color:
                is_neutral = self.color_matcher.is_neutral(item.primary_color_hex)
                is_bold = self.color_matcher.is_bold_color(item.primary_color_hex)
                
                if is_bold:
                    score += 0.35
                elif is_neutral:
                    score += 0.25
                else:
                    score += 0.20
            
            weather_score = self._calculate_weather_score(item, weather_suggestions)
            occasion_score = self._calculate_occasion_score(item, occasion)
            score += weather_score * 0.15 + occasion_score * 0.15
            
            scored.append((item, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        top_candidates = [
            item for item, s in scored[:5] 
            if s >= scored[0][1] - 0.20
        ]
        
        return random.choice(top_candidates) if top_candidates else scored[0][0]
    
    def _select_matching_item(
        self,
        candidates: List[ClothingItem],
        selected_colors: List[str],
        weather_suggestions: Dict[str, Any],
        occasion: str,
        outfit_context: Dict[str, Any],
        exclude_ids: List[int] = None
    ) -> Optional[Tuple[ClothingItem, Dict[str, Any]]]:
        """Select the best color-matching item, with exclusion support."""
        exclude_ids = exclude_ids or []
        candidates = [c for c in candidates if c.id not in exclude_ids]
        
        if not candidates:
            return None
        
        scored = []
        for item in candidates:
            scores = self._calculate_total_score(
                item, selected_colors, weather_suggestions, occasion, outfit_context
            )
            scored.append((item, scores))
        
        scored.sort(key=lambda x: x[1]["total"], reverse=True)
        
        min_color_score = 0.35
        valid = [
            (item, scores) for item, scores in scored 
            if scores["color"] >= min_color_score
        ]
        
        if not valid:
            valid = scored
        
        top_candidates = [
            (item, scores) for item, scores in valid[:5]
            if scores["total"] >= valid[0][1]["total"] - 0.15
        ]
        
        selected = random.choice(top_candidates) if top_candidates else valid[0]
        return selected
    
    # =========================================================================
    # OUTFIT ANALYSIS & EXPLANATIONS
    # =========================================================================
    
    def _analyze_outfit_colors(self, hex_colors: List[str]) -> Dict[str, Any]:
        """Analyze the outfit's color palette."""
        if len(hex_colors) < 2:
            return {
                "strategy": "single_item",
                "score": 1.0,
                "harmony": "excellent",
                "description": "Single item outfit"
            }
        
        harmony = self.color_matcher.calculate_outfit_harmony(hex_colors)
        
        return {
            "strategy": harmony.get("strategy", "mixed"),
            "score": harmony["score"],
            "harmony": harmony["harmony"],
            "description": harmony.get("strategy_description", "Mixed color palette"),
            "relationships": harmony.get("details", [])
        }
    
    def _generate_outfit_explanation(
        self,
        outfit: Dict[str, Any],
        color_analysis: Dict[str, Any],
        hex_colors: List[str],
        occasion: str
    ) -> Dict[str, Any]:
        """Generate detailed explanation for why this outfit works."""
        
        strategy = color_analysis.get("strategy", "mixed")
        strategy_info = STRATEGY_EXPLANATIONS.get(strategy, STRATEGY_EXPLANATIONS["mixed"])
        
        # Build color description
        color_names = [get_color_name(c) for c in hex_colors]
        unique_colors = list(dict.fromkeys(color_names))  # Remove duplicates, keep order
        
        if len(unique_colors) == 1:
            color_summary = f"A {unique_colors[0]} focused look"
        elif len(unique_colors) == 2:
            color_summary = f"{unique_colors[0].title()} and {unique_colors[1]}"
        else:
            color_summary = f"{', '.join(unique_colors[:-1])}, and {unique_colors[-1]}"
        
        # Score interpretation
        score = color_analysis.get("score", 0.7)
        harmony = color_analysis.get("harmony", "good")
        harmony_desc = HARMONY_DESCRIPTIONS.get(harmony, "A reasonable color combination")
        
        # Build item-by-item breakdown
        item_explanations = []
        for layer, item_data in outfit.items():
            if isinstance(item_data, dict) and "clothing_type" in item_data:
                item_color = item_data.get("primary_color_hex")
                color_name = get_color_name(item_color) if item_color else "unknown"
                
                is_neutral = self.color_matcher.is_neutral(item_color) if item_color else True
                is_bold = self.color_matcher.is_bold_color(item_color) if item_color else False
                
                role = "neutral base" if is_neutral else ("statement piece" if is_bold else "supporting color")
                
                item_explanations.append({
                    "layer": layer,
                    "item": item_data.get("clothing_type", "item"),
                    "color": color_name,
                    "role": role
                })
        
        # Occasion fit
        occasion_name = OCCASIONS.get(occasion, {}).get("name", occasion)
        
        return {
            "summary": f"{strategy_info['title']}: {color_summary}",
            "color_strategy": {
                "name": strategy_info["title"],
                "explanation": strategy_info["explanation"],
                "tip": strategy_info["tip"]
            },
            "harmony": {
                "score": round(score, 2),
                "level": harmony,
                "description": harmony_desc
            },
            "colors_used": [
                {"hex": c, "name": get_color_name(c)} for c in hex_colors
            ],
            "item_breakdown": item_explanations,
            "occasion_fit": f"Styled for {occasion_name}"
        }
    
    def _apply_fashion_rules_bonus(
        self, 
        outfit: Dict[str, Any],
        hex_colors: List[str]
    ) -> Tuple[float, List[str]]:
        """Apply fashion rules and return adjustments with explanations."""
        adjustments = 0.0
        explanations = []
        
        neutrals = [c for c in hex_colors if self.color_matcher.is_neutral(c)]
        bold_colors = [c for c in hex_colors if self.color_matcher.is_bold_color(c)]
        
        if len(neutrals) >= len(hex_colors) * 0.5:
            adjustments += FASHION_RULES["neutral_base"]["bonus"]
            explanations.append("✓ Strong neutral foundation")
        
        if len(bold_colors) == 1:
            adjustments += FASHION_RULES["single_accent"]["bonus"]
            explanations.append("✓ Perfect single accent color")
        
        if len(bold_colors) > 2:
            adjustments += FASHION_RULES["max_two_bold"]["penalty"]
            explanations.append("⚠ Multiple bold colors competing")
        
        temperatures = [
            self.color_matcher.get_color_temperature(c) 
            for c in hex_colors 
            if not self.color_matcher.is_neutral(c)
        ]
        if temperatures and all(t == temperatures[0] for t in temperatures):
            adjustments += FASHION_RULES["temperature_consistency"]["bonus"]
            explanations.append(f"✓ Consistent {temperatures[0]} color temperature")
        
        if "top" in outfit and "bottom" in outfit:
            top_item = outfit["top"]
            bottom_item = outfit["bottom"]
            
            if isinstance(top_item, dict) and isinstance(bottom_item, dict):
                top_hex = top_item.get("primary_color_hex")
                bottom_hex = bottom_item.get("primary_color_hex")
                
                if top_hex and bottom_hex:
                    top_l = self.color_matcher.hex_to_hsl(top_hex)[2]
                    bottom_l = self.color_matcher.hex_to_hsl(bottom_hex)[2]
                    
                    if bottom_l < top_l:
                        adjustments += FASHION_RULES["dark_bottom_light_top"]["bonus"]
                        explanations.append("✓ Classic dark bottom, light top")
        
        return adjustments, explanations
    
    # =========================================================================
    # SINGLE OUTFIT GENERATION
    # =========================================================================
    
    def _generate_single_outfit(
        self,
        all_items: List[ClothingItem],
        weather_suggestions: Dict[str, Any],
        occasion: str,
        required_layers: List[str],
        exclude_ids: List[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a single outfit, optionally excluding certain items."""
        exclude_ids = exclude_ids or []
        
        outfit = {}
        selected_colors = []
        selection_details = []
        
        outfit_context = {
            "neutral_count": 0,
            "bold_count": 0,
            "temperature": None
        }
        
        layer_order = ["top", "bottom", "outerwear", "footwear", "socks"]
        
        for layer in layer_order:
            if layer not in required_layers:
                continue
            
            candidates = self._get_items_by_layer(all_items, layer)
            if not candidates:
                continue
            
            if not selected_colors:
                selected_item = self._select_base_item(
                    candidates, weather_suggestions, occasion, exclude_ids
                )
                scores = self._calculate_total_score(
                    selected_item, [], weather_suggestions, occasion, outfit_context
                ) if selected_item else None
            else:
                result = self._select_matching_item(
                    candidates, selected_colors, weather_suggestions, occasion, 
                    outfit_context, exclude_ids
                )
                if result:
                    selected_item, scores = result
                else:
                    selected_item, scores = None, None
            
            if selected_item:
                if selected_item.primary_color_hex:
                    if self.color_matcher.is_neutral(selected_item.primary_color_hex):
                        outfit_context["neutral_count"] += 1
                    if self.color_matcher.is_bold_color(selected_item.primary_color_hex):
                        outfit_context["bold_count"] += 1
                
                outfit[layer] = {
                    "id": selected_item.id,
                    "clothing_type": selected_item.clothing_type,
                    "image_path": selected_item.image_path,
                    "primary_color_hex": selected_item.primary_color_hex,
                    "secondary_color_hex": selected_item.secondary_color_hex,
                    "attributes": self._parse_attributes(selected_item.attributes),
                    "scores": scores
                }
                
                selection_details.append({
                    "layer": layer,
                    "item_id": selected_item.id,
                    "item_type": selected_item.clothing_type,
                    "color": selected_item.primary_color_hex,
                    "color_name": get_color_name(selected_item.primary_color_hex),
                    "is_neutral": self.color_matcher.is_neutral(selected_item.primary_color_hex) if selected_item.primary_color_hex else True,
                    "is_bold": self.color_matcher.is_bold_color(selected_item.primary_color_hex) if selected_item.primary_color_hex else False,
                    "scores": scores
                })
                
                if selected_item.primary_color_hex:
                    selected_colors.append(selected_item.primary_color_hex)
        
        if not outfit:
            return None
        
        # Analyze colors
        color_analysis = self._analyze_outfit_colors(selected_colors)
        
        # Apply fashion rules
        rule_bonus, rule_explanations = self._apply_fashion_rules_bonus(outfit, selected_colors)

        final_score = min(1.0, color_analysis["score"] + rule_bonus)

        # Cap "safe but boring" all-neutral outfits (Goldilocks Principle)
        if color_analysis.get("strategy") == "neutral_monochrome":
            final_score = min(final_score, 0.90)

        if final_score >= 0.85:
            harmony_level = "excellent"
        elif final_score >= 0.70:
            harmony_level = "good"
        elif final_score >= 0.55:
            harmony_level = "acceptable"
        else:
            harmony_level = "poor"
        
        color_analysis["score"] = final_score
        color_analysis["harmony"] = harmony_level
        
        # Generate explanation
        explanation = self._generate_outfit_explanation(
            outfit, color_analysis, selected_colors, occasion
        )
        
        missing_layers = [layer for layer in required_layers if layer not in outfit]
        
        return {
            "outfit": outfit,
            "color_harmony": {
                "score": round(final_score, 2),
                "harmony": harmony_level,
                "strategy": color_analysis["strategy"],
                "description": color_analysis.get("description", ""),
                "fashion_rules_applied": rule_explanations
            },
            "explanation": explanation,
            "selection_details": selection_details,
            "colors_used": selected_colors,
            "outfit_summary": {
                "neutral_count": outfit_context["neutral_count"],
                "bold_count": outfit_context["bold_count"],
                "total_items": len(outfit)
            },
            "missing_layers": missing_layers,
            "complete": len(missing_layers) == 0
        }
    
    # =========================================================================
    # MAIN GENERATION METHOD (Multiple Outfits)
    # =========================================================================
    
    def generate_outfit(
        self,
        db: Session,
        user_id: int,
        weather_suggestions: Dict[str, Any],
        occasion: str = "casual",
        num_options: int = 3
    ) -> Dict[str, Any]:
        """
        Generate multiple outfit recommendations.
        
        Returns 3 different outfit options ranked by score.
        """
        all_items = db.query(ClothingItem).filter(
            ClothingItem.user_id == user_id
        ).all()
        
        if not all_items:
            return {
                "success": False,
                "message": "No clothing items in wardrobe",
                "outfits": []
            }
        
        required_layers = weather_suggestions.get("recommended_layers", 
            ["top", "bottom", "footwear", "socks"])
        
        # Generate multiple outfit options
        outfits = []
        used_base_ids = []
        
        for i in range(num_options):
            outfit_result = self._generate_single_outfit(
                all_items,
                weather_suggestions,
                occasion,
                required_layers,
                exclude_ids=used_base_ids
            )
            
            if outfit_result:
                # Track used base items for variety
                if "top" in outfit_result["outfit"]:
                    used_base_ids.append(outfit_result["outfit"]["top"]["id"])
                elif "bottom" in outfit_result["outfit"]:
                    used_base_ids.append(outfit_result["outfit"]["bottom"]["id"])
                
                outfit_result["option_number"] = i + 1
                outfits.append(outfit_result)
        
        if not outfits:
            return {
                "success": False,
                "message": "Could not generate any outfits",
                "outfits": []
            }

        # Calculate composite score for each outfit (60/20/20 weighting)
        for outfit in outfits:
            # Get color harmony score
            harmony_score = outfit["color_harmony"]["score"]

            # Calculate average weather score across items
            weather_scores = []
            occasion_scores = []

            for _, item_data in outfit["outfit"].items():
                if isinstance(item_data, dict) and "scores" in item_data and item_data["scores"]:
                    weather_scores.append(item_data["scores"].get("weather", 0.5))
                    occasion_scores.append(item_data["scores"].get("occasion", 0.5))

            weather_avg = sum(weather_scores) / len(weather_scores) if weather_scores else 0.5
            occasion_avg = sum(occasion_scores) / len(occasion_scores) if occasion_scores else 0.5

            # Compute weighted composite score (thesis-consistent)
            composite_score = (
                0.60 * harmony_score +
                0.20 * weather_avg +
                0.20 * occasion_avg
            )

            # Store in outfit dict for transparency
            outfit["composite_score"] = round(composite_score, 3)
            outfit["score_breakdown"] = {
                "color_harmony": round(harmony_score, 3),
                "weather_suitability": round(weather_avg, 3),
                "occasion_suitability": round(occasion_avg, 3),
                "weights": {"color": 0.60, "weather": 0.20, "occasion": 0.20}
            }

        # Sort by composite score (NOT just color harmony)
        outfits.sort(key=lambda x: x["composite_score"], reverse=True)

        # Re-number after sorting
        for i, outfit in enumerate(outfits):
            outfit["option_number"] = i + 1
            outfit["is_recommended"] = (i == 0)
        
        return {
            "success": True,
            "occasion": OCCASIONS.get(occasion, {}).get("name", occasion),
            "total_options": len(outfits),
            "outfits": outfits,
            "best_outfit": outfits[0] if outfits else None
        }
    
    # =========================================================================
    # ADDITIONAL METHODS
    # =========================================================================
    
    def generate_by_color(
        self,
        db: Session,
        user_id: int,
        base_color_hex: str,
        weather_suggestions: Dict[str, Any],
        occasion: str = "casual"
    ) -> Dict[str, Any]:
        """Generate outfit starting from a specific color."""
        all_items = db.query(ClothingItem).filter(
            ClothingItem.user_id == user_id
        ).all()
        
        if not all_items:
            return {
                "success": False,
                "message": "No clothing items in wardrobe",
                "outfit": None
            }
        
        matching_items = []
        for item in all_items:
            if item.primary_color_hex:
                score = self.color_matcher.calculate_match_score(
                    item.primary_color_hex, base_color_hex
                )
                if score >= 0.65:
                    matching_items.append((item, score))
        
        if not matching_items:
            return {
                "success": False,
                "message": f"No items found matching the requested color",
                "outfit": None
            }
        
        matching_items.sort(key=lambda x: x[1], reverse=True)
        base_item = matching_items[0][0]
        
        required_layers = weather_suggestions.get("recommended_layers", 
            ["top", "bottom", "footwear", "socks"])
        
        outfit = {}
        selected_colors = [base_item.primary_color_hex]
        
        outfit_context = {
            "neutral_count": 1 if self.color_matcher.is_neutral(base_item.primary_color_hex) else 0,
            "bold_count": 1 if self.color_matcher.is_bold_color(base_item.primary_color_hex) else 0
        }
        
        outfit[base_item.layer_type] = {
            "id": base_item.id,
            "clothing_type": base_item.clothing_type,
            "image_path": base_item.image_path,
            "primary_color_hex": base_item.primary_color_hex,
            "secondary_color_hex": base_item.secondary_color_hex,
            "attributes": self._parse_attributes(base_item.attributes)
        }
        
        layer_order = ["top", "bottom", "outerwear", "footwear", "socks"]
        
        for layer in layer_order:
            if layer not in required_layers or layer == base_item.layer_type:
                continue
            
            candidates = self._get_items_by_layer(all_items, layer)
            if not candidates:
                continue
            
            result = self._select_matching_item(
                candidates, selected_colors, weather_suggestions, occasion, outfit_context
            )
            
            if result:
                selected_item, scores = result
                
                outfit[layer] = {
                    "id": selected_item.id,
                    "clothing_type": selected_item.clothing_type,
                    "image_path": selected_item.image_path,
                    "primary_color_hex": selected_item.primary_color_hex,
                    "secondary_color_hex": selected_item.secondary_color_hex,
                    "attributes": self._parse_attributes(selected_item.attributes)
                }
                
                if selected_item.primary_color_hex:
                    selected_colors.append(selected_item.primary_color_hex)
                    if self.color_matcher.is_neutral(selected_item.primary_color_hex):
                        outfit_context["neutral_count"] += 1
                    if self.color_matcher.is_bold_color(selected_item.primary_color_hex):
                        outfit_context["bold_count"] += 1
        
        color_analysis = self._analyze_outfit_colors(selected_colors)
        explanation = self._generate_outfit_explanation(outfit, color_analysis, selected_colors, occasion)
        missing_layers = [layer for layer in required_layers if layer not in outfit]
        
        return {
            "success": True,
            "occasion": OCCASIONS.get(occasion, {}).get("name", occasion),
            "base_color": base_color_hex,
            "base_color_name": get_color_name(base_color_hex),
            "outfit": outfit,
            "color_harmony": {
                "score": color_analysis["score"],
                "harmony": color_analysis["harmony"],
                "strategy": color_analysis["strategy"],
                "description": color_analysis["description"]
            },
            "explanation": explanation,
            "colors_used": selected_colors,
            "missing_layers": missing_layers,
            "complete": len(missing_layers) == 0
        }
    
    def get_occasions(self) -> List[Dict[str, str]]:
        """Return list of available occasions."""
        return [
            {"id": key, "name": value["name"], "description": value["description"]}
            for key, value in OCCASIONS.items()
        ]
    
    def get_color_strategies(self) -> List[Dict[str, str]]:
        """Return list of winning color strategies with explanations."""
        strategies = []
        for key, value in self.color_matcher.WINNING_COMBINATIONS.items():
            strategy_explanation = STRATEGY_EXPLANATIONS.get(key, {})
            strategies.append({
                "id": key,
                "name": value.get("name", key),
                "description": value.get("description", ""),
                "score": value.get("score", 0.7),
                "example": value.get("example", ""),
                "tip": strategy_explanation.get("tip", "")
            })
        return strategies


# Global instance
recommendation_engine = RecommendationEngine()