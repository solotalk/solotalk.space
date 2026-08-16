#!/usr/bin/env bash
# Solotalk Space — one-shot deployment / upgrade script.
#
# Installs or upgrades the full stack on a single Linux server:
#   1. Clone (or pull) the main repository
#   2. Set up / edit the .env file
#   3. Install files (backend binary, frontend dist, nginx config, scripts)
#   4. Create the app user and grant ownership
#   5. Create / update the systemd service
#   6. Install the backup cron entry
#   7. Run database migrations
#   8. Start the app and reload nginx
#
# Fresh installs and upgrades from a former version are both supported:
# existing .env / systemd unit / cron entry are detected and preserved or
# updated idempotently.
#
# Every step asks for approval unless -y is given.
#
# Usage: sudo ./deploy.sh [-y|--yes] [-h|--help]

set -euo pipefail
trap 'echo "[ERROR] Failed at line $LINENO. Aborting." >&2' ERR

# ---------------------------------------------------------------------------
# Configuration (override via environment if needed)
# ---------------------------------------------------------------------------
REPO_URL="${REPO_URL:-https://github.com/solotalk/solotalk.space.git}"
BRANCH="${BRANCH:-master}"
REPO_DIR="${REPO_DIR:-/opt/solotalk/repo}"
INSTALL_DIR="${INSTALL_DIR:-/opt/solotalk}"
APP_USER="${APP_USER:-solotalk}"
WEB_ROOT="${WEB_ROOT:-/var/www/solotalk/web}"
SOFTWARE_DIR="${SOFTWARE_DIR:-/var/www/solotalk/software}"
BACKUP_DIR="${BACKUP_DIR:-/data/solotalk/backups}"
SERVICE_NAME="${SERVICE_NAME:-solotalk-api}"
NGINX_CONF_DST="${NGINX_CONF_DST:-/etc/nginx/conf.d/solotalk.space.conf}"
CRON_FILE="${CRON_FILE:-/etc/cron.d/solotalk-backup}"

ASSUME_YES=0
for arg in "$@"; do
    case "$arg" in
        -y|--yes) ASSUME_YES=1 ;;
        -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
        *) echo "Unknown argument: $arg" >&2; exit 2 ;;
    esac
done

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
die()  { echo "[ERROR] $*" >&2; exit 1; }

