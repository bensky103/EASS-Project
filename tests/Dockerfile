# tests/Dockerfile 
FROM python:3.11-slim

WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy setup.py from project root to /code
COPY ../setup.py ./

# Copy the entire project
COPY . /code/

# Install the package in development mode
RUN pip install -e .

ENV PYTHONPATH=/code

CMD ["pytest", "-q"]
