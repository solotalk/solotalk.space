import os
import tempfile

# Point storage and secrets at test-local values before any app module import.
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="solotalk-test-uploads-"))
os.environ.setdefault("JWT_SECRET", "test-secret-key-padded-to-32-bytes!")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token
from app.db import Base, get_db
from app.main import create_app
from app.models import resource, review_record, software, user  # noqa: F401 — register models
from app.models.user import User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = testing_session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def _make_user(db_session, username: str, is_admin: bool) -> dict:
    user = User(username=username, password_hash="unused", is_admin=is_admin)
    db_session.add(user)
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


@pytest.fixture()
def admin_headers(db_session):
    return _make_user(db_session, "admin", True)


@pytest.fixture()
def user_headers(db_session):
    return _make_user(db_session, "alice", False)
