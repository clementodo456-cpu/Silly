import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.cleanup import cleanup_user_context

logger = logging.getLogger(__name__)

def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🖼️ Convert Image", callback_data="nav_convert")],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="nav_help"),
            InlineKeyboardButton("💬 About", callback_data="nav_about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start command and returns to main menu."""
    cleanup_user_context(context.user_data)
    welcome_text = (
        "🖼️ <b>Image Format Converter</b> (@sillysistbot)\n\n"
        "Convert your images between <b>JPG, PNG, WEBP, GIF, BMP,</b> and <b>TIFF</b> formats quickly and easily.\n\n"
        "📤 Send me an image directly or tap <b>Convert Image</b> below to get started!"
    )

    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_start_keyboard(),
            parse_mode=ParseMode.HTML,
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=get_start_keyboard(),
            parse_mode=ParseMode.HTML,
        )

async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays information about the bot."""
    query = update.callback_query
    await query.answer()

    about_text = (
        "💬 <b>About Image Converter Bot</b>\n\n"
        "This bot provides fast, secure image format conversions directly inside Telegram.\n\n"
        "✨ <b>Key Features:</b>\n"
        "• Automatic background blending for transparent JPG conversion\n"
        "• Handles compressed Photos and original File Documents\n"
        "• Immediate temporary file destruction for privacy\n"
        "• Powered by Python & Pillow\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼️ Convert Image", callback_data="nav_convert")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_start")],
    ])

    await query.edit_message_text(
        about_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
