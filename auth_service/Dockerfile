#auth_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the auth service and install it as a package
COPY ./auth_service /app/auth_service
COPY setup.py /app/
RUN pip install -e .

# Add the parent directory to PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8001
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

