from app.config import settings
from app.storage.base import Storage
from app.storage.local import LocalDiskStorage

# Factory kept separate from the interface so an object-storage
# implementation (OSS/S3) can be selected here later via settings.
def get_storage() -> Storage:
    return LocalDiskStorage(settings.UPLOAD_DIR)
