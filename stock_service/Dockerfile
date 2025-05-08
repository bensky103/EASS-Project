#stock_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app

# copy only requirements first
COPY stock_service/requirements.txt ./requirements.txt   
RUN pip install --upgrade pip && \
    pip install -r requirements.txt                      

COPY ./stock_service /app/stock_service
EXPOSE 8002
CMD ["uvicorn", "stock_service.main:app", "--host", "0.0.0.0", "--port", "8002"]

