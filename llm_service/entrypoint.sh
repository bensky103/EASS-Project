#!/bin/sh
set -e

OLLAMA_HOST=${OLLAMA_HOST:-http://eass_ollama:11434}
OLLAMA_MODEL=${OLLAMA_MODEL:-llama3}

# Wait for Ollama service to be ready
MAX_ATTEMPTS=30
SLEEP_TIME=5
ATTEMPT=1

until curl -sf "$OLLAMA_HOST/api/tags" | grep -q "$OLLAMA_MODEL"; do
  echo "[Entrypoint] Waiting for Ollama ($OLLAMA_HOST) and model '$OLLAMA_MODEL' to be ready... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
  ATTEMPT=$((ATTEMPT+1))
  if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "[Entrypoint] Ollama or model '$OLLAMA_MODEL' not ready after $MAX_ATTEMPTS attempts. Exiting."
    exit 1
  fi
  sleep $SLEEP_TIME
done

echo "[Entrypoint] Ollama and model '$OLLAMA_MODEL' are ready. Starting LLM service..."

# Start the FastAPI server
exec uvicorn llm_service.main:app --host 0.0.0.0 --port 8003
