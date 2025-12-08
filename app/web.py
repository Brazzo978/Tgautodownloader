from datetime import datetime
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .logging_utils import log_buffer
from .status_tracker import DownloadEntry, tracker


def _format_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def build_html(entries: List[DownloadEntry], logs: List[str]) -> str:
    rows = "".join(
        f"<tr><td>{e.id}</td><td>{e.username or e.user_id or '-'}</td><td>{e.url}</td>"
        f"<td>{e.status}</td><td>{e.detail}</td><td>{_format_time(e.updated_at)}</td></tr>"
        for e in entries
    )
    log_lines = "".join(f"<li>{line}</li>" for line in logs)
    return f"""
    <html>
    <head>
        <title>Telegram Downloader - Stato</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            h1 {{ margin-bottom: 0.5rem; }}
            .section {{ margin-bottom: 2rem; }}
        </style>
    </head>
    <body>
        <h1>Stato download</h1>
        <div class="section">
            <table>
                <thead>
                    <tr><th>ID</th><th>Utente</th><th>URL</th><th>Stato</th><th>Dettagli</th><th>Ultimo aggiornamento</th></tr>
                </thead>
                <tbody>{rows or '<tr><td colspan="6">Nessun download ancora.</td></tr>'}</tbody>
            </table>
        </div>
        <div class="section">
            <h2>Log recenti</h2>
            <ol>{log_lines or '<li>Nessun log ancora.</li>'}</ol>
        </div>
    </body>
    </html>
    """


def create_web_app() -> FastAPI:
    app = FastAPI(title="Telegram Video Bot Monitor")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        entries = await tracker.list_entries()
        logs = log_buffer.list_logs()
        return build_html(entries, logs)

    @app.get("/api/status")
    async def status() -> dict:
        entries = await tracker.list_entries()
        return {
            "downloads": [
                {
                    "id": e.id,
                    "url": e.url,
                    "user_id": e.user_id,
                    "username": e.username,
                    "status": e.status,
                    "detail": e.detail,
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in entries
            ]
        }

    @app.get("/api/logs")
    async def logs() -> dict:
        return {"logs": log_buffer.list_logs()}

    return app
