import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from telegram import Bot

from . import config
from .downloader import cleanup_file, download_video, file_size_mb
from .status_tracker import tracker

logger = logging.getLogger(__name__)


@dataclass
class DownloadJob:
    entry_id: int
    url: str
    chat_id: int
    user_id: Optional[int]
    username: Optional[str]


class DownloadQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[DownloadJob] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task[None]] = None
        self._bot: Optional[Bot] = None

    def pending_jobs(self) -> int:
        return self._queue.qsize()

    async def enqueue(self, job: DownloadJob, bot: Bot) -> None:
        await self._queue.put(job)
        if not self._bot:
            self._bot = bot
        await self._ensure_worker()

    async def _ensure_worker(self) -> None:
        if self._worker_task and not self._worker_task.done():
            return
        self._worker_task = asyncio.create_task(self._worker())

    async def _worker(self) -> None:
        while True:
            job = await self._queue.get()
            try:
                await self._process_job(job)
            except Exception:
                logger.exception("Errore durante l'elaborazione del job %s", job.entry_id)
            finally:
                self._queue.task_done()

    async def _process_job(self, job: DownloadJob) -> None:
        if not self._bot:
            logger.error("Nessun bot disponibile per elaborare il job")
            return

        await tracker.update(job.entry_id, status="downloading", detail="In corso")

        loop = asyncio.get_running_loop()
        video_path: Optional[Path]
        reused: bool
        video_path, reused = await loop.run_in_executor(
            None, download_video, job.url, config.DOWNLOAD_DIR, job.user_id, job.username
        )

        if not video_path or not video_path.exists():
            await tracker.update(job.entry_id, status="errore", detail="Download fallito")
            await self._bot.send_message(chat_id=job.chat_id, text=config.ERROR_MESSAGE)
            return

        if reused:
            await tracker.update(
                job.entry_id,
                status="downloading",
                detail=f"File già presente: {video_path.name}",
            )
            await self._bot.send_message(
                chat_id=job.chat_id,
                text=config.FILE_ALREADY_PRESENT_MESSAGE.format(filename=video_path.name),
            )

        size_mb = file_size_mb(video_path)
        max_upload_mb = config.active_upload_limit_mb()
        if size_mb > max_upload_mb:
            if config.TELEGRAM_BOT_API_ENABLED:
                await self._bot.send_message(
                    chat_id=job.chat_id,
                    text=config.FILE_TOO_LARGE_MESSAGE.format(max_mb=max_upload_mb),
                )
                detail = f"{size_mb:.1f} MB (> {max_upload_mb} MB con Bot API self-hosted)"
            else:
                await self._bot.send_message(
                    chat_id=job.chat_id,
                    text=config.FILE_TOO_LARGE_BOT_API_DISABLED.format(
                        size_gb=size_mb / 1024, max_mb=max_upload_mb
                    ),
                )
                detail = f"{size_mb:.1f} MB scaricati, limite {max_upload_mb} MB"
            if config.DELETE_AFTER_SEND:
                cleanup_file(video_path)
            else:
                logger.info("File conservato perché DELETE_AFTER_SEND=False: %s", video_path)
            await tracker.update(job.entry_id, status="troppo grande", detail=detail)
            return

        caption = f"Ecco il tuo video (circa {size_mb:.1f} MB)"
        detail_suffix = f"{size_mb:.1f} MB" + (" (riutilizzato)" if reused else "")
        try:
            with video_path.open("rb") as file:
                await self._bot.send_video(
                    chat_id=job.chat_id,
                    video=file,
                    caption=caption,
                )
            await tracker.update(job.entry_id, status="inviato", detail=detail_suffix)
        except Exception:
            logger.exception("Invio video fallito, provo come documento")
            try:
                with video_path.open("rb") as file:
                    await self._bot.send_document(
                        chat_id=job.chat_id,
                        document=file,
                        caption=caption,
                    )
                await tracker.update(
                    job.entry_id, status="inviato come documento", detail=detail_suffix
                )
            except Exception:
                logger.exception("Errore durante l'invio del file")
                await self._bot.send_message(chat_id=job.chat_id, text=config.ERROR_MESSAGE)
                await tracker.update(job.entry_id, status="errore", detail="Invio fallito")
                return
        finally:
            if config.DELETE_AFTER_SEND:
                cleanup_file(video_path)
            else:
                logger.info(
                    "File conservato dopo il download perché DELETE_AFTER_SEND=False: %s",
                    video_path,
                )


download_queue = DownloadQueue()
