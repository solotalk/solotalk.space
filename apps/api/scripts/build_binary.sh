#!/usr/bin/env bash
# Build a single-file backend binary with PyInstaller.
# Output: dist/solotalk-api
set -euo pipefail

cd "$(dirname "$0")/.."

uv run pyinstaller \
    --onefile \
    --clean \
    --name solotalk-api \
    --hidden-import uvicorn.logging \
    --hidden-import uvicorn.loops.auto \
    --hidden-import uvicorn.protocols.http.auto \
    --hidden-import uvicorn.protocols.websockets.auto \
    --hidden-import uvicorn.lifespan.on \
    app/main.py

echo "Built: dist/solotalk-api"
