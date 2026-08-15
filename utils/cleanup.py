import os
import logging

logger = logging.getLogger(__name__)

def safe_remove_file(filepath: str | None) -> None:
    """Safely delete a file from disk if it exists without throwing errors."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.debug(f"Successfully deleted temporary file: {filepath}")
        except Exception as e:
            logger.error(f"Error removing file {filepath}: {e}")

def cleanup_user_context(user_data: dict) -> None:
    """Removes temporary user files and resets context state keys."""
    input_path = user_data.get("input_file_path")
    output_path = user_data.get("output_file_path")

    safe_remove_file(input_path)
    safe_remove_file(output_path)

    user_data.pop("input_file_path", None)
    user_data.pop("output_file_path", None)
    user_data.pop("original_format", None)
    user_data.pop("original_filename", None)
    user_data.pop("awaiting_image", None)
