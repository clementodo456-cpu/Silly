import logging
import traceback
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import config
from handlers.start import start_command, about_callback
from handlers.help import help_command
from handlers.conversion import (
    prompt_upload_callback,
    handle_image_message,
    handle_non_image_message,
    process_conversion_callback,
    cancel_callback,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catches unhandled exceptions globally, preventing process crashes and notifying the user."""
    logger.error("Unhandled exception occurred:", exc_info=context.error)

    if isinstance(update, Update):
        user_text = (
            "⚠️ <b>An unexpected error occurred.</b>\n\n"
            "Please try sending your image again or reset the process using /start."
        )
        try:
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    user_text, parse_mode="HTML"
                )
            elif update.message:
                await update.message.reply_text(user_text, parse_mode="HTML")
        except Exception as notify_err:
            logger.error(f"Failed to send error message to user: {notify_err}")


def main() -> None:
    """Entry point to run the bot as a Render Background Worker using long-polling."""
    logger.info("Initializing Telegram Image Format Converter Bot (Background Worker Mode)...")

    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .build()
    )

    # Attach global exception handling
    application.add_error_handler(global_error_handler)

    # Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("cancel", cancel_callback))

    # Navigation Callback Handlers
    application.add_handler(CallbackQueryHandler(start_command, pattern="^nav_start$"))
    application.add_handler(CallbackQueryHandler(prompt_upload_callback, pattern="^nav_convert$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^nav_help$"))
    application.add_handler(CallbackQueryHandler(about_callback, pattern="^nav_about$"))
    application.add_handler(CallbackQueryHandler(cancel_callback, pattern="^nav_cancel$"))

    # Conversion Format Callback Handlers (JPG, PNG, WEBP, GIF, BMP, TIFF)
    application.add_handler(CallbackQueryHandler(process_conversion_callback, pattern="^fmt_"))

    # Photo & Image Document Message Handlers
    image_filter = filters.PHOTO | filters.Document.IMAGE
    application.add_handler(MessageHandler(image_filter, handle_image_message))

    # Non-Image File Filter
    application.add_handler(
        MessageHandler(filters.Document.ALL & ~filters.Document.IMAGE, handle_non_image_message)
    )

    logger.info("Starting Telegram bot long-polling loop...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
