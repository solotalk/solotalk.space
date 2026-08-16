#!/usr/bin/env bash
# Solotalk Space — backup script (cron-ready).
#
# Dumps the MySQL database and archives the uploads directory into
# $BACKUP_DIR, then rotates so only the newest 14 of each kind are kept.
#
# Usage: backup.sh [path-to-.env]   (default: ../.env relative to this script)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-$SCRIPT_DIR/../.env}"
BACKUP_DIR="${BACKUP_DIR:-/data/solotalk/backups}"
KEEP=14

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Load environment (DB_*, UPLOAD_DIR).
if [[ ! -f "$ENV_FILE" ]]; then
    log "ERROR: env file not found: $ENV_FILE"
    exit 1
fi
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${UPLOAD_DIR:?UPLOAD_DIR is required}"

TS="$(date '+%Y%m%d-%H%M%S')"
mkdir -p "$BACKUP_DIR"

# --- Database dump ---------------------------------------------------------
DB_DUMP="$BACKUP_DIR/db-$TS.sql.gz"
log "Dumping database $DB_NAME to $DB_DUMP ..."
MYSQL_PWD="$DB_PASSWORD" mysqldump \
    --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER" \
    --single-transaction --quick \
    "$DB_NAME" | gzip > "$DB_DUMP"
log "Database dump complete."

# --- Uploads archive -------------------------------------------------------
UPLOADS_ARCHIVE="$BACKUP_DIR/uploads-$TS.tar.gz"
log "Archiving uploads directory $UPLOAD_DIR to $UPLOADS_ARCHIVE ..."
tar -czf "$UPLOADS_ARCHIVE" -C "$(dirname "$UPLOAD_DIR")" "$(basename "$UPLOAD_DIR")"
log "Uploads archive complete."

# --- Rotation: keep the newest $KEEP of each kind --------------------------
log "Rotating backups (keeping newest $KEEP of each kind) ..."
ls -1t "$BACKUP_DIR"/db-*.sql.gz 2>/dev/null | tail -n "+$((KEEP + 1))" | xargs -r rm -f
ls -1t "$BACKUP_DIR"/uploads-*.tar.gz 2>/dev/null | tail -n "+$((KEEP + 1))" | xargs -r rm -f
log "Rotation complete."

log "Backup finished successfully."
