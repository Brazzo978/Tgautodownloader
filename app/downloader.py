import logging
from pathlib import Path
from typing import Optional

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def ensure_download_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def download_video(url: str, download_dir: str) -> Optional[Path]:
    """
    Scarica il video dall'URL usando yt-dlp nella cartella download_dir.
    Ritorna il percorso completo del file scaricato, oppure None in caso di errore.
    """

    target_dir = ensure_download_dir(download_dir)
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
