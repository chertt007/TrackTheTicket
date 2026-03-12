"""Shared infrastructure utilities used by multiple modules."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 500

    def to_dict(self) -> dict[str, str | int]:
        """Serialize object data into a dictionary payload."""
        return {
            "code": self.code,
            "message": self.message,
            "status_code": self.status_code,
        }

