# tests/conftest.py
import pytest, socket, time, subprocess
import httpx

COMPOSE_FILE = "docker-compose.yml"

@pytest.fixture(scope="session", autouse=True)
def _stack_up_and_wait():
    
    # wait for auth:8001 and stock:8002 and app:8000
    for port in (8001, 8002, 8000):
        for _ in range(30):
            try:
                s = socket.create_connection(("localhost", port), timeout=1)
                s.close()
                break
            except OSError:
                time.sleep(1)
        else:
            pytest.exit(f"Service on port {port} never became ready")
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
