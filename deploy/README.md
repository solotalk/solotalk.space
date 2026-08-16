# deploy/ — Deployment assets

Deployment artifacts for the single-server Solotalk Space setup (nginx + FastAPI binary + MySQL 8.0.44).

## File inventory

| Path | Purpose |
| --- | --- |
| `.env.example` | Environment variable template. Copy to `.env` and fill in real values — never commit `.env`. |
| `nginx/solotalk.space.conf.example` | nginx server block: frontend static hosting + SPA fallback, `/api/` reverse proxy, `/software/` static installers, coarse per-IP rate limiting. |
| `scripts/deploy.sh` | One-shot deployment/upgrade on the server: clones or pulls the repo, edits `.env`, installs files, creates the app user, systemd unit and cron entry, runs migrations, starts the app. Every step asks for approval unless `-y` is given. |
| `scripts/backup.sh` | Cron-ready backup: `mysqldump` + uploads archive, keeps the newest 14 of each. |
| `scripts/migrate.sh` | Applies DB migrations (`alembic upgrade head`), via the deployed binary or `uv run` from source. |

## Server layout

- `/etc/nginx/conf.d/solotalk.space.conf` — copy of `nginx/solotalk.space.conf.example`. The `limit_req_zone` / `limit_conn_zone` directives at the top of the file belong in the nginx **http** block (e.g. `nginx.conf`), not the server block — see the comments in the file.
- `/var/www/solotalk/web` — frontend build output (`apps/web` dist).
- `/var/www/solotalk/software` — software installer files for the Download page.
- `/data/solotalk/uploads` — uploaded resource files (`UPLOAD_DIR`).
- `/data/solotalk/backups` — backup output (`BACKUP_DIR`, overridable via env).
- Backend binary listens on `127.0.0.1:8000` (e.g. managed by systemd).
- Scripts: place `scripts/*.sh` anywhere stable (e.g. `/opt/solotalk/scripts`), `chmod +x`, and pass the `.env` path as the first argument if it is not `../.env` relative to the script.

## Automated deployment

On the target server (as root):

```bash
# Fresh install or upgrade — same command; existing installations are detected.
curl -fsSL https://raw.githubusercontent.com/solotalk/solotalk.space/master/deploy/scripts/deploy.sh -o /tmp/deploy.sh
sudo bash /tmp/deploy.sh        # add -y to auto-approve every step
```

The script clones/pulls the repo to `/opt/solotalk/repo`, edits `.env`, installs the binary/dist/nginx config/scripts, creates the `solotalk` user, the systemd unit and the backup cron entry, runs migrations, then starts the app.

## Setup reminder

1. `cp .env.example .env` and fill in every `change-me` value (DB credentials, JWT secret, initial admin password).
2. Create the directories above with appropriate ownership.
3. Install the nginx config, then `nginx -t && systemctl reload nginx`.
4. Run `scripts/migrate.sh` to bring the database schema up to date.

## Backup cron

Daily at 03:17:

```cron
17 3 * * * /opt/solotalk/scripts/backup.sh /opt/solotalk/.env >> /var/log/solotalk-backup.log 2>&1
```
