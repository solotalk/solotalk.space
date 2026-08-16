import shutil
import uuid
from pathlib import Path
from typing import BinaryIO

from app.storage.base import Storage


class LocalDiskStorage(Storage):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def save(self, filename: str, fileobj: BinaryIO) -> str:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename).suffix
        stored_path = f"{uuid.uuid4().hex}{suffix}"
        with open(self.base_dir / stored_path, "wb") as out:
            shutil.copyfileobj(fileobj, out)
        return stored_path

    def get_path(self, stored_path: str) -> str:
        return str(self.base_dir / stored_path)
