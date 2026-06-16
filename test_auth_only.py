import requests as r, time

BASE = "http://localhost:8001"

# Test root or health
t0 = time.time()
try:
    resp = r.get(f"{BASE}/docs", timeout=5)
    print(f"GET /docs -> {resp.status_code} ({time.time()-t0:.2f}s)")
except Exception as e:
    print(f"GET /docs FAILED: {e} ({time.time()-t0:.2f}s)")

# Test login with wrong password first (should be fast 401)
t0 = time.time()
try:
    resp = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": "wrongpassword"}, timeout=10)
    print(f"Login wrong pw -> {resp.status_code} ({time.time()-t0:.2f}s)")
    if resp.status_code != 401:
        print(f"  Body: {resp.text[:200]}")
except Exception as e:
    print(f"Login wrong pw FAILED: {e} ({time.time()-t0:.2f}s)")

# Test login with actual pw
t0 = time.time()
try:
    resp = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": "gonzalo123"}, timeout=15)
    print(f"Login correct pw -> {resp.status_code} ({time.time()-t0:.2f}s)")
    if resp.status_code == 200:
        cookie = resp.cookies.get("access_token", "")
        print(f"  Cookie: {cookie[:30] if cookie else 'MISSING!'}...")
    else:
        print(f"  Body: {resp.text[:300]}")
except Exception as e:
    print(f"Login correct pw FAILED: {e} ({time.time()-t0:.2f}s)")

# Test pago status
t0 = time.time()
try:
    resp = r.get(f"{BASE}/api/v1/pagos/33", timeout=15)
    print(f"GET /api/v1/pagos/33 (no auth) -> {resp.status_code} ({time.time()-t0:.2f}s)")
    print(f"  Body: {resp.text[:200]}")
except Exception as e:
    print(f"GET /api/v1/pagos/33 FAILED: {e} ({time.time()-t0:.2f}s)")
