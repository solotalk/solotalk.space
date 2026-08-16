from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db import get_db
from app.models.resource import Resource, ResourceStatus
from app.models.review_record import ReviewRecord
from app.models.user import User
from app.routers.resources import ResourceOut

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
