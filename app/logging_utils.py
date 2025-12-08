import logging
from collections import deque
from typing import Deque, List

from . import config


class InMemoryLogHandler(logging.Handler):
    def __init__(self, max_records: int):
        super().__init__()
        self.records: Deque[str] = deque(maxlen=max_records)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.records.append(msg)

    def list_logs(self) -> List[str]:
        return list(self.records)[::-1]


log_buffer = InMemoryLogHandler(max_records=config.LOG_BUFFER_LIMIT)
