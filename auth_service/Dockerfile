#auth_service/Dockerfile

FROM python:3.11-slim
WORKDIR /app
COPY ./auth_service /app/auth_service
RUN pip install fastapi uvicorn motor pydantic[email] passlib[bcrypt] pyjwt
EXPOSE 8001
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

