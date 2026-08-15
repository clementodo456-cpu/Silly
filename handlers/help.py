import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help command and displays usage information."""
    help_text = (
        "ℹ️ <b>How to Use Image Converter Bot</b>\n\n"
        "1️⃣ <b>Send an Image:</b> Send any photo or document image to this chat.\n"
        "2️⃣ <b>Select Target Format:</b> Pick from JPG, PNG, WEBP, GIF, BMP, or TIFF.\n"
        "3️⃣ <b>Download:</b> Get your converted file immediately!\n\n"
        "📌 <b>Supported Formats:</b>\n"
        "• <code>JPG / JPEG</code> (Auto-converts transparent areas to white)\n"
        "• <code>PNG</code> (Supports alpha channel transparency)\n"
        "• <code>WEBP</code> (Optimized web graphic format)\n"
        "• <code>GIF</code> (Graphics Interchange Format)\n"
        "• <code>BMP</code> (Uncompressed bitmap image)\n"
        "• <code>TIFF</code> (High quality raster image format)\n\n"
        "⚙️ <b>Limitations:</b>\n"
        f"• Max file size: <b>{MAX_FILE_SIZE_MB} MB</b>\n"
        "• All temporary files are cleaned up immediately."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼️ Convert Image", callback_data="nav_convert")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_start")],
    ])

    if update.message:
        await update.message.reply_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            help_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
