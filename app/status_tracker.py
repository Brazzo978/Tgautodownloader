import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional


@dataclass
class DownloadEntry:
    id: int
    url: str
    user_id: Optional[int]
    username: Optional[str]
    status: str
    detail: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class DownloadTracker:
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self._entries: Deque[DownloadEntry] = deque(maxlen=max_entries)
        self._lock = asyncio.Lock()
        self._counter = 0

    async def add(self, url: str, user_id: Optional[int], username: Optional[str], status: str, detail: str = "") -> int:
        async with self._lock:
            self._counter += 1
            entry = DownloadEntry(
                id=self._counter,
                url=url,
                user_id=user_id,
                username=username,
                status=status,
                detail=detail,
            )
            self._entries.appendleft(entry)
            return entry.id

    async def update(self, entry_id: int, status: str, detail: str = "") -> None:
        async with self._lock:
            for entry in self._entries:
                if entry.id == entry_id:
                    entry.status = status
                    entry.detail = detail
                    entry.updated_at = datetime.utcnow()
                    break

    async def list_entries(self) -> List[DownloadEntry]:
        async with self._lock:
            return list(self._entries)


tracker = DownloadTracker()
