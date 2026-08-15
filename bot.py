import logging
from aiohttp import web
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def health_check(request: web.Request) -> web.Response:
    """Minimal HTTP response endpoint for Render Web Service health checks."""
    return web.Response(text="Telegram Image Converter Bot is active.", status=200)

async def start_health_server(port: int) -> None:
    """Starts background HTTP health server."""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP server bound to 0.0.0.0:{port}")

async def post_init(application: Application) -> None:
    """Executes after application initialization to attach the health server."""
    await start_health_server(config.PORT)

def main() -> None:
    """Entry point to run the bot using long-polling."""
    logger.info("Initializing Telegram Image Format Converter Bot...")

    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Command Registration
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("cancel", cancel_callback))

    # Navigation Callbacks
    application.add_handler(CallbackQueryHandler(start_command, pattern="^nav_start$"))
    application.add_handler(CallbackQueryHandler(prompt_upload_callback, pattern="^nav_convert$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^nav_help$"))
    application.add_handler(CallbackQueryHandler(about_callback, pattern="^nav_about$"))
    application.add_handler(CallbackQueryHandler(cancel_callback, pattern="^nav_cancel$"))

    # Format Callbacks
    application.add_handler(CallbackQueryHandler(process_conversion_callback, pattern="^fmt_"))

    # Image Message Handling
    image_filter = filters.PHOTO | filters.Document.IMAGE
    application.add_handler(MessageHandler(image_filter, handle_image_message))

    # Non-image Document Handler
    application.add_handler(
        MessageHandler(filters.Document.ALL & ~filters.Document.IMAGE, handle_non_image_message)
    )

    logger.info("Starting Telegram bot polling loop...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
