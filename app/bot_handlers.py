import asyncio
import logging
import re
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from . import config
from .downloader import cleanup_file, download_video, file_size_mb
from .status_tracker import tracker

logger = logging.getLogger(__name__)

URL_REGEX = re.compile(r"https?://\S+")


def extract_url(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    match = URL_REGEX.search(text)
    return match.group(0) if match else None


def is_authorized(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id in config.ALLOWED_USER_IDS)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text(config.UNAUTHORIZED_MESSAGE)
        return

    message = config.WELCOME_MESSAGE.format(max_mb=config.MAX_FILE_SIZE_MB)
    await update.message.reply_text(message)


async def _download(url: str) -> Optional[Path]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, download_video, url, config.DOWNLOAD_DIR)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not is_authorized(update):
        await update.message.reply_text(config.UNAUTHORIZED_MESSAGE)
        return

    url = extract_url(update.message.text)
    if not url:
        await update.message.reply_text(config.INVALID_URL_MESSAGE)
        return

    await update.message.reply_text(config.DOWNLOADING_MESSAGE)
    entry_id = await tracker.add(
        url=url,
        user_id=update.effective_user.id if update.effective_user else None,
        username=update.effective_user.username if update.effective_user else None,
        status="downloading",
        detail="In corso",
    )

    try:
        video_path = await _download(url)
        if not video_path or not video_path.exists():
            await update.message.reply_text(config.ERROR_MESSAGE)
            await tracker.update(entry_id, status="errore", detail="Download fallito")
            return

        size_mb = file_size_mb(video_path)
        if size_mb > config.MAX_FILE_SIZE_MB:
            await update.message.reply_text(
                config.FILE_TOO_LARGE_MESSAGE.format(max_mb=config.MAX_FILE_SIZE_MB)
            )
            cleanup_file(video_path)
            await tracker.update(
                entry_id, status="troppo grande", detail=f"{size_mb:.1f} MB"
            )
            return

        caption = f"Ecco il tuo video (circa {size_mb:.1f} MB)"
        try:
            with video_path.open("rb") as file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=file,
                    caption=caption,
                )
            await tracker.update(entry_id, status="inviato", detail=f"{size_mb:.1f} MB")
        except Exception:
            logger.exception("Invio video fallito, provo come documento")
            try:
                with video_path.open("rb") as file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        caption=caption,
                    )
                await tracker.update(
                    entry_id, status="inviato come documento", detail=f"{size_mb:.1f} MB"
                )
            except Exception:
                logger.exception("Errore durante l'invio del file")
                await update.message.reply_text(config.ERROR_MESSAGE)
                await tracker.update(entry_id, status="errore", detail="Invio fallito")
                return
        finally:
            cleanup_file(video_path)

    except Exception:
        logger.exception("Errore generale durante la gestione del messaggio")
        await tracker.update(entry_id, status="errore", detail="Eccezione imprevista")
        await update.message.reply_text(config.ERROR_MESSAGE)
