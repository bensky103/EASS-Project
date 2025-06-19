#app/Dockerfile

# 1. base image
FROM python:3.11-slim

# 2. set working directory
WORKDIR /app

# 3. copy & install dependencies first
COPY app/requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# 4. copy the entire app code
COPY app     ./app

# 5. expose port & run uvicorn against the package
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
