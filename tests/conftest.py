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
    print(f"Waiting for service {service} on {base_url}{endpoint} for {timeout}s...")
    while True:
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=5)
            response.raise_for_status()
            print(f"Service {service}:{port}{endpoint} responded with {response.status_code}. Ready.")
            return
        except httpx.TransportError as e:
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for {service}:{port}{endpoint}. Last transport error: {e}")
                pytest.exit(f"Service {service} on port {port} (endpoint {endpoint}) never became ready. Last transport error: {e}")
            time.sleep(1)
        except Exception as e:
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for {service}:{port}{endpoint}. Last unexpected error: {e}")
                pytest.exit(f"Service {service} on port {port} (endpoint {endpoint}) failed with unexpected error: {e}")
            time.sleep(1)

# @pytest.fixture(scope="session", autouse=True)
# def _stack_up_and_wait():
#     print("Starting service readiness checks...")
#     wait_for_http_service("eass_auth", 8001, timeout=60)
#     wait_for_http_service("stock_data_fetching", 8000)
#     wait_for_http_service("llm_service", 8003)
#     print("All services reported ready.")
#     yield

# ── 2. sync client (simple tests) ───────────────────────────────────
@pytest.fixture
def http():
    """Synchronous httpx client (handy for simple GET/POST)."""
    with httpx.Client(base_url="http://auth:8001") as c:
        yield c


# ── 3. async client (pytest‑asyncio tests) ──────────────────────────
@pytest.fixture
async def ahttp():
    async with httpx.AsyncClient(base_url="http://auth:8001") as c:
        yield c
