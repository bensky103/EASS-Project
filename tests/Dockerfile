# tests/Dockerfile 
FROM python:3.11-slim

WORKDIR /code

# Copy the root requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

ENV PYTHONPATH=/code

# Copy the rest of the repo
COPY . /code

CMD ["pytest", "-q"]
