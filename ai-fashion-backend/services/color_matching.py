"""
Color Matching Service
Research-backed color coordination using the Goldilocks Principle.

References:
- Gray et al. (2014) "The Science of Style" - PLOS ONE
- Li et al. (2025) "Colour harmony evaluation" - Fashion and Textiles
"""

import colorsys
import math
from typing import List, Tuple, Dict, Any, Optional


class ColorMatcher:
    """
    Matches colors using HSL color space with research-backed scoring.
    
    Key Principle: The Goldilocks Effect
    - Too similar (matchy-matchy) = unfashionable
    - Too different (clashing) = unfashionable  
    - Moderate coordination = OPTIMAL
    
    Color Relationships:
    - Complementary: Hue ± 180° (bold contrast)
    - Analogous: Hue ± 30° (harmonious)
    - Triadic: Hue ± 120° (vibrant)
    - Split-Complementary: Hue ± 150° (balanced contrast)
    - Neutral: Low saturation pairs with anything
    """
    
    # ==========================================================================
    # THRESHOLDS
    # ==========================================================================
    
    NEUTRAL_SATURATION_THRESHOLD = 0.15
    NEUTRAL_LIGHTNESS_LOW = 0.12
    NEUTRAL_LIGHTNESS_HIGH = 0.88
    
    # Hue difference thresholds (degrees)
    ANALOGOUS_RANGE = 30
    COMPLEMENTARY_RANGE = 25
    TRIADIC_RANGE = 20
    SPLIT_COMPLEMENTARY_RANGE = 20
    
    # ==========================================================================
    # NEUTRAL COLOR DEFINITIONS
    # ==========================================================================
    
    NEUTRAL_COLORS = {
        # Blacks
        "black": {"h_range": (0, 360), "s_max": 0.15, "l_max": 0.15},
        # Whites
        "white": {"h_range": (0, 360), "s_max": 0.15, "l_min": 0.85},
        # Grays
        "gray": {"h_range": (0, 360), "s_max": 0.15, "l_range": (0.15, 0.85)},
        # Navy (acts as neutral in fashion)
        "navy": {"h_range": (220, 250), "s_range": (0.3, 0.8), "l_range": (0.1, 0.3)},
        # Beige/Tan
        "beige": {"h_range": (25, 45), "s_range": (0.1, 0.4), "l_range": (0.6, 0.85)},
        # Brown
        "brown": {"h_range": (15, 40), "s_range": (0.2, 0.6), "l_range": (0.15, 0.4)},
        # Cream
        "cream": {"h_range": (40, 60), "s_range": (0.1, 0.3), "l_range": (0.8, 0.95)},
    }
    
    # ==========================================================================
    # WINNING COMBINATIONS (Research-backed)
    # ==========================================================================
    
    WINNING_COMBINATIONS = {
        # Most reliable combinations
        "neutral_monochrome": {
            "description": "All neutrals (black, white, gray, navy, beige)",
            "score": 0.90,
            "example": "Black pants, white shirt, gray jacket"
        },
        "neutral_plus_one_accent": {
            "description": "Neutral base with one statement color",
            "score": 0.95,
            "example": "Navy suit, white shirt, burgundy tie"
        },
        "monochromatic_shades": {
            "description": "Same hue, different lightness/saturation",
            "score": 0.88,
            "example": "Light blue shirt, dark blue pants"
        },
        "analogous_harmony": {
            "description": "Adjacent colors on wheel",
            "score": 0.85,
            "example": "Blue and teal, or red and orange"
        },
        "complementary_muted": {
            "description": "Opposite colors, both muted/desaturated",
            "score": 0.82,
            "example": "Muted blue with muted orange/rust"
        },
        "split_complementary": {
            "description": "Base color + two adjacent to complement",
            "score": 0.80,
            "example": "Blue with yellow-orange and red-orange"
        },
        "triadic_one_dominant": {
            "description": "Three colors, one dominant, two accents",
            "score": 0.75,
            "example": "Navy dominant, red and yellow accents"
        },
    }
    
    # ==========================================================================
    # CONVERSION UTILITIES
    # ==========================================================================
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string."""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def hex_to_hsl(self, hex_color: str) -> Tuple[float, float, float]:
        """
        Convert hex color to HSL.
        Returns (hue, saturation, lightness) where:
        - hue: 0-360 degrees
        - saturation: 0-1
        - lightness: 0-1
        """
        rgb = self.hex_to_rgb(hex_color)
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s, l)
    
    def hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """Convert HSL to hex color."""
        r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
        return "#{:02x}{:02x}{:02x}".format(
            int(r * 255), int(g * 255), int(b * 255)
        )
    
    # ==========================================================================
    # COLOR CLASSIFICATION
    # ==========================================================================
    
    def is_neutral(self, hex_color: str) -> bool:
        """
        Check if a color is neutral (low saturation or acts as neutral).
        Includes: black, white, gray, navy, beige, brown, cream
        """
        h, s, l = self.hex_to_hsl(hex_color)
        
        # Pure neutrals (no saturation)
        if s < self.NEUTRAL_SATURATION_THRESHOLD:
            return True
        
        # Very dark (near black)
        if l < self.NEUTRAL_LIGHTNESS_LOW:
            return True
        
        # Very light (near white)
        if l > self.NEUTRAL_LIGHTNESS_HIGH:
            return True
        
        # Navy blues (fashion neutral)
        if 220 <= h <= 250 and s < 0.8 and l < 0.35:
            return True
        
        # Beige/tan/cream
        if 25 <= h <= 50 and s < 0.4 and l > 0.55:
            return True
        
        # Brown
        if 15 <= h <= 40 and s < 0.6 and l < 0.4:
            return True
        
        return False
    
    def is_bold_color(self, hex_color: str) -> bool:
        """Check if a color is bold/saturated (statement color)."""
        h, s, l = self.hex_to_hsl(hex_color)
        return s > 0.5 and 0.25 < l < 0.75
    
    def get_color_temperature(self, hex_color: str) -> str:
        """Determine if a color is warm, cool, or neutral."""
        h, s, l = self.hex_to_hsl(hex_color)
        
        if s < 0.15:
            return "neutral"
        
        # Warm colors: red, orange, yellow (0-60, 300-360)
        if h <= 60 or h >= 300:
            return "warm"
        
        # Cool colors: green, blue, purple (120-270)
        if 120 <= h <= 270:
            return "cool"
        
        # Transitional zones
        if 60 < h < 120:
            return "warm"  # Yellow-green leans warm
        
        return "cool"  # 270-300 purple leans cool
    
    def get_color_category(self, hex_color: str) -> str:
        """Get the general color category."""
        h, s, l = self.hex_to_hsl(hex_color)
        
        if s < 0.1:
            if l < 0.2:
                return "black"
            elif l > 0.8:
                return "white"
            else:
                return "gray"
        
        # Map hue to color name
        if h < 15 or h >= 345:
            return "red"
        elif h < 45:
            return "orange"
        elif h < 65:
            return "yellow"
        elif h < 150:
            return "green"
        elif h < 200:
            return "cyan"
        elif h < 260:
            return "blue"
        elif h < 290:
            return "purple"
        elif h < 345:
            return "pink"
        
        return "unknown"
    
    # ==========================================================================
    # HUE CALCULATIONS
    # ==========================================================================
    
    def get_hue_difference(self, hue1: float, hue2: float) -> float:
        """Calculate the smallest angle between two hues (0-180)."""
        diff = abs(hue1 - hue2)
        return min(diff, 360 - diff)
    
    def get_color_relationship(self, hex_color1: str, hex_color2: str) -> str:
        """
        Determine the relationship between two colors.
        Returns: 'identical', 'monochromatic', 'neutral', 'analogous', 
                 'complementary', 'split_complementary', 'triadic', or 'clash'
        """
        # Check for neutrals first
        neutral1 = self.is_neutral(hex_color1)
        neutral2 = self.is_neutral(hex_color2)
        
        if neutral1 and neutral2:
            return "neutral"
        
        if neutral1 or neutral2:
            return "neutral_accent"
        
        h1, s1, l1 = self.hex_to_hsl(hex_color1)
        h2, s2, l2 = self.hex_to_hsl(hex_color2)
        
        hue_diff = self.get_hue_difference(h1, h2)
        lightness_diff = abs(l1 - l2)
        saturation_diff = abs(s1 - s2)
        
        # Identical colors (exact match)
        if hue_diff < 5 and lightness_diff < 0.1 and saturation_diff < 0.1:
            return "identical"
        
        # Monochromatic: same hue, different lightness/saturation
        if hue_diff < 15 and (lightness_diff > 0.15 or saturation_diff > 0.15):
            return "monochromatic"
        
        # Analogous: within 30 degrees
        if hue_diff <= self.ANALOGOUS_RANGE:
            return "analogous"
        
        # Complementary: around 180 degrees
        if abs(hue_diff - 180) <= self.COMPLEMENTARY_RANGE:
            return "complementary"
        
        # Split-complementary: around 150 or 210 degrees
        if abs(hue_diff - 150) <= self.SPLIT_COMPLEMENTARY_RANGE:
            return "split_complementary"
        if abs(hue_diff - 210) <= self.SPLIT_COMPLEMENTARY_RANGE:
            return "split_complementary"
        
        # Triadic: around 120 degrees
        if abs(hue_diff - 120) <= self.TRIADIC_RANGE:
            return "triadic"
        
        # Clash zone: 60-90 degrees and 90-120 degrees (awkward zone)
        if 45 <= hue_diff <= 75:
            return "clash"
        if 85 <= hue_diff <= 115:
            return "clash"
        
        # Default to acceptable
        return "acceptable"
    
    # ==========================================================================
    # GOLDILOCKS SCORING (Research-backed)
    # ==========================================================================
    
    def calculate_goldilocks_score(self, coordination_level: float) -> float:
        """
        Apply the Goldilocks Principle quadratic curve.

        Inspired by: Gray et al. (2014) "The Science of Style"
        Original finding: Moderate coordination receives highest fashionability ratings

        Our operationalization:
        - Formula: Fashionableness = -0.50m² + 0.62m + 0.49
        - Peak at m ≈ 0.62 (moderate coordination)
        - Input 'coordination_level' now represents "closeness to ideal harmony zones"
        - Not raw similarity, so complementary colors (ideal zone) score well

        Args:
            coordination_level: How close the pair is to ideal fashion harmony (0-1)
                               0.6-0.7 = optimal range for fashion coordination

        Returns:
            Fashion score (0-1) with peak at moderate coordination
        """
        m = coordination_level

        # Original formula normalized to 0-1 range
        # Peak is at m = 0.62 (moderate coordination)
        raw_score = -0.50 * (m ** 2) + 0.62 * m + 0.49

        # Normalize to 0-1 range (original peaks around 0.68)
        normalized = raw_score / 0.68

        return max(0.0, min(1.0, normalized))
    
    def calculate_coordination_level(self, hex_color1: str, hex_color2: str) -> float:
        """
        Calculate coordination level based on distance to ideal fashion harmony zones.

        CRITICAL CHANGE: This is NOT similarity, but "how close to ideal coordination."
        Returns values that peak around harmony zones (0.6-0.7 = ideal for Goldilocks).

        Ideal zones:
        - ~20°: Monochromatic shades
        - ~30°: Analogous harmony
        - ~150°: Split-complementary
        - ~180°: Complementary contrast
        """
        # Handle neutrals first (they always coordinate well)
        if self.is_neutral(hex_color1) and self.is_neutral(hex_color2):
            return 0.70  # Neutrals together = good moderate coordination

        if self.is_neutral(hex_color1) or self.is_neutral(hex_color2):
            return 0.65  # Neutral + color = good coordination (Goldilocks zone)

        h1, s1, l1 = self.hex_to_hsl(hex_color1)
        h2, s2, l2 = self.hex_to_hsl(hex_color2)

        hue_diff = self.get_hue_difference(h1, h2)
        lightness_diff = abs(l1 - l2)
        saturation_diff = abs(s1 - s2)

        # Calculate "distance to nearest ideal harmony zone"
        # Define ideal hue distances for fashion
        ideal_zones = [
            20,   # Monochromatic shades
            30,   # Analogous harmony
            120,  # Triadic
            150,  # Split-complementary
            180,  # Complementary
        ]

        # Find closest ideal zone
        min_distance_to_ideal = min(abs(hue_diff - zone) for zone in ideal_zones)

        # Convert distance to coordination score
        # Closer to ideal zone = higher coordination
        # Max distance from any zone = 30° (halfway between zones)
        hue_coordination = 1 - (min_distance_to_ideal / 30)
        hue_coordination = max(0.0, min(1.0, hue_coordination))

        # Scale to Goldilocks optimal range (0.55-0.75)
        # This ensures harmony zones score in the "moderate" range
        hue_coordination = 0.55 + (hue_coordination * 0.20)

        # Lightness and saturation contribute to refinement
        lightness_coordination = 1 - lightness_diff
        saturation_coordination = 1 - saturation_diff

        # Weighted combination (hue harmony matters most)
        final_coordination = (
            hue_coordination * 0.70 +
            lightness_coordination * 0.20 +
            saturation_coordination * 0.10
        )

        return max(0.0, min(1.0, final_coordination))
    
    def calculate_match_score(self, hex_color1: str, hex_color2: str) -> float:
        """
        Calculate a fashion-appropriate match score using Goldilocks principle.
        
        Key insight: Neither too similar nor too different is best.
        """
        relationship = self.get_color_relationship(hex_color1, hex_color2)
        coordination = self.calculate_coordination_level(hex_color1, hex_color2)
        
        # Base score from Goldilocks curve
        goldilocks_score = self.calculate_goldilocks_score(coordination)
        
        # Relationship-based adjustments
        # SMALLER adjustments now because coordination_level already encodes harmony
        adjustments = {
            "identical": -0.20,          # Still penalize exact matches
            "monochromatic": 0.05,       # Small boost (already in ideal zone)
            "neutral": 0.10,             # Reliable neutral pairing
            "neutral_accent": 0.15,      # Classic winning combo
            "analogous": 0.05,           # Already scored well via zones
            "complementary": 0.03,       # Already scored well via zones
            "split_complementary": 0.03, # Already scored well via zones
            "triadic": 0.0,              # Neutral adjustment
            "acceptable": -0.10,         # Moderate penalty
            "clash": -0.25,              # Strong penalty for clash zones
        }
        
        adjustment = adjustments.get(relationship, 0)
        final_score = goldilocks_score + adjustment
        
        return max(0.0, min(1.0, final_score))
    
    # ==========================================================================
    # OUTFIT HARMONY ANALYSIS
    # ==========================================================================
    
    def analyze_outfit_combination(self, hex_colors: List[str]) -> Dict[str, Any]:
        """
        Analyze an outfit's color combination and identify the strategy used.
        """
        if len(hex_colors) < 2:
            return {
                "strategy": "single_item",
                "score": 1.0,
                "description": "Single item - no color coordination needed"
            }
        
        # Count color types
        neutrals = [c for c in hex_colors if self.is_neutral(c)]
        bold_colors = [c for c in hex_colors if self.is_bold_color(c)]
        
        neutral_count = len(neutrals)
        bold_count = len(bold_colors)
        total = len(hex_colors)
        
        # Determine strategy
        if neutral_count == total:
            return {
                "strategy": "neutral_monochrome",
                "score": 0.88,
                "description": "Classic neutral palette - timeless and safe"
            }
        
        if neutral_count >= total - 1 and bold_count == 1:
            return {
                "strategy": "neutral_plus_accent",
                "score": 0.95,
                "description": "Neutral base with one statement color - highly fashionable"
            }
        
        if neutral_count >= total - 2 and bold_count <= 2:
            return {
                "strategy": "neutral_base",
                "score": 0.90,
                "description": "Neutral foundation with accent colors"
            }
        
        # Check for monochromatic (same hue family)
        if self._is_monochromatic(hex_colors):
            return {
                "strategy": "monochromatic",
                "score": 0.88,
                "description": "Elegant single-color family with varied shades"
            }
        
        # Check for analogous
        if self._is_analogous(hex_colors):
            return {
                "strategy": "analogous",
                "score": 0.85,
                "description": "Harmonious adjacent colors - naturally pleasing"
            }
        
        # Check for complementary
        if self._has_complementary(hex_colors):
            return {
                "strategy": "complementary",
                "score": 0.80,
                "description": "Bold complementary contrast - eye-catching"
            }
        
        # Check for triadic
        if self._is_triadic(hex_colors):
            return {
                "strategy": "triadic",
                "score": 0.75,
                "description": "Vibrant triadic scheme - dynamic and bold"
            }
        
        # Default: mixed
        return {
            "strategy": "mixed",
            "score": 0.70,
            "description": "Eclectic color mix"
        }
    
    def _is_monochromatic(self, hex_colors: List[str]) -> bool:
        """Check if colors are monochromatic (same hue family)."""
        non_neutrals = [c for c in hex_colors if not self.is_neutral(c)]
        if len(non_neutrals) < 2:
            return False
        
        hues = [self.hex_to_hsl(c)[0] for c in non_neutrals]
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                if self.get_hue_difference(hues[i], hues[j]) > 20:
                    return False
        return True
    
    def _is_analogous(self, hex_colors: List[str]) -> bool:
        """Check if non-neutral colors are analogous."""
        non_neutrals = [c for c in hex_colors if not self.is_neutral(c)]
        if len(non_neutrals) < 2:
            return False
        
        hues = sorted([self.hex_to_hsl(c)[0] for c in non_neutrals])
        
        # Check if all hues fit within 60 degree range
        min_hue, max_hue = hues[0], hues[-1]
        hue_span = self.get_hue_difference(min_hue, max_hue)
        
        return hue_span <= 60
    
    def _has_complementary(self, hex_colors: List[str]) -> bool:
        """Check if there's a complementary pair."""
        non_neutrals = [c for c in hex_colors if not self.is_neutral(c)]
        
        for i in range(len(non_neutrals)):
            for j in range(i + 1, len(non_neutrals)):
                h1 = self.hex_to_hsl(non_neutrals[i])[0]
                h2 = self.hex_to_hsl(non_neutrals[j])[0]
                if abs(self.get_hue_difference(h1, h2) - 180) <= 30:
                    return True
        return False
    
    def _is_triadic(self, hex_colors: List[str]) -> bool:
        """Check if colors form a triadic scheme."""
        non_neutrals = [c for c in hex_colors if not self.is_neutral(c)]
        if len(non_neutrals) < 3:
            return False
        
        hues = [self.hex_to_hsl(c)[0] for c in non_neutrals[:3]]
        
        # Check if hues are roughly 120 degrees apart
        diffs = []
        for i in range(3):
            diff = self.get_hue_difference(hues[i], hues[(i + 1) % 3])
            diffs.append(diff)
        
        # Allow some tolerance
        return all(90 <= d <= 150 for d in diffs)
    
    def calculate_outfit_harmony(self, hex_colors: List[str]) -> Dict[str, Any]:
        """
        Calculate overall harmony score for a set of colors.
        Uses Goldilocks principle and fashion rules.
        """
        if len(hex_colors) < 2:
            return {"score": 1.0, "harmony": "excellent", "details": []}
        
        # Get outfit strategy analysis
        strategy_analysis = self.analyze_outfit_combination(hex_colors)
        
        # Calculate pairwise scores
        pair_scores = []
        pair_details = []
        
        for i in range(len(hex_colors)):
            for j in range(i + 1, len(hex_colors)):
                score = self.calculate_match_score(hex_colors[i], hex_colors[j])
                relationship = self.get_color_relationship(hex_colors[i], hex_colors[j])
                pair_scores.append(score)
                pair_details.append({
                    "color1": hex_colors[i],
                    "color2": hex_colors[j],
                    "relationship": relationship,
                    "score": round(score, 3)
                })
        
        # Base score from pairwise analysis
        avg_pair_score = sum(pair_scores) / len(pair_scores)
        
        # Apply fashion rules
        rule_adjustments = self._apply_fashion_rules(hex_colors)
        
        # Combine scores
        final_score = (
            avg_pair_score * 0.5 +           # Pairwise harmony
            strategy_analysis["score"] * 0.3 + # Strategy bonus
            rule_adjustments * 0.2             # Fashion rules
        )

        # Cap "safe but boring" outfits (Goldilocks: moderate coordination is best)
        if strategy_analysis["strategy"] == "neutral_monochrome":
            final_score = min(final_score, 0.90)  # Max 90% for all-neutral

        # Determine harmony level
        if final_score >= 0.85:
            harmony = "excellent"
        elif final_score >= 0.70:
            harmony = "good"
        elif final_score >= 0.55:
            harmony = "acceptable"
        else:
            harmony = "poor"
        
        return {
            "score": round(final_score, 2),
            "harmony": harmony,
            "strategy": strategy_analysis["strategy"],
            "strategy_description": strategy_analysis["description"],
            "details": pair_details
        }
    
    def _apply_fashion_rules(self, hex_colors: List[str]) -> float:
        """
        Apply fashion rules and return adjustment score (0-1).
        """
        score = 0.7  # Base score
        
        neutrals = [c for c in hex_colors if self.is_neutral(c)]
        bold_colors = [c for c in hex_colors if self.is_bold_color(c)]
        
        # Rule 1: Neutral base is excellent
        if len(neutrals) >= len(hex_colors) * 0.5:
            score += 0.15
        
        # Rule 2: One accent color is ideal
        if len(bold_colors) == 1:
            score += 0.10
        
        # Rule 3: Too many bold colors is risky
        if len(bold_colors) > 2:
            score -= 0.10
        
        # Rule 4: Check temperature consistency
        temperatures = [self.get_color_temperature(c) for c in hex_colors if not self.is_neutral(c)]
        if temperatures:
            if all(t == temperatures[0] for t in temperatures):
                score += 0.05  # Consistent temperature
        
        # Rule 5: Avoid identical non-neutral colors
        non_neutrals = [c for c in hex_colors if not self.is_neutral(c)]
        for i in range(len(non_neutrals)):
            for j in range(i + 1, len(non_neutrals)):
                if self.get_color_relationship(non_neutrals[i], non_neutrals[j]) == "identical":
                    score -= 0.15  # Matchy-matchy penalty
        
        return max(0.0, min(1.0, score))
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def find_matching_colors(
        self, 
        target_hex: str, 
        candidate_hexes: List[str],
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find colors from candidates that match well with target.
        Returns sorted list by match score.
        """
        matches = []
        
        for hex_color in candidate_hexes:
            score = self.calculate_match_score(target_hex, hex_color)
            if score >= min_score:
                matches.append({
                    "hex": hex_color,
                    "score": round(score, 3),
                    "relationship": self.get_color_relationship(target_hex, hex_color)
                })
        
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches
    
    def suggest_complementary_colors(self, hex_color: str) -> Dict[str, str]:
        """
        Suggest complementary, analogous, and triadic colors.
        """
        h, s, l = self.hex_to_hsl(hex_color)
        
        return {
            "complementary": self.hsl_to_hex((h + 180) % 360, s, l),
            "analogous_1": self.hsl_to_hex((h + 30) % 360, s, l),
            "analogous_2": self.hsl_to_hex((h - 30) % 360, s, l),
            "triadic_1": self.hsl_to_hex((h + 120) % 360, s, l),
            "triadic_2": self.hsl_to_hex((h + 240) % 360, s, l),
            "split_comp_1": self.hsl_to_hex((h + 150) % 360, s, l),
            "split_comp_2": self.hsl_to_hex((h + 210) % 360, s, l),
        }
    
    def get_color_info(self, hex_color: str) -> Dict[str, Any]:
        """Get detailed information about a color."""
        h, s, l = self.hex_to_hsl(hex_color)
        
        return {
            "hex": hex_color,
            "hsl": {"hue": round(h, 1), "saturation": round(s, 3), "lightness": round(l, 3)},
            "category": self.get_color_category(hex_color),
            "temperature": self.get_color_temperature(hex_color),
            "is_neutral": self.is_neutral(hex_color),
            "is_bold": self.is_bold_color(hex_color),
        }


# Global instance
color_matcher = ColorMatcher()