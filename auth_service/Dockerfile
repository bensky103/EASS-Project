#auth_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app

# copy only requirements first
COPY auth_service/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt    

COPY ./auth_service /app/auth_service

EXPOSE 8001
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

