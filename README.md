# Solotalk Space

Monorepo for the **Solotalk Space** website.

## Overview

Solotalk Space consists of:

- **Homepage** — promotional landing page
- **Download** — software download page
- **Question Bank Sharing (core)** — a forum-like platform where users upload exam/question resources for others to use

Key characteristics:

- **No login required for downloads.** Access is protected by per-IP rate limiting (nginx + application layer) to prevent scraping and traffic abuse.
- **Login required for uploads.** Uploaders must fill in the resource metadata when submitting.
- **Admin moderation.** Resources become publicly downloadable only after admin approval; admins can ban any resource at any time.
- **Disclaimer.** All resources are uploaded by users. The site takes no responsibility for their content; contact us for takedown in case of infringement.

## Tech Stack

| Part | Technology |
| --- | --- |
| Backend | FastAPI (Python), dependencies managed with uv, packaged as a single binary with PyInstaller |
| Frontend | Vue 3 + Vite + Naive UI, dependencies managed with pnpm |
| Database | MySQL 8.0.44, migrations via Alembic |
| Deployment | nginx (reverse proxy + static hosting + IP rate limiting) |

## Repository Layout

```
apps/
  api/        # FastAPI backend
  web/        # Vue 3 frontend
packages/     # shared packages (placeholder)
deploy/       # nginx config example, DB migration/deploy scripts, backup scripts, .env.example
```

## Deliverables

- Backend binary (PyInstaller single-file build)
- Frontend static build artifacts
- nginx configuration example
- MySQL 8.0.44 migration & deployment scripts
- Automated backup scripts (database + uploaded files)

## Configuration

Database credentials and other environment-specific settings are loaded from environment variables via a `.env` file (see `deploy/.env.example`). Never commit real `.env` files.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system architecture
- [CONTRIBUTE.md](CONTRIBUTE.md) — contribution guide, **read this before writing any code**
- [中文版 README](README.zh-CN.md)
