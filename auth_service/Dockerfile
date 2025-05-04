FROM python:3.11-slim
WORKDIR /app
COPY ./auth_service /app
RUN pip install fastapi uvicorn motor pydantic passlib[bcrypt] pyjwt
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

