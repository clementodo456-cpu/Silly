import os
import uuid
import logging
from PIL import Image

logger = logging.getLogger(__name__)

FORMAT_MAP = {
    "JPG": ("JPEG", ".jpg"),
    "JPEG": ("JPEG", ".jpg"),
    "PNG": ("PNG", ".png"),
    "WEBP": ("WEBP", ".webp"),
    "GIF": ("GIF", ".gif"),
    "BMP": ("BMP", ".bmp"),
    "TIFF": ("TIFF", ".tiff"),
}

def convert_image(input_path: str, target_format: str, output_dir: str) -> str:
    """
    Converts an image file to the target format using Pillow.
    Handles transparency gracefully by flattening RGBA to white background for JPG/BMP.
    """
    target_format_upper = target_format.upper()
    if target_format_upper not in FORMAT_MAP:
        raise ValueError(f"Unsupported format requested: {target_format}")

    pil_format, ext = FORMAT_MAP[target_format_upper]
    unique_id = uuid.uuid4().hex[:8]
    output_filename = f"converted_{unique_id}{ext}"
    output_path = os.path.join(output_dir, output_filename)

    logger.info(f"Converting image {input_path} -> {pil_format}")

    with Image.open(input_path) as img:
        # Check if requested format does not support transparency
        if pil_format in ("JPEG", "BMP"):
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                rgba_img = img.convert("RGBA")
                background = Image.new("RGB", rgba_img.size, (255, 255, 255))
                background.paste(rgba_img, mask=rgba_img.split()[3])
                save_img = background
            else:
                save_img = img.convert("RGB")
        else:
            save_img = img

        save_kwargs = {}
        if pil_format == "JPEG":
            save_kwargs.update({"quality": 95, "optimize": True})
        elif pil_format == "WEBP":
            save_kwargs.update({"quality": 95, "method": 6})
        elif pil_format == "PNG":
            save_kwargs.update({"optimize": True})

        save_img.save(output_path, format=pil_format, **save_kwargs)

    logger.info(f"Conversion complete: {output_path}")
    return output_path
