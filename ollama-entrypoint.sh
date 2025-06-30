#!/bin/sh
set -e

echo "[Entrypoint] Starting Ollama server in background..."
ollama serve &
OLLAMA_PID=$!

# Wait for the server to be ready using nc (netcat)
if command -v nc > /dev/null; then
  until nc -z localhost 11434; do
    echo "Waiting for Ollama server to be ready (using nc)..."
    sleep 2
  done
else
  echo "Warning: nc (netcat) not found. Proceeding after 10 seconds, but Ollama server readiness is not guaranteed."
  sleep 10
fi

echo "[Entrypoint] Pulling llama3 model..."
ollama pull llama3

echo "[Entrypoint] Ready. Bringing Ollama server to foreground."
wait $OLLAMA_PID 