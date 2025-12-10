import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


@dataclass
class DownloadOutcome:
    path: Optional[Path]
    reused: bool
    skipped: bool = False
    estimated_size_mb: Optional[float] = None


def ensure_download_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def user_download_dir(base_dir: str, user_id: Optional[int], username: Optional[str]) -> Path:
    label = username or (str(user_id) if user_id is not None else "anonimo")
    safe_label = re.sub(r"[^A-Za-z0-9._-]", "_", label) or "utente"
    return Path(base_dir) / safe_label


def download_video(
    url: str,
    download_dir: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    max_download_mb: Optional[int] = None,
) -> DownloadOutcome:
    """
    Scarica il video dall'URL usando yt-dlp nella cartella download_dir.
    Restituisce un ``DownloadOutcome`` che indica se il file è stato scaricato,
    riutilizzato, oppure saltato prima del download perché supera il limite.
    """

    if user_id is None and username is None:
        target_dir = ensure_download_dir(download_dir)
    else:
        target_dir = ensure_download_dir(user_download_dir(download_dir, user_id, username))
    output_template = str(target_dir / "%(title).80s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "logger": logger,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            estimated_size_mb = _extract_size_mb(info)

            if max_download_mb and estimated_size_mb and estimated_size_mb > max_download_mb:
                logger.warning(
                    "Download saltato perché stimato %s MB (> %s MB)",
                    f"{estimated_size_mb:.1f}",
                    max_download_mb,
                )
                return DownloadOutcome(
                    path=None,
                    reused=False,
                    skipped=True,
                    estimated_size_mb=estimated_size_mb,
                )

            downloaded_path = ydl.prepare_filename(info)
            final_path = Path(downloaded_path)
            if final_path.suffix != ".mp4" and final_path.with_suffix(".mp4").exists():
                final_path = final_path.with_suffix(".mp4")

            if final_path.exists():
                logger.info("File già presente, salto il download: %s", final_path)
                return DownloadOutcome(
                    path=final_path,
                    reused=True,
                    estimated_size_mb=estimated_size_mb,
                )

            info = ydl.process_info(info)
            final_path = Path(ydl.prepare_filename(info))
            if final_path.suffix != ".mp4" and final_path.with_suffix(".mp4").exists():
                final_path = final_path.with_suffix(".mp4")
            logger.info("Video scaricato: %s", final_path)
            return DownloadOutcome(
                path=final_path,
                reused=False,
                estimated_size_mb=file_size_mb(final_path),
            )
    except Exception:
        logger.exception("Errore durante il download del video")
        return DownloadOutcome(path=None, reused=False, skipped=False)


def file_size_mb(path: Path) -> float:
    size_bytes = path.stat().st_size
    return size_bytes / (1024 * 1024)


def _extract_size_mb(info: dict) -> Optional[float]:
    for key in ("filesize", "filesize_approx"):
        if info.get(key):
            return info[key] / (1024 * 1024)
    return None


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
            logger.info("File rimosso: %s", path)
    except Exception:
        logger.exception("Errore durante la rimozione del file: %s", path)
