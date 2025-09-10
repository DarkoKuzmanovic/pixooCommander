#!/usr/bin/env python3
"""
Scene preview renderer for NiceGUI web UI.

This module provides functions to render small preview images for scene objects
that were previously rendered with Qt. The previews are 64x64 PNG images that
can be displayed in the web UI via data URIs.
"""

import asyncio
import base64
import logging
from typing import Any, Union
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not available - preview functionality will be limited")

logger = logging.getLogger(__name__)


def render_scene_preview(scene: Any, size: tuple = (64, 64)) -> bytes:
    """
    Synchronously render a 64x64 PNG preview for the given scene object.

    Args:
        scene: A scene object with various possible attributes
        size: Tuple of (width, height) for the preview image

    Returns:
        bytes: PNG image data as bytes

    The function supports:
    - Text-like scenes: if hasattr(scene, 'text') or getattr(scene, 'type', '') == 'text'
    - Image-like scenes: if hasattr(scene, 'image') or hasattr(scene, 'image_path')
    - Fallback: simple placeholder for other scene types
    """
    if not PIL_AVAILABLE:
        # Return a simple placeholder if PIL is not available
        return _create_placeholder_image(size, "No PIL")

    try:
        width, height = size

        # Create a new image with a dark background
        img = Image.new('RGB', (width, height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)

        # Check if it's a text-like scene
        if _is_text_scene(scene):
            return _render_text_scene(scene, img, draw, size)

        # Check if it's an image-like scene
        elif _is_image_scene(scene):
            return _render_image_scene(scene, img, draw, size)

        # Fallback to a generic placeholder
        else:
            scene_type = getattr(scene, 'type', 'Unknown')
            return _create_placeholder_image(size, f"{scene_type}")

    except Exception as e:
        logger.error(f"Error rendering scene preview: {e}", exc_info=True)
        # Return a fallback placeholder on any error
        return _create_placeholder_image(size, "Error")


async def async_render_scene_preview(scene: Any, size: tuple = (64, 64)) -> str:
    """
    Asynchronously render a scene preview and return as a data URI.

    This function runs the synchronous renderer in a thread to avoid blocking
    the event loop, then converts the result to a data URI.

    Args:
        scene: A scene object with various possible attributes
        size: Tuple of (width, height) for the preview image

    Returns:
        str: PNG data URI string ready for NiceGUI's ui.image()
    """
    # Run the synchronous renderer in a thread to avoid blocking
    png_bytes = await asyncio.to_thread(render_scene_preview, scene, size)

    # Convert to data URI
    encoded = base64.b64encode(png_bytes).decode('utf-8')
    return f"data:image/png;base64,{encoded}"


def _is_text_scene(scene: Any) -> bool:
    """Determine if a scene is text-like."""
    return (hasattr(scene, 'text') or
            getattr(scene, 'type', '') == 'text' or
            (hasattr(scene, 'config') and isinstance(getattr(scene, 'config', {}), dict) and
             ('text' in scene.config or 'lines' in scene.config)))


def _is_image_scene(scene: Any) -> bool:
    """Determine if a scene is image-like."""
    return (hasattr(scene, 'image') or
            hasattr(scene, 'image_path') or
            (hasattr(scene, 'config') and isinstance(getattr(scene, 'config', {}), dict) and
             'path' in scene.config))


def _render_text_scene(scene: Any, img: Image.Image, draw: ImageDraw.Draw, size: tuple) -> bytes:
    """Render a text-like scene."""
    width, height = size

    # Extract text from the scene
    text = ""
    if hasattr(scene, 'text'):
        text = str(scene.text)
    elif hasattr(scene, 'config') and isinstance(getattr(scene, 'config', {}), dict):
        # Try to get text from config
        if 'text' in scene.config:
            text = str(scene.config['text'])
        elif 'lines' in scene.config and scene.config['lines']:
            # For multi-line scenes, use the first line
            first_line = scene.config['lines'][0]
            if isinstance(first_line, dict) and 'text' in first_line:
                text = str(first_line['text'])
            elif isinstance(first_line, str):
                text = first_line

    if not text:
        text = "Text"

    # Try to load a font, fallback to default if needed
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()

    # Scale font to fit if needed
    try:
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # If text is too wide, try a smaller font
        if text_width > width * 0.9:
            try:
                small_font = ImageFont.truetype("arial.ttf", 8)
            except:
                try:
                    small_font = ImageFont.truetype("DejaVuSans.ttf", 8)
                except:
                    small_font = ImageFont.load_default()

            # Check if smaller font fits better
            small_bbox = draw.textbbox((0, 0), text, font=small_font)
            small_width = small_bbox[2] - small_bbox[0]
            if small_width < width * 0.9:
                font = small_font
                text_width = small_width
                text_height = small_bbox[3] - small_bbox[1]
    except:
        # If we can't measure text, use default sizing
        pass

    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = max(0, (width - text_width) // 2)
    y = max(0, (height - text_height) // 2)

    # Draw text with a light color
    draw.text((x, y), text, fill=(220, 220, 220), font=font)

    # Save to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def _render_image_scene(scene: Any, img: Image.Image, draw: ImageDraw.Draw, size: tuple) -> bytes:
    """Render an image-like scene."""
    width, height = size

    try:
        # Try to get the image from the scene
        pil_image = None

        if hasattr(scene, 'image') and isinstance(scene.image, Image.Image):
            pil_image = scene.image
        elif hasattr(scene, 'image_path') and isinstance(scene.image_path, str):
            pil_image = Image.open(scene.image_path)
        elif hasattr(scene, 'config') and isinstance(getattr(scene, 'config', {}), dict):
            if 'path' in scene.config and isinstance(scene.config['path'], str):
                pil_image = Image.open(scene.config['path'])

        if pil_image:
            # Scale the image to fit within the preview size while maintaining aspect ratio
            pil_image.thumbnail((width, height), Image.Resampling.LANCZOS)

            # Calculate position to center the image
            img_width, img_height = pil_image.size
            x = (width - img_width) // 2
            y = (height - img_height) // 2

            # Paste the image onto our preview
            img.paste(pil_image, (x, y))
        else:
            # Fallback if we couldn't load an image
            return _create_placeholder_image(size, "Img?")

    except Exception as e:
        logger.error(f"Error loading image for preview: {e}", exc_info=True)
        # Fallback to placeholder on error
        return _create_placeholder_image(size, "Img!")

    # Save to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def _create_placeholder_image(size: tuple, label: str) -> bytes:
    """Create a simple placeholder image with a label."""
    width, height = size

    # Create image with a distinct background
    img = Image.new('RGB', (width, height), color=(60, 60, 80))
    draw = ImageDraw.Draw(img)

    # Try to get a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 10)
        except:
            font = ImageFont.load_default()

    # Center the label text
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = max(0, (width - text_width) // 2)
    y = max(0, (height - text_height) // 2)

    # Draw text
    draw.text((x, y), label, fill=(200, 200, 200), font=font)

    # Draw a border
    draw.rectangle([0, 0, width-1, height-1], outline=(100, 100, 120), width=1)

    # Save to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def _example_usage():
    """
    Example usage of the preview renderer functions.

    This function demonstrates how to create a dummy scene object and
    convert it to a data URI for use in NiceGUI.
    """
    # Create a simple dummy text scene
    class DummyTextScene:
        def __init__(self, text):
            self.type = 'text'
            self.text = text
            self.config = {'text': text}

    # Create a dummy image scene
    class DummyImageScene:
        def __init__(self, path=None):
            self.type = 'image'
            self.image_path = path
            self.config = {'path': path} if path else {}

    # Example 1: Text scene
    text_scene = DummyTextScene("Hello")
    text_preview_bytes = render_scene_preview(text_scene)
    print(f"Text preview size: {len(text_preview_bytes)} bytes")

    # Example 2: Image scene (would need a real image path to fully test)
    image_scene = DummyImageScene()
    image_preview_bytes = render_scene_preview(image_scene)
    print(f"Image preview size: {len(image_preview_bytes)} bytes")

    # Example 3: Async usage
    import asyncio

    async def async_example():
        data_uri = await async_render_scene_preview(text_scene)
        print(f"Data URI length: {len(data_uri)} characters")
        print(f"Data URI starts with: {data_uri[:50]}...")

    # Run the async example
    asyncio.run(async_example())


if __name__ == "__main__":
    _example_usage()