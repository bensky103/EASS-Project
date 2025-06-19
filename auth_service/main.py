from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth_service.routers.auth import router as auth_router
from auth_service.routers.user import router as user_router

app = FastAPI(title="Auth Service")

@app.get("/", tags=["root"])
async def root():
    return {"status": "ok"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