confirm() {
    # confirm <prompt> — returns 0 to proceed, 1 to skip.
    if [[ "$ASSUME_YES" -eq 1 ]]; then
        log "AUTO-YES: $1"
        return 0
    fi
    local reply
    read -r -p "$1 [y/N] " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

pick_editor() {
    if [[ -n "${EDITOR:-}" ]]; then echo "$EDITOR"; return; fi
    for e in nano vim vi; do
        if command -v "$e" >/dev/null 2>&1; then echo "$e"; return; fi
    done
    die "No editor found (nano/vim/vi). Set \$EDITOR and retry."
}

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
[[ "$EUID" -eq 0 ]] || die "This script must be run as root (use sudo)."
command -v git      >/dev/null 2>&1 || die "git is required but not installed."
command -v systemctl >/dev/null 2>&1 || die "systemd is required but not found."
if ! command -v nginx >/dev/null 2>&1; then
    log "WARNING: nginx not found. Install it before the final step."
fi

UPGRADE=0
if [[ -f "/etc/systemd/system/${SERVICE_NAME}.service" || -d "$INSTALL_DIR/bin" ]]; then
    UPGRADE=1
    log "Existing installation detected — running in UPGRADE mode."
else
    log "No existing installation detected — running in FRESH INSTALL mode."
fi

# ---------------------------------------------------------------------------
# Step 1: Clone or pull the repository
# ---------------------------------------------------------------------------
if confirm "Step 1/8: Clone/pull $REPO_URL ($BRANCH) into $REPO_DIR?"; then
    if [[ -d "$REPO_DIR/.git" ]]; then
        log "Repository exists, pulling latest $BRANCH ..."
        git -C "$REPO_DIR" checkout "$BRANCH"
        git -C "$REPO_DIR" pull --ff-only
    else
        log "Cloning repository ..."
        mkdir -p "$(dirname "$REPO_DIR")"
        git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
    fi
else
    [[ -d "$REPO_DIR" ]] || die "No repository at $REPO_DIR; cannot continue without Step 1."
    log "Skipped. Using existing repository at $REPO_DIR."
fi

# ---------------------------------------------------------------------------
# Step 2: Set up / edit the .env file
# ---------------------------------------------------------------------------
ENV_FILE="$INSTALL_DIR/.env"
if confirm "Step 2/8: Set up .env at $ENV_FILE?"; then
    mkdir -p "$INSTALL_DIR"
    if [[ ! -f "$ENV_FILE" ]]; then
        cp "$REPO_DIR/deploy/.env.example" "$ENV_FILE"
        chmod 600 "$ENV_FILE"
        log "Created $ENV_FILE from .env.example."
        if [[ "$ASSUME_YES" -eq 1 ]]; then
            log "WARNING: -y given; skipping interactive edit. EDIT $ENV_FILE BEFORE STARTING THE APP."
        else
            log "Opening $ENV_FILE for editing — fill in every change-me value."
            "$(pick_editor)" "$ENV_FILE"
        fi
    else
        log "Existing .env found (preserved)."
        if [[ "$ASSUME_YES" -eq 0 ]]; then
            read -r -p "Edit existing $ENV_FILE now? [y/N] " reply
            if [[ "$reply" =~ ^[Yy]$ ]]; then
                "$(pick_editor)" "$ENV_FILE"
            fi
        fi
    fi
else
    [[ -f "$ENV_FILE" ]] || die "No .env at $ENV_FILE; cannot continue without Step 2."
fi
# Read UPLOAD_DIR from .env so directories match the app configuration.
UPLOAD_DIR="$(grep -E '^UPLOAD_DIR=' "$ENV_FILE" | cut -d= -f2- || true)"
UPLOAD_DIR="${UPLOAD_DIR:-/data/solotalk/uploads}"

# ---------------------------------------------------------------------------
# Step 3: Install files
# ---------------------------------------------------------------------------
if confirm "Step 3/8: Install binary, frontend dist, nginx config, and scripts?"; then
    # --- Backend binary -----------------------------------------------------
    BINARY_SRC="$REPO_DIR/apps/api/dist/solotalk-api"
    if [[ ! -f "$BINARY_SRC" ]]; then
        log "Backend binary not found at $BINARY_SRC."
        if command -v uv >/dev/null 2>&1 && confirm "Build it from source with uv + PyInstaller now?"; then
            (cd "$REPO_DIR/apps/api" && uv sync && bash scripts/build_binary.sh)
        fi
    fi
    [[ -f "$BINARY_SRC" ]] || die "Backend binary missing. Build it (apps/api/scripts/build_binary.sh) and rerun."

    # Stop the service before replacing the binary (upgrade case).
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        log "Stopping $SERVICE_NAME for binary replacement ..."
        systemctl stop "$SERVICE_NAME"
    fi

    mkdir -p "$INSTALL_DIR/bin" "$INSTALL_DIR/scripts"
    cp "$BINARY_SRC" "$INSTALL_DIR/bin/solotalk-api"
    chmod 755 "$INSTALL_DIR/bin/solotalk-api"
    log "Installed backend binary -> $INSTALL_DIR/bin/solotalk-api"

    # --- Frontend dist ------------------------------------------------------
    DIST_SRC="$REPO_DIR/apps/web/dist"
    if [[ ! -d "$DIST_SRC" ]]; then
        log "Frontend dist not found at $DIST_SRC."
        if command -v pnpm >/dev/null 2>&1 && confirm "Build it from source with pnpm now?"; then
            (cd "$REPO_DIR/apps/web" && pnpm install && pnpm build)
        fi
    fi
    if [[ -d "$DIST_SRC" ]]; then
        mkdir -p "$WEB_ROOT"
        if command -v rsync >/dev/null 2>&1; then
            rsync -a --delete "$DIST_SRC/" "$WEB_ROOT/"
        else
            cp -a "$DIST_SRC/." "$WEB_ROOT/"
        fi
        log "Installed frontend dist -> $WEB_ROOT"
    else
        log "WARNING: no frontend dist; nginx will have nothing to serve at $WEB_ROOT."
    fi

    # --- nginx config -------------------------------------------------------
    # server_name / listen port are customizable. On upgrade, values from the
    # previously installed config are read back and offered as defaults.
    NGINX_CONF_SRC="$REPO_DIR/deploy/nginx/solotalk.space.conf.example"
    DEFAULT_SERVER_NAME="solotalk.space www.solotalk.space"
    DEFAULT_LISTEN_PORT="80"
    if [[ -f "$NGINX_CONF_DST" ]]; then
        OLD_SERVER_NAME="$(grep -oE '^[[:space:]]*server_name[[:space:]]+[^;]+' "$NGINX_CONF_DST" | head -n1 | sed -E 's/^[[:space:]]*server_name[[:space:]]+//')"
        OLD_LISTEN_PORT="$(grep -oE '^[[:space:]]*listen[[:space:]]+[0-9]+' "$NGINX_CONF_DST" | head -n1 | grep -oE '[0-9]+')"
        [[ -n "$OLD_SERVER_NAME" ]] && DEFAULT_SERVER_NAME="$OLD_SERVER_NAME"
        [[ -n "$OLD_LISTEN_PORT" ]] && DEFAULT_LISTEN_PORT="$OLD_LISTEN_PORT"
        log "Existing nginx config found: server_name='$DEFAULT_SERVER_NAME' listen=$DEFAULT_LISTEN_PORT"
    fi
    SERVER_NAME="${SERVER_NAME:-$DEFAULT_SERVER_NAME}"
    LISTEN_PORT="${LISTEN_PORT:-$DEFAULT_LISTEN_PORT}"
    if [[ "$ASSUME_YES" -eq 0 ]]; then
        read -r -p "server_name [$DEFAULT_SERVER_NAME]: " reply
        [[ -n "$reply" ]] && SERVER_NAME="$reply"
        read -r -p "listen port [$DEFAULT_LISTEN_PORT]: " reply
        [[ -n "$reply" ]] && LISTEN_PORT="$reply"
    fi
    [[ "$LISTEN_PORT" =~ ^[0-9]+$ && "$LISTEN_PORT" -le 65535 ]] || die "Invalid listen port: $LISTEN_PORT"
    [[ -n "$SERVER_NAME" ]] || die "server_name must not be empty."

    cp "$NGINX_CONF_SRC" "$NGINX_CONF_DST"
    sed -i -E "s|^([[:space:]]*)listen[[:space:]]+[0-9]+;|\1listen $LISTEN_PORT;|" "$NGINX_CONF_DST"
    sed -i -E "s|^([[:space:]]*)server_name[[:space:]]+[^;]+;|\1server_name $SERVER_NAME;|" "$NGINX_CONF_DST"
    log "Installed nginx config -> $NGINX_CONF_DST (server_name='$SERVER_NAME', listen=$LISTEN_PORT)"
    if ! grep -qs 'zone=dl_limit' /etc/nginx/nginx.conf 2>/dev/null; then
        log "WARNING: make sure the limit_req_zone/limit_conn_zone directives (top of the"
        log "         installed config file) are moved into the nginx http block."
    fi

    # --- Maintenance scripts -------------------------------------------------
    cp "$REPO_DIR/deploy/scripts/backup.sh" "$REPO_DIR/deploy/scripts/migrate.sh" \
       "$REPO_DIR/deploy/scripts/deploy.sh" "$INSTALL_DIR/scripts/"
    chmod +x "$INSTALL_DIR/scripts/"*.sh
    log "Installed scripts -> $INSTALL_DIR/scripts"
else
    log "Skipped Step 3."
fi

# ---------------------------------------------------------------------------
# Step 4: App user + directories + ownership
# ---------------------------------------------------------------------------
if confirm "Step 4/8: Create app user '$APP_USER' (if missing) and set ownership?"; then
    if ! id -u "$APP_USER" >/dev/null 2>&1; then
        useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER"
        log "Created system user $APP_USER."
    else
        log "User $APP_USER already exists."
    fi
    mkdir -p "$UPLOAD_DIR" "$BACKUP_DIR" "$SOFTWARE_DIR" "$WEB_ROOT"
    chown -R "$APP_USER:$APP_USER" "$UPLOAD_DIR" "$BACKUP_DIR"
    chown -R "$APP_USER:$APP_USER" "$WEB_ROOT" "$SOFTWARE_DIR"
    chown -R "$APP_USER:$APP_USER" "$INSTALL_DIR/bin"
    chmod 600 "$ENV_FILE"
    chown "$APP_USER:$APP_USER" "$ENV_FILE"
    log "Ownership granted to $APP_USER."
else
    log "Skipped Step 4."
fi

# ---------------------------------------------------------------------------
# Step 5: systemd service
# ---------------------------------------------------------------------------
UNIT_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
if confirm "Step 5/8: Create/update systemd unit $UNIT_FILE?"; then
    cat > "$UNIT_FILE" <<EOF
[Unit]
Description=Solotalk Space API (FastAPI binary)
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/bin/solotalk-api
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
    log "Systemd unit installed and enabled."
else
    log "Skipped Step 5."
fi

# ---------------------------------------------------------------------------
# Step 6: Backup cron entry
# ---------------------------------------------------------------------------
if confirm "Step 6/8: Install backup cron entry (daily 03:17) at $CRON_FILE?"; then
    cat > "$CRON_FILE" <<EOF
# Solotalk Space daily backup (database + uploads).
17 3 * * * root BACKUP_DIR=$BACKUP_DIR $INSTALL_DIR/scripts/backup.sh $ENV_FILE >> /var/log/solotalk-backup.log 2>&1
EOF
    chmod 644 "$CRON_FILE"
    log "Cron entry installed -> $CRON_FILE"
else
    log "Skipped Step 6."
fi

# ---------------------------------------------------------------------------
# Step 7: Database migrations
# ---------------------------------------------------------------------------
if confirm "Step 7/8: Run database migrations (alembic upgrade head)?"; then
    if command -v uv >/dev/null 2>&1 && [[ -d "$REPO_DIR/apps/api" ]]; then
        set -a; source "$ENV_FILE"; set +a
        (cd "$REPO_DIR/apps/api" && uv sync && uv run alembic upgrade head)
        log "Migrations complete."
    else
        log "WARNING: uv not available; run migrations manually:"
        log "  cd $REPO_DIR/apps/api && uv run alembic upgrade head"
    fi
else
    log "Skipped Step 7."
fi

# ---------------------------------------------------------------------------
# Step 8: Start the app
# ---------------------------------------------------------------------------
if confirm "Step 8/8: Start $SERVICE_NAME and reload nginx?"; then
    systemctl start "$SERVICE_NAME" 2>/dev/null || systemctl restart "$SERVICE_NAME"
    if command -v nginx >/dev/null 2>&1; then
        nginx -t
        systemctl reload nginx
        log "nginx reloaded."
    fi
    sleep 2
    if curl -sf -m 5 http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        log "Health check passed: http://127.0.0.1:8000/api/health"
    else
        log "WARNING: health check failed. Inspect with: journalctl -u $SERVICE_NAME -e"
    fi
    systemctl --no-pager --full status "$SERVICE_NAME" | head -n 5 || true
else
    log "Skipped Step 8."
fi

log "Done. Mode: $([[ "$UPGRADE" -eq 1 ]] && echo upgrade || echo fresh install)."
