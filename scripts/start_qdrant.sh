#!/usr/bin/env bash
# ==============================================================================
# Script khởi chạy Qdrant Vector DB Server (High-Performance Native Service)
# Port: 6333 (HTTP REST) / 6334 (gRPC)
# ==============================================================================

set -euo pipefail

QDRANT_DIR="/home/infvn/qdrant_server"
DATA_DIR="${QDRANT_DIR}/storage"
mkdir -p "${DATA_DIR}"

if pgrep -x "qdrant" > /dev/null; then
    echo "Qdrant server is already running."
    exit 0
fi

echo "Starting Qdrant Server at http://localhost:6333 ..."
cd "${QDRANT_DIR}"
exec ./qdrant --uri "http://0.0.0.0:6333"
