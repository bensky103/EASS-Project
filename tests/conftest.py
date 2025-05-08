# tests/conftest.py
import pytest, socket, time, subprocess
import httpx

COMPOSE_FILE = "docker-compose.yml"

def wait_for_http_service(service: str, port: int, endpoint: str = "/health", timeout: int = 30):
    base_url = f"http://{service}:{port}"  # Changed to use service name and port correctly
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

@pytest.fixture(scope="session", autouse=True)
def _stack_up_and_wait():
    # Fixed the order of parameters (service name, port)
    wait_for_http_service("auth", 8001)  # Changed from "auth", 8001 to correct order
    wait_for_http_service("stock", 8002)
    wait_for_http_service("model", 8000)
    yield
    

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
