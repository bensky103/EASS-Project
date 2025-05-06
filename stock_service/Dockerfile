#stock_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app
COPY ./stock_service /app/stock_service
RUN pip install fastapi uvicorn httpx python-dotenv
EXPOSE 8002
CMD ["uvicorn", "stock_service.main:app", "--host", "0.0.0.0", "--port", "8002"]

