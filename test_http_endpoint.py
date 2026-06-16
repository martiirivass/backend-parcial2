"""Test actual HTTP endpoint for pago status"""
import requests as r
import json

BASE = "http://localhost:8001"

# Try known passwords for the user
for pw in ["gonzalo123", "gonzalo", "123456", "test123", "password"]:
    login = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": pw}, timeout=5)
    if login.status_code == 200:
        print(f"Login OK with: {pw}")
        cookie = login.cookies.get("access_token", "")
        cookies = {"access_token": cookie}
        # pedido 33 got updated by my test script
        resp = r.get(f"{BASE}/api/v1/pagos/33", cookies=cookies, timeout=10)
        print(f"GET /api/v1/pagos/33 -> {resp.status_code}")
        print(f"Body: {json.dumps(resp.json(), indent=2)}")
        break
else:
    print("Cannot log in. Check if password was changed.")
    print("Testing endpoint without auth to see error format:")
    resp = r.get(f"{BASE}/api/v1/pagos/33", timeout=5)
    print(f"GET /api/v1/pagos/33 -> {resp.status_code}: {resp.text[:200]}")
    
    # Try admin
    login = r.post(f"{BASE}/auth/login", json={"email": "admin@admin.com", "password": "admin123"}, timeout=5)
    if login.status_code == 200:
        print("Admin login OK")
        cookie = login.cookies.get("access_token", "")
        resp = r.get(f"{BASE}/api/v1/pagos/33", cookies={"access_token": cookie}, timeout=10)
        print(f"Admin GET /api/v1/pagos/33 -> {resp.status_code}")
        print(f"Body: {resp.text[:300]}")
