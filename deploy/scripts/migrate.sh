#!/usr/bin/env bash
# Solotalk Space — apply database migrations (alembic upgrade head).
#
# Two modes, picked automatically:
#   1. Binary mode:  set SOLOTALK_MIGRATE_CMD to a command that runs
#      `alembic upgrade head` from the deployed backend binary
#      (e.g. SOLOTALK_MIGRATE_CMD="/opt/solotalk/solotalk-api migrate").
#   2. Source mode:  when SOLOTALK_MIGRATE_CMD is unset, runs
#      `uv run alembic upgrade head` from apps/api (deploying from source).
#
# Usage: migrate.sh [path-to-.env]   (default: ../.env relative to this script)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${1:-$SCRIPT_DIR/../.env}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Load environment (DB_*) so alembic can reach the database.
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "$ENV_FILE"
    set +a
else
    log "WARNING: env file not found: $ENV_FILE (continuing with current environment)"
fi

if [[ -n "${SOLOTALK_MIGRATE_CMD:-}" ]]; then
    # Mode 1: deployed binary.
    log "Running migrations via backend binary: $SOLOTALK_MIGRATE_CMD"
    $SOLOTALK_MIGRATE_CMD
else
    # Mode 2: from source, via uv in apps/api.
    log "Running migrations from source: uv run alembic upgrade head"
    cd "$REPO_ROOT/apps/api"
    uv run alembic upgrade head
fi

log "Migrations complete."
