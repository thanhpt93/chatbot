#!/usr/bin/env bash
# ==============================================================================
# Script khởi chạy vLLM Serving cho Groupware AI Chatbot
# Mô hình: Qwen2.5-7B-Instruct (hỗ trợ cả bản chuẩn BF16 hoặc bản AWQ 4-bit)
# ==============================================================================

set -euo pipefail

# Kích hoạt môi trường conda chat
CONDA_BASE="/home/infvn/miniconda3"
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate chat

# Cấu hình mặc định
PORT=${PORT:-8000}
HOST=${HOST:-"0.0.0.0"}
GPU_ID=${CUDA_VISIBLE_DEVICES:-"0"}

# Tùy chọn Model:
# 1. Bản AWQ 4-bit (Khuyên dùng cho card 12GB - VRAM ~5.5GB, dư dả KV cache dài):
#    MODEL_NAME="Qwen/Qwen2.5-7B-Instruct-AWQ"
# 2. Bản gốc BF16 (Chạy trên card 16GB có sẵn - VRAM ~15GB):
#    MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
MODEL_NAME=${1:-"Qwen/Qwen2.5-7B-Instruct-AWQ"}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEM_UTIL=${GPU_MEM_UTIL:-0.90}

echo "=========================================================="
echo " Starting vLLM Serving Server"
echo " Model:          ${MODEL_NAME}"
echo " Host:           ${HOST}:${PORT}"
echo " GPU Device:     ${GPU_ID}"
echo " Max Context:    ${MAX_MODEL_LEN} tokens"
echo " GPU Mem Util:   ${GPU_MEM_UTIL}"
echo "=========================================================="

export CUDA_VISIBLE_DEVICES="${GPU_ID}"

exec python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_NAME}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEM_UTIL}" \
    --trust-remote-code \
    --dtype auto \
    --enforce-eager
