from fastapi import FastAPI
from stock_service.routes.stock import router as stock_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stock-Data Service")
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(stock_router)

