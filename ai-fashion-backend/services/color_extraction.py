"""
Color Extraction Service
Uses K-Means clustering to extract dominant colors from clothing images.
Includes HSL conversion for color matching.
"""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter
from typing import List, Dict, Any, Tuple
import colorsys


# =============================================================================
# FASHION COLOR NAME MAPPING
# =============================================================================

FASHION_COLORS = {
    # Neutrals
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "charcoal": (54, 69, 79),
    "ivory": (255, 255, 240),
    "cream": (255, 253, 208),
    "beige": (245, 245, 220),
    "tan": (210, 180, 140),
    "brown": (139, 69, 19),
    "chocolate": (123, 63, 0),
    "camel": (193, 154, 107),
    "taupe": (72, 60, 50),
    
    # Blues
    "navy": (0, 0, 128),
    "royal blue": (65, 105, 225),
    "sky blue": (135, 206, 235),
    "baby blue": (137, 207, 240),
    "teal": (0, 128, 128),
    "turquoise": (64, 224, 208),
    "cobalt": (0, 71, 171),
    "denim": (21, 96, 189),
    "powder blue": (176, 224, 230),
    
    # Reds
    "red": (255, 0, 0),
    "burgundy": (128, 0, 32),
    "maroon": (128, 0, 0),
    "wine": (114, 47, 55),
    "crimson": (220, 20, 60),
    "coral": (255, 127, 80),
    "salmon": (250, 128, 114),
    "rust": (183, 65, 14),
    "brick": (203, 65, 84),
    
    # Pinks
    "pink": (255, 192, 203),
    "hot pink": (255, 105, 180),
    "blush": (222, 93, 131),
    "rose": (255, 0, 127),
    "magenta": (255, 0, 255),
    "fuchsia": (255, 0, 128),
    "dusty rose": (194, 134, 141),
    
    # Greens
    "green": (0, 128, 0),
    "olive": (128, 128, 0),
    "forest green": (34, 139, 34),
    "sage": (188, 184, 138),
    "mint": (152, 255, 152),
    "emerald": (80, 200, 120),
    "hunter green": (53, 94, 59),
    "army green": (75, 83, 32),
    "lime": (50, 205, 50),
    
    # Yellows & Oranges
    "yellow": (255, 255, 0),
    "mustard": (255, 219, 88),
    "gold": (255, 215, 0),
    "orange": (255, 165, 0),
    "peach": (255, 218, 185),
    "apricot": (251, 206, 177),
    "tangerine": (255, 168, 18),
    
    # Purples
    "purple": (128, 0, 128),
    "lavender": (230, 230, 250),
    "lilac": (200, 162, 200),
    "plum": (142, 69, 133),
    "violet": (238, 130, 238),
    "mauve": (224, 176, 255),
    "eggplant": (97, 64, 81),
    
    # Metallics
    "silver": (192, 192, 192),
    "champagne": (247, 231, 206),
}


class ColorExtractor:
    """
    Extracts dominant colors from images using K-Means clustering.
    Provides colors in RGB, HEX, and HSL formats.
    """
    
    def __init__(self):
        # Precompute fashion color arrays for fast matching
        self.color_names = list(FASHION_COLORS.keys())
        self.color_values = np.array(list(FASHION_COLORS.values()))
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string."""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex string to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hsl(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """
        Convert RGB to HSL color space.
        Returns (hue, saturation, lightness) where:
        - hue: 0-360 degrees
        - saturation: 0-1
        - lightness: 0-1
        """
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s, l)  # Convert hue to degrees
    
    def _get_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """Find the closest fashion color name for an RGB value."""
        rgb_array = np.array(rgb)
        distances = np.sqrt(np.sum((self.color_values - rgb_array) ** 2, axis=1))
        closest_idx = np.argmin(distances)
        return self.color_names[closest_idx]
    
    def _is_background_color(self, rgb: Tuple[int, int, int], threshold: int = 30) -> bool:
        """Check if color is likely a background (white/near-white or black)."""
        # Check for white/near-white
        if all(c > 240 for c in rgb):
            return True
        # Check for black/near-black
        if all(c < 15 for c in rgb):
            return True
        return False
    
    def extract_colors(
        self, 
        image_path: str, 
        n_colors: int = 5,
        filter_background: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract dominant colors from an image using K-Means clustering.
        
        Args:
            image_path: Path to the image file
            n_colors: Number of color clusters (default 5)
            filter_background: Whether to filter out white/black backgrounds
            
        Returns:
            List of color dictionaries with hex, rgb, hsl, name, and percentage
        """
        try:
            # 1. Load and prepare image
            img = Image.open(image_path).convert("RGB")
            img.thumbnail((150, 150))  # Resize for faster processing
            
            # 2. Convert to numpy array and reshape
            pixels = np.array(img)
            pixels = pixels.reshape(-1, 3)  # Shape: (N, 3)
            
            # 3. Filter out background colors if enabled
            if filter_background:
                mask = ~np.apply_along_axis(
                    lambda rgb: self._is_background_color(tuple(rgb)), 
                    1, 
                    pixels
                )
                pixels = pixels[mask]
                
                # If too few pixels remain, use original
                if len(pixels) < 100:
                    img = Image.open(image_path).convert("RGB")
                    img.thumbnail((150, 150))
                    pixels = np.array(img).reshape(-1, 3)
            
            # 4. Apply K-Means clustering
            kmeans = KMeans(
                n_clusters=min(n_colors, len(pixels)),
                random_state=42,
                n_init=10,
                max_iter=300
            )
            kmeans.fit(pixels)
            
            # 5. Get cluster centers and counts
            cluster_centers = kmeans.cluster_centers_
            label_counts = Counter(kmeans.labels_)
            total_pixels = len(pixels)
            
            # 6. Build results sorted by dominance
            colors = []
            sorted_clusters = sorted(
                label_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for cluster_idx, pixel_count in sorted_clusters:
                rgb = tuple(int(c) for c in cluster_centers[cluster_idx])
                
                # Skip background colors in results
                if filter_background and self._is_background_color(rgb):
                    continue
                
                percentage = (pixel_count / total_pixels) * 100
                hsl = self._rgb_to_hsl(rgb)
                
                colors.append({
                    "hex": self._rgb_to_hex(rgb),
                    "rgb": list(rgb),
                    "hsl": {
                        "h": round(hsl[0], 1),
                        "s": round(hsl[1], 3),
                        "l": round(hsl[2], 3)
                    },
                    "name": self._get_color_name(rgb),
                    "percentage": round(percentage, 2)
                })
                
                # Return top 3 colors
                if len(colors) >= 3:
                    break
            
            return colors
            
        except Exception as e:
            print(f"Error extracting colors: {e}")
            return []
    
    def get_primary_and_secondary(
        self, 
        image_path: str
    ) -> Tuple[str, str]:
        """
        Get just the primary and secondary hex colors.
        Used for storing in database.
        
        Returns:
            Tuple of (primary_hex, secondary_hex)
        """
        colors = self.extract_colors(image_path)
        
        primary = colors[0]["hex"] if len(colors) > 0 else None
        secondary = colors[1]["hex"] if len(colors) > 1 else None
        
        return primary, secondary


# Global instance
color_extractor = ColorExtractor()