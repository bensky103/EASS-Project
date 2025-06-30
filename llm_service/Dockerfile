# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy setup.py from project root to /app
COPY ../setup.py ./

# Install the package in development mode
RUN pip install -e .


# Copy ollama-entrypoint.sh from the project root to the Docker image
COPY ../ollama-entrypoint.sh ./ollama-entrypoint.sh
RUN chmod +x ollama-entrypoint.sh

# Expose the port the app runs on
EXPOSE 8003

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "llm_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

# ENTRYPOINT removed; docker-compose.yml will set the entrypoint 