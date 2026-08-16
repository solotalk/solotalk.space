import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.software import Software
from app.storage import get_storage

router = APIRouter(prefix="/api/software", tags=["software"])


class SoftwareOut(BaseModel):
    id: int
    name: str
    version: str
    platform: str
    description: str | None
    file_size: int
    download_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SoftwareListOut(BaseModel):
    items: list[SoftwareOut]


@router.get("", response_model=SoftwareListOut)
def list_software(db: Session = Depends(get_db)):
    items = db.scalars(
        select(Software)
        .where(Software.is_active.is_(True))
        .order_by(Software.created_at.desc())
    ).all()
    return SoftwareListOut(items=items)


@router.get("/{software_id}/download")
def download_software(software_id: int, db: Session = Depends(get_db)):
    # Per-IP rate limiting is enforced by DownloadRateLimitMiddleware.
    software = db.get(Software, software_id)
    if software is None or not software.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Software not found"
        )
    file_path = get_storage().get_path(software.stored_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    software.download_count += 1
    db.commit()
    return FileResponse(file_path, filename=software.original_filename)
