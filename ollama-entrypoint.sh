#!/bin/sh
set -e

echo "[Entrypoint] Pulling llama3 model..."
ollama pull llama3

echo "[Entrypoint] Pre-loading llama3 model into memory..."
ollama run llama3 </dev/null || true

echo "[Entrypoint] Starting Ollama server..."
exec serve 