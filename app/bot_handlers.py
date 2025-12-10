import re
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from . import config
from .download_queue import DownloadJob, download_queue
from .status_tracker import tracker

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

    message = config.WELCOME_MESSAGE.format(max_mb=config.active_upload_limit_mb())
    await update.message.reply_text(message)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    if not is_authorized(update):
        await update.message.reply_text(config.UNAUTHORIZED_MESSAGE)
        return

    if not update.effective_chat:
        await update.message.reply_text(config.ERROR_MESSAGE)
        return

    url = extract_url(update.message.text)
    if not url:
        await update.message.reply_text(config.INVALID_URL_MESSAGE)
        return

    queued_position = download_queue.pending_jobs() + 1
    entry_id = await tracker.add(
        url=url,
        user_id=update.effective_user.id if update.effective_user else None,
        username=update.effective_user.username if update.effective_user else None,
        status="in coda",
        detail=f"In attesa (posizione {queued_position})",
    )
    await download_queue.enqueue(
        DownloadJob(
            entry_id=entry_id,
            url=url,
            chat_id=update.effective_chat.id if update.effective_chat else 0,
            user_id=update.effective_user.id if update.effective_user else None,
            username=update.effective_user.username if update.effective_user else None,
        ),
        bot=context.bot,
    )

    reply_message = config.DOWNLOADING_MESSAGE
    if queued_position > 1:
        reply_message = f"{config.DOWNLOADING_MESSAGE} (posizione in coda: {queued_position})"
    await update.message.reply_text(reply_message)
