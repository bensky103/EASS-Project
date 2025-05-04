FROM python:3.11-slim
WORKDIR /app
COPY ./stock_service /app
RUN pip install fastapi uvicorn httpx python-dotenv
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

