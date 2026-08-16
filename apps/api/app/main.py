import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db import SessionLocal
from app.middleware.rate_limit import DownloadRateLimitMiddleware
from app.models.user import User
from app.routers import admin, auth, resources

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    _seed_initial_admin()
    yield


def _seed_initial_admin() -> None:
    """Create the initial admin account if no admin exists yet.

    Requires the schema to be in place (run `alembic upgrade head` first);
    failures are logged so the app can still start for read-only checks.
    """
    db = SessionLocal()
    try:
        has_admin = db.scalar(select(User.id).where(User.is_admin.is_(True)).limit(1))
        if has_admin is None:
            db.add(
                User(
                    username=settings.INITIAL_ADMIN_USERNAME,
                    password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                    is_admin=True,
                )
            )
            db.commit()
            logger.info("Seeded initial admin '%s'", settings.INITIAL_ADMIN_USERNAME)
    except Exception:
        db.rollback()
        logger.exception("Failed to seed initial admin (is the schema migrated?)")
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Solotalk Space API", lifespan=lifespan)
    app.add_middleware(
        DownloadRateLimitMiddleware,
        limit_per_minute=settings.RATE_LIMIT_DOWNLOAD_PER_MINUTE,
    )
    app.include_router(auth.router)
    app.include_router(resources.router)
    app.include_router(admin.router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
