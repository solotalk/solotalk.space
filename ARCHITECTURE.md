# Solotalk Space — Architecture

This document describes the agreed system architecture. It is the reference for all implementation work; deviations must be discussed before coding.

## 1. System Overview

Solotalk Space is a single-server web application composed of three runtime parts:

```
                        ┌─────────────────────────────────────┐
 Browser ──────────────▶│ nginx                               │
                        │  - static hosting (frontend build)  │
                        │  - reverse proxy → backend binary   │
                        │  - per-IP rate limiting (coarse)    │
                        └──────┬──────────────────────┬───────┘
                               ▼                      ▼
                     ┌──────────────────┐   ┌──────────────────┐
                     │ Backend binary   │   │ uploads/         │
                     │ (FastAPI,        │──▶│ (resource files  │
                     │  PyInstaller)    │   │  on local disk)  │
                     └──────┬───────────┘   └──────────────────┘
                            ▼
                     ┌──────────────────┐
                     │ MySQL 8.0.44     │
                     └──────────────────┘
```

- **nginx** serves the frontend static build, reverse-proxies API requests to the backend binary, and enforces coarse per-IP rate limits (`limit_req` / `limit_conn`).
- **Backend** is a FastAPI application packaged as a single-file binary via PyInstaller; the deployment machine needs no Python environment.
- **MySQL 8.0.44** stores all structured data; connections are configured exclusively through environment variables (`.env`).
- **Uploaded resource files** live on local disk (path from env). The storage layer is abstracted behind an interface so it can be swapped for object storage (OSS/S3) later without touching business logic.

## 2. Repository Layout

```
apps/
  api/          # FastAPI backend (uv, Alembic, PyInstaller)
  web/          # Vue 3 frontend (Vite, pnpm, Naive UI)
packages/       # shared packages — placeholder, currently empty
deploy/         # deployment artifacts:
                #   - nginx config example
                #   - DB migration/deploy scripts
                #   - backup scripts
                #   - .env.example
```

## 3. Backend (`apps/api`)

- **Framework:** FastAPI.
- **Dependency management:** uv (lockfile committed).
- **Packaging:** PyInstaller single-file binary.
- **Configuration:** all environment-specific values (DB credentials, JWT secret, upload directory, initial admin account, etc.) are loaded from environment variables via `.env`; never hard-coded.
- **Authentication:** JWT (short-lived access token + refresh token). Registration/login required only for uploading and administration; browsing and downloading are anonymous.
- **Initial admin:** seeded on first startup from environment variables.
- **Rate limiting:** an application-layer middleware applies fine-grained per-IP counting on download/search endpoints, complementing the coarse nginx limits.
- **Database migrations:** Alembic, versioned with the backend code; deployment runs `alembic upgrade head`. An initial SQL dump is provided for fresh installations.
- **Storage:** repository/interface pattern — `LocalDiskStorage` now, `ObjectStorage` reserved for future upgrade.

## 4. Frontend (`apps/web`)

- **Stack:** Vue 3 + Vite + Naive UI, dependencies managed with pnpm.
- **Pages:** Homepage (promotion), Download (software), Question Bank (browse/search/download anonymously; upload + metadata form after login), Admin (review queue, ban/unban).
- **UI copy:** minimal and functional — no excessive explanatory text on display pages.
- **Build output:** static artifacts served by nginx.

## 5. Data & Moderation Flow

- Resource lifecycle: `pending` → (admin approves) → `published`; (admin rejects) → `rejected`; admin can move any resource to `banned` at any time.
- Only `published` resources are visible and downloadable publicly.
- Core entities (initial design, refined during implementation): users, resources (metadata + file reference + status), review records, download logs (for IP rate limiting / auditing).
- Disclaimer: resources are user-uploaded; the site assumes no responsibility and honors takedown requests.

## 6. Deployment & Deliverables

Deliverables produced by the build:

1. Backend binary (PyInstaller)
2. Frontend static artifacts
3. nginx configuration example
4. MySQL 8.0.44 migration & deployment scripts (Alembic + initial SQL)
5. Automated backup scripts

**Backup:** cron-driven script performing `mysqldump` plus an archive of the uploads directory, with date-based rotation (keep the latest N copies).

## 7. Security Notes

- No login for downloads; abuse is controlled by nginx + application-layer per-IP rate limiting.
- JWT secrets and DB credentials only ever enter via environment variables.
- Uploads are stored outside the web root and served through the backend with status/permission checks.
