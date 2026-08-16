import os
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.models.resource import Resource, ResourceStatus
from app.models.user import User
from app.storage import get_storage

router = APIRouter(prefix="/api/resources", tags=["resources"])


class ResourceOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    original_filename: str
    file_size: int
    download_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ResourceOut]


@router.get("", response_model=ResourceListOut)
def list_resources(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Resource).where(Resource.status == ResourceStatus.PUBLISHED)
    if keyword:
        like = f"%{keyword}%"
        query = query.where(
            or_(Resource.title.like(like), Resource.description.like(like))
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Resource.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ResourceListOut(total=total, page=page, page_size=page_size, items=items)


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.get(Resource, resource_id)
    if resource is None or resource.status != ResourceStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )
    return resource


@router.get("/{resource_id}/download")
def download_resource(resource_id: int, db: Session = Depends(get_db)):
    # Per-IP rate limiting is enforced by DownloadRateLimitMiddleware.
    resource = db.get(Resource, resource_id)
    if resource is None or resource.status != ResourceStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )
    file_path = get_storage().get_path(resource.stored_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    resource.download_count += 1
    db.commit()
    return FileResponse(file_path, filename=resource.original_filename)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResourceOut)
def upload_resource(
    file: UploadFile = File(),
    title: str = Form(min_length=1, max_length=255),
    description: str = Form(default=""),
    category: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    storage = get_storage()
    stored_path = storage.save(file.filename or "unnamed", file.file)
    resource = Resource(
        uploader_id=current_user.id,
        title=title,
        description=description,
        category=category,
        original_filename=file.filename or "unnamed",
        stored_path=stored_path,
        file_size=os.path.getsize(storage.get_path(stored_path)),
        status=ResourceStatus.PENDING,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource
