# tests/conftest.py
import pytest, socket, time, subprocess
import httpx
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_data_fetching.main import app as stock_app
from llm_service.main import app as llm_app

COMPOSE_FILE = "docker-compose.yml"

def wait_for_http_service(service: str, port: int, endpoint: str = "/health", timeout: int = 30):
    # Use service name instead of localhost for Docker networking
    base_url = f"http://{service}:{port}"
    start_time = time.time()
    while True:
        try:
            response = httpx.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                return
        except (httpx.RequestError, ConnectionError):
            if time.time() - start_time > timeout:
                pytest.exit(f"Service {service} on port {port} never became ready")
            time.sleep(1)

@pytest.fixture(scope="session")
def _stack_up_and_wait():
    wait_for_http_service("auth", 8001)
    wait_for_http_service("stock_data_fetching", 8000)
    wait_for_http_service("llm_service", 8003)
    yield

# ── 2. sync client (simple tests) ───────────────────────────────────
@pytest.fixture
def http():
    """Synchronous httpx client (handy for simple GET/POST)."""
    with httpx.Client(base_url="http://localhost:8001") as c:
        yield c


# ── 3. async client (pytest‑asyncio tests) ──────────────────────────
@pytest.fixture
async def ahttp():
    async with httpx.AsyncClient(base_url="http://localhost:8001") as c:
        yield c
