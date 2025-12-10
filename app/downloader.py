import logging
import re
from pathlib import Path
from typing import Optional

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def ensure_download_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def user_download_dir(base_dir: str, user_id: Optional[int], username: Optional[str]) -> Path:
    label = username or (str(user_id) if user_id is not None else "anonimo")
    safe_label = re.sub(r"[^A-Za-z0-9._-]", "_", label) or "utente"
    return Path(base_dir) / safe_label


def download_video(
    url: str, download_dir: str, user_id: Optional[int] = None, username: Optional[str] = None
) -> Optional[Path]:
    """
    Scarica il video dall'URL usando yt-dlp nella cartella download_dir.
    Ritorna il percorso completo del file scaricato, oppure None in caso di errore.
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
            info = ydl.extract_info(url, download=True)
            downloaded_path = ydl.prepare_filename(info)
            final_path = Path(downloaded_path)
            if final_path.suffix != ".mp4" and final_path.with_suffix(".mp4").exists():
                final_path = final_path.with_suffix(".mp4")
            logger.info("Video scaricato: %s", final_path)
            return final_path
    except Exception:
        logger.exception("Errore durante il download del video")
        return None


def file_size_mb(path: Path) -> float:
    size_bytes = path.stat().st_size
    return size_bytes / (1024 * 1024)


def cleanup_file(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
            logger.info("File rimosso: %s", path)
    except Exception:
        logger.exception("Errore durante la rimozione del file: %s", path)
