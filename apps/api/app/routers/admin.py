import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db import get_db
from app.models.resource import Resource, ResourceStatus
from app.models.review_record import ReviewRecord
from app.models.software import Software
from app.models.user import User
from app.routers.resources import ResourceOut
from app.routers.software import SoftwareOut
from app.storage import get_storage

router = APIRouter(
    prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)]
)


class ReviewRequest(BaseModel):
    comment: str = ""


def _review(
    resource_id: int,
    target_status: ResourceStatus,
    action: str,
    comment: str,
    db: Session,
    admin: User,
) -> Resource:
    resource = db.get(Resource, resource_id)
    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )
    resource.status = target_status
    db.add(
        ReviewRecord(
            resource_id=resource.id, admin_id=admin.id, action=action, comment=comment
        )
    )
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/resources", response_model=list[ResourceOut])
def list_resources_by_status(
    status_filter: ResourceStatus = Query(default=ResourceStatus.PENDING, alias="status"),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Resource)
        .where(Resource.status == status_filter)
        .order_by(Resource.created_at.asc())
    ).all()


@router.post("/resources/{resource_id}/approve", response_model=ResourceOut)
def approve_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return _review(resource_id, ResourceStatus.PUBLISHED, "approve", "", db, admin)


@router.post("/resources/{resource_id}/reject", response_model=ResourceOut)
def reject_resource(
    resource_id: int,
    payload: ReviewRequest | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    comment = payload.comment if payload else ""
    return _review(resource_id, ResourceStatus.REJECTED, "reject", comment, db, admin)


@router.post("/resources/{resource_id}/ban", response_model=ResourceOut)
def ban_resource(
    resource_id: int,
    payload: ReviewRequest | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    comment = payload.comment if payload else ""
    return _review(resource_id, ResourceStatus.BANNED, "ban", comment, db, admin)


class SoftwareUpdateRequest(BaseModel):
    name: str | None = None
    version: str | None = None
    platform: str | None = None
    description: str | None = None
    is_active: bool | None = None


@router.get("/software", response_model=list[SoftwareOut])
def list_all_software(db: Session = Depends(get_db)):
    return db.scalars(select(Software).order_by(Software.created_at.desc())).all()


@router.post("/software", status_code=status.HTTP_201_CREATED, response_model=SoftwareOut)
def upload_software(
    file: UploadFile = File(),
    name: str = Form(min_length=1, max_length=255),
    version: str = Form(min_length=1, max_length=64),
    platform: str = Form(min_length=1, max_length=32),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    storage = get_storage()
    stored_path = storage.save(file.filename or "unnamed", file.file)
    software = Software(
        name=name,
        version=version,
        platform=platform,
        description=description,
        original_filename=file.filename or "unnamed",
        stored_path=stored_path,
        file_size=os.path.getsize(storage.get_path(stored_path)),
        is_active=True,
    )
    db.add(software)
    db.commit()
    db.refresh(software)
    return software


@router.patch("/software/{software_id}", response_model=SoftwareOut)
def update_software(
    software_id: int,
    payload: SoftwareUpdateRequest,
    db: Session = Depends(get_db),
):
    software = db.get(Software, software_id)
    if software is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Software not found"
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(software, field, value)
    db.commit()
    db.refresh(software)
    return software


@router.delete("/software/{software_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_software(software_id: int, db: Session = Depends(get_db)):
    software = db.get(Software, software_id)
    if software is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Software not found"
        )
    file_path = get_storage().get_path(software.stored_path)
    db.delete(software)
    db.commit()
    # Best-effort cleanup; a missing file must not fail the delete.
    try:
        os.remove(file_path)
    except OSError:
        pass
