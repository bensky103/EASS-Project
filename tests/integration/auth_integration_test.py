import httpx, pytest, uuid

BASE = "http://eass_auth:8001"

def unique_email():
    return f"u{uuid.uuid4().hex[:8]}@test.local"

def test_register_and_login(http):
    email = unique_email()
    pw = "pass123"

    # register
    r = http.post(f"{BASE}/auth/register", json={"email": email, "password": pw})
    assert r.status_code == 201

    # login
    r = http.post(f"{BASE}/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token.startswith("ey")  # simple smoke check

    # access watchlist (should be empty)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    r = http.get(f"{BASE}/user/watchlist", headers=headers)
    if r.status_code != 200:
        print(f"Error response: {r.text}")
    assert r.status_code == 200
    assert isinstance(r.json(), list)  # Should return empty list

