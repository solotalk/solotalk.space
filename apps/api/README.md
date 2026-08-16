# Solotalk Space API

FastAPI backend for Solotalk Space: question-bank sharing with anonymous
browsing/downloading, authenticated uploads, and admin review.

## Quickstart

```bash
# Install dependencies (uv)
uv sync

# Configure environment
cp ../../deploy/.env.example .env
# Edit .env: DB credentials, JWT_SECRET, UPLOAD_DIR, initial admin, etc.

# Create the database schema (requires a running MySQL 8.0.44)
uv run alembic upgrade head

# Run the development server
uv run uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`; docs at `/docs`.
On startup the upload directory is created and the initial admin account is
seeded from `.env` if no admin exists.

## Endpoints

- `POST /api/auth/register` / `POST /api/auth/login` / `POST /api/auth/refresh`
- `GET /api/resources` — list published resources (keyword, page, page_size)
- `GET /api/resources/{id}` — resource detail (published only)
- `GET /api/resources/{id}/download` — download file (per-IP rate limited)
- `POST /api/resources` — upload (auth required, multipart: file + title/description/category)
- `GET /api/admin/resources?status=pending` — review queue (admin)
- `POST /api/admin/resources/{id}/approve|reject|ban` — review actions (admin)
- `GET /api/health`

## Binary build

```bash
./scripts/build_binary.sh
# -> dist/solotalk-api (PyInstaller single-file binary)
```

The binary serves the API directly (`uvicorn` programmatic run on port 8000).
Schema migrations are not baked into the binary; run `alembic upgrade head`
against the target database during deployment.
