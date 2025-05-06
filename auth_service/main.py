from fastapi import FastAPI
from auth_service.routers.auth import router as auth_router
from auth_service.routers.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auth Service")
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)

