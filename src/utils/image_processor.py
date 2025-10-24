"""
Image Processor for VLM
Handles image validation and preprocessing for Vision Language Models
"""

import os
from pathlib import Path
from typing import Tuple
from PIL import Image


def validate_image(image_path: str, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate image file
    
    Args:
        image_path: Path to image
        max_size_mb: Maximum file size in MB
        
    Returns:
        (is_valid, error_message)
    """
    if not os.path.exists(image_path):
        return False, "File does not exist"
    
    ext = Path(image_path).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        return False, f"Unsupported format: {ext}"
    
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File too large: {file_size_mb:.2f}MB (max: {max_size_mb}MB)"
    
    return True, "Valid"


def convert_pdf_to_image(pdf_path: str, output_path: str = None) -> str:
    """
    Convert PDF first page to image for VLM processing
    
    Args:
        pdf_path: Path to PDF
        output_path: Output path (optional)
        
    Returns:
        Path to converted image
    """
    try:
        from pdf2image import convert_from_path
        
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        
        if not images:
            raise ValueError("Could not extract image from PDF")
        
        if output_path is None:
            output_path = pdf_path.rsplit('.', 1)[0] + '_converted.png'
        
        images[0].save(output_path, 'PNG')
        return output_path
        
    except ImportError:
        raise ImportError(
            "pdf2image required for PDF processing. "
            "Install with: pip install pdf2image"
        )
    except Exception as e:
        raise Exception(f"PDF conversion failed: {str(e)}")


def preprocess_image(image_path: str, output_path: str = None) -> str:
    """
    Preprocess image for VLM (minimal processing)
    - Resize if too large
    - Convert to RGB
    
    Args:
        image_path: Input image path
        output_path: Output path (optional)
        
    Returns:
        Path to processed image
    """
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Resize if too large (VLMs work best with reasonable sizes)
        max_dimension = 2048
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_processed{ext}"
        
        img.save(output_path, quality=95)
        return output_path
        
    except Exception as e:
        print(f"Preprocessing failed: {e}. Using original.")
        return image_path


def prepare_image_for_vlm(image_path: str) -> Tuple[str, dict]:
    """
    Complete image preparation pipeline for VLM processing
    
    Args:
        image_path: Input image path
        
    Returns:
        (processed_image_path, metadata)
    """
    metadata = {
        "original_path": image_path,
        "converted_from_pdf": False,
        "preprocessed": False,
        "validation_passed": False
    }
    
    # Validate
    is_valid, error_msg = validate_image(image_path)
    if not is_valid:
        raise ValueError(f"Image validation failed: {error_msg}")
    
    metadata["validation_passed"] = True
    
    # Convert PDF if needed
    if image_path.lower().endswith('.pdf'):
        try:
            image_path = convert_pdf_to_image(image_path)
            metadata["converted_from_pdf"] = True
            metadata["converted_path"] = image_path
        except Exception as e:
            raise Exception(f"PDF conversion failed: {str(e)}")
    
    # Preprocess
    try:
        processed_path = preprocess_image(image_path)
        metadata["preprocessed"] = True
        metadata["processed_path"] = processed_path
    except Exception as e:
        print(f"Preprocessing failed, using original: {e}")
        processed_path = image_path
    
    # Get image info
    try:
        img = Image.open(processed_path)
        metadata["image_info"] = {
            "format": img.format,
            "size": img.size,
            "mode": img.mode
        }
    except:
        pass
    
    return processed_path, metadata