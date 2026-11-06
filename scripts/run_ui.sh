#!/usr/bin/env bash
# ==============================================================================
# Script khởi chạy Giao diện Chatbot (Web UI)
# Cổng mặc định: 8080 (Truy cập: http://localhost:8080)
# ==============================================================================

set -euo pipefail

CONDA_BASE="/home/infvn/miniconda3"
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate chat

PORT=${PORT:-8080}
HOST=${HOST:-"0.0.0.0"}
export CUDA_VISIBLE_DEVICES=1

echo "=========================================================="
echo " Khởi chạy Giao diện Groupware AI Chatbot Web UI"
echo " Địa chỉ truy cập: http://localhost:${PORT}"
echo " Endpoint vLLM:     http://localhost:8000/v1"
echo "=========================================================="

exec python scripts/chat_ui.py --host "${HOST}" --port "${PORT}"
