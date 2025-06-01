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

# Copy the rest of the application
COPY llm_service /app/llm_service
COPY llm_service/entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose the port the app runs on
EXPOSE 8003

# Use the entrypoint script
ENTRYPOINT ["./entrypoint.sh"] 