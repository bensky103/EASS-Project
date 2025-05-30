#!/bin/bash

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
while ! curl -s http://ollama:11434/api/version > /dev/null; do
    sleep 1
done

# Pull the LLaMA model
echo "Pulling LLaMA 3 model..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3"}'

# Start the FastAPI service
echo "Starting LLM service..."
exec uvicorn llm_service.main:app --host 0.0.0.0 --port 8003