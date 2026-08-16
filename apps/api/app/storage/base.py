from abc import ABC, abstractmethod
from typing import BinaryIO


class Storage(ABC):
    """Storage backend interface for uploaded resource files."""

    @abstractmethod
    def save(self, filename: str, fileobj: BinaryIO) -> str:
        """Persist a file and return its stored path (opaque to callers)."""

    @abstractmethod
    def get_path(self, stored_path: str) -> str:
        """Resolve a stored path to an absolute filesystem path."""
