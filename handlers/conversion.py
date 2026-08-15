import os
import uuid
import logging
from PIL import Image

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, TEMP_DIR
from utils.image_converter import convert_image
from utils.cleanup import cleanup_user_context, safe_remove_file

logger = logging.getLogger(__name__)

def get_format_keyboard() -> InlineKeyboardMarkup:
    """Returns format selection inline buttons grid."""
    keyboard = [
        [
            InlineKeyboardButton("JPG", callback_data="fmt_JPG"),
            InlineKeyboardButton("PNG", callback_data="fmt_PNG"),
            InlineKeyboardButton("WEBP", callback_data="fmt_WEBP"),
        ],
        [
            InlineKeyboardButton("GIF", callback_data="fmt_GIF"),
            InlineKeyboardButton("BMP", callback_data="fmt_BMP"),
            InlineKeyboardButton("TIFF", callback_data="fmt_TIFF"),
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="nav_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def prompt_upload_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompts user to upload an image."""
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_image"] = True

    prompt_text = (
        "📤 <b>Upload Your Image</b>\n\n"
        "Send an image as a compressed Telegram photo or an uncompressed document attachment.\n\n"
        f"<i>Maximum size limit: {MAX_FILE_SIZE_MB} MB</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="nav_cancel")]
    ])

    await query.edit_message_text(
        prompt_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

async def handle_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes photo or document image sent by the user."""
    message = update.message
    if not message:
        return

    document = message.document
    photo = message.photo[-1] if message.photo else None

    if not photo and not document:
        return

    file_size = photo.file_size if photo else (document.file_size if document else 0)
    if file_size > MAX_FILE_SIZE_BYTES:
        await message.reply_text(
            f"⚠️ <b>File Exceeds Limit!</b>\n\nYour file is {file_size / (1024 * 1024):.1f} MB. "
            f"The maximum allowed size is <b>{MAX_FILE_SIZE_MB} MB</b>.",
            parse_mode=ParseMode.HTML,
        )
        return

    status_msg = await message.reply_text("📥 <i>Downloading image...</i>", parse_mode=ParseMode.HTML)

    cleanup_user_context(context.user_data)

    unique_id = uuid.uuid4().hex[:8]
    original_name = document.file_name if document and document.file_name else f"image_{unique_id}"
    temp_input_path = os.path.join(TEMP_DIR, f"input_{unique_id}")

    try:
        tg_file = await (photo or document).get_file()
        await tg_file.download_to_drive(temp_input_path)

        with Image.open(temp_input_path) as img:
            img.verify()
            with Image.open(temp_input_path) as img_read:
                detected_format = img_read.format or "UNKNOWN"

        context.user_data["input_file_path"] = temp_input_path
        context.user_data["original_format"] = detected_format
        context.user_data["original_filename"] = original_name
        context.user_data["awaiting_image"] = False

        select_text = (
            f"📥 <b>Image Received!</b>\n\n"
            f"• <b>Format:</b> <code>{detected_format}</code>\n"
            f"• <b>Size:</b> {file_size / 1024:.1f} KB\n\n"
            "🎯 Choose the output format you want to convert to:"
        )

        await status_msg.edit_text(
            select_text,
            reply_markup=get_format_keyboard(),
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        logger.error(f"Failed to process image upload: {e}", exc_info=True)
        safe_remove_file(temp_input_path)
        cleanup_user_context(context.user_data)
        await status_msg.edit_text(
            "❌ <b>Invalid or Corrupted Image</b>\n\n"
            "Could not decode the uploaded file as a valid image. Please send a valid image file.",
            parse_mode=ParseMode.HTML,
        )

async def handle_non_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rejects non-image document uploads."""
    if context.user_data.get("awaiting_image"):
        await update.message.reply_text(
            "⚠️ <b>Unsupported File Type!</b>\n\n"
            "Please send a valid image format (JPG, PNG, WEBP, GIF, BMP, or TIFF).",
            parse_mode=ParseMode.HTML,
        )

async def process_conversion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes the conversion process upon format button selection."""
    query = update.callback_query
    await query.answer()

    target_fmt = query.data.replace("fmt_", "")
    input_path = context.user_data.get("input_file_path")
    orig_fmt = context.user_data.get("original_format", "UNKNOWN")

    if not input_path or not os.path.exists(input_path):
        await query.edit_message_text(
            "⚠️ <b>Session Expired!</b>\n\nPlease send a new image to start converting.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🖼️ Convert Image", callback_data="nav_convert")]
            ]),
            parse_mode=ParseMode.HTML,
        )
        return

    await query.edit_message_text(
        f"⌛ <b>Converting image to {target_fmt}...</b>\nPlease wait standard processing time.",
        parse_mode=ParseMode.HTML,
    )

    output_path = None
    try:
        output_path = convert_image(input_path, target_fmt, TEMP_DIR)
        context.user_data["output_file_path"] = output_path

        summary_caption = (
            f"✅ <b>Conversion Complete!</b>\n\n"
            f"• <b>Original Format:</b> <code>{orig_fmt}</code>\n"
            f"• <b>Converted Format:</b> <code>{target_fmt}</code>"
        )

        completion_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Convert Another", callback_data="nav_convert"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="nav_start"),
            ]
        ])

        with open(output_path, "rb") as converted_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=converted_file,
                filename=f"converted.{target_fmt.lower()}",
                caption=summary_caption,
                reply_markup=completion_keyboard,
                parse_mode=ParseMode.HTML,
            )

        try:
            await query.message.delete()
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error converting image to {target_fmt}: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ <b>Conversion Error!</b>\n\nAn issue occurred while converting to {target_fmt}. "
            "Please try selecting another format.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Try Again", callback_data="nav_convert")]
            ]),
            parse_mode=ParseMode.HTML,
        )
    finally:
        cleanup_user_context(context.user_data)

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancels active conversion session."""
    cleanup_user_context(context.user_data)

    cancel_text = "❌ <b>Operation cancelled.</b> Send /start to begin again."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_start")]
    ])

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            cancel_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    elif update.message:
        await update.message.reply_text(
            cancel_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
