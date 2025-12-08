# pip install -r requirements.txt
# python -m app.main

import asyncio
import logging

import uvicorn
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from . import config
from .bot_handlers import handle_start, handle_text
from .logging_utils import log_buffer
from .web import create_web_app


def setup_logging() -> None:
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logging.basicConfig(level=log_level, handlers=[stream_handler])

    log_buffer.setFormatter(formatter)
    logging.getLogger().addHandler(log_buffer)


async def run_bot() -> None:
    builder = ApplicationBuilder().token(config.BOT_TOKEN)

    if config.TELEGRAM_BOT_API_ENABLED:
        builder = builder.base_url(config.TELEGRAM_BOT_API_BASE_URL).base_file_url(
            config.TELEGRAM_BOT_API_FILE_URL
        )

    application = builder.build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def run_web() -> None:
    app = create_web_app()
    config_uvicorn = uvicorn.Config(
        app,
        host=config.WEB_APP_HOST,
        port=config.WEB_APP_PORT,
        log_level=config.LOG_LEVEL.lower(),
        access_log=False,
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()


async def main_async() -> None:
    setup_logging()
    logging.info("Avvio bot e web GUI")
    await asyncio.gather(run_bot(), run_web())


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
