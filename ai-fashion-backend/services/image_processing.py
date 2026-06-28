"""
Image Processing Service
Handles background removal using rembg/U2Net and image manipulation.
"""

import os
import uuid
from PIL import Image
from rembg import remove
from io import BytesIO
from typing import Tuple


class ImageProcessor:
    """
    Handles all image processing operations:
    - Background removal using U2Net
    - Adding white background
    - Resizing and compression
    """
    
    # Directories
    UPLOAD_DIR = "uploads"
    ORIGINAL_DIR = os.path.join(UPLOAD_DIR, "original")
    PROCESSED_DIR = os.path.join(UPLOAD_DIR, "processed")
    
    # Max image size
    MAX_SIZE = (800, 800)
    
    def __init__(self):
        """Initialize and create directories if needed."""
        for directory in [self.ORIGINAL_DIR, self.PROCESSED_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def save_original(self, file_content: bytes, filename: str) -> str:
        """
        Save the original uploaded image.
        
        Args:
            file_content: Raw bytes from upload
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            ext = "jpg"
        unique_name = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(self.ORIGINAL_DIR, unique_name)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(file_content)
        
        return filepath
    
    def remove_background(self, image_path: str) -> str:
        """
        Remove background from clothing image using U2Net.
        
        Args:
            image_path: Path to original image
            
        Returns:
            Path to processed image with white background
        """
        # 1. Read original image
        with open(image_path, "rb") as f:
            input_image = f.read()
        
        # 2. Remove background using rembg (U2Net model)
        # Returns image with transparent background
        output_image = remove(input_image)
        
        # 3. Convert to PIL Image
        img = Image.open(BytesIO(output_image))
        
        # 4. Add white background
        if img.mode == "RGBA":
            # Create white background
            white_bg = Image.new("RGB", img.size, (255, 255, 255))
            # Paste image using alpha channel as mask
            white_bg.paste(img, mask=img.split()[3])
            img = white_bg
        else:
            img = img.convert("RGB")
        
        # 5. Resize if too large (maintain aspect ratio)
        img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)
        
        # 6. Save processed image
        base_name = os.path.basename(image_path).rsplit(".", 1)[0]
        processed_filename = f"{base_name}_processed.png"
        processed_path = os.path.join(self.PROCESSED_DIR, processed_filename)
        
        img.save(processed_path, "PNG", quality=95)
        
        return processed_path
    
    def process_image(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """
        Complete image processing pipeline.
        
        Args:
            file_content: Raw bytes from upload
            filename: Original filename
            
        Returns:
            Tuple of (original_path, processed_path)
        """
        # Save original
        original_path = self.save_original(file_content, filename)
        
        # Remove background and save processed
        processed_path = self.remove_background(original_path)
        
        return original_path, processed_path
    
    def delete_images(self, original_path: str, processed_path: str):
        """Delete both original and processed images."""
        for path in [original_path, processed_path]:
            if path and os.path.exists(path):
                os.remove(path)


# Global instance
image_processor = ImageProcessor()