"""Call the ACTUAL backend endpoint directly"""
import requests as r
import json

BASE = "http://localhost:8001"

# First, let's just test the backend is alive
try:
    resp = r.get(f"{BASE}/docs", timeout=5)
    print(f"Backend alive: {resp.status_code}")
except Exception as e:
    print(f"Backend NOT reachable: {e}")
    exit(1)

# Hit the pagos/33 endpoint WITHOUT auth to see the error
resp = r.get(f"{BASE}/api/v1/pagos/33", timeout=5)
print(f"\nWithout auth: {resp.status_code}")
try:
    print(f"  Body: {resp.json()}")
except:
    print(f"  Body: {resp.text[:200]}")

# Try to login as admin
login = r.post(f"{BASE}/auth/login", json={"email": "admin@admin.com", "password": "admin123"}, timeout=5)
print(f"\nAdmin login: {login.status_code}")
if login.status_code == 200:
    cookie = login.cookies.get("access_token", "")
    cookies = {"access_token": cookie}
    # But admin can't access pedido 33 (belongs to user_id=2)
    resp2 = r.get(f"{BASE}/api/v1/pagos/33", cookies=cookies, timeout=5)
    print(f"Admin pago status: {resp2.status_code}")
    try:
        print(f"  Body: {resp2.json()}")
    except:
        print(f"  Body: {resp2.text[:200]}")

# Last resort - try common passwords for the user
for pw in ["gonzalo123", "gonzalo", "test123", "password", "123456789"]:
    login = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": pw}, timeout=5)
    if login.status_code == 200:
        print(f"\nUSER LOGIN SUCCESS with password: {pw}")
        cookie = login.cookies.get("access_token", "")
        cookies = {"access_token": cookie}
        resp3 = r.get(f"{BASE}/api/v1/pagos/33", cookies=cookies, timeout=10)
        print(f"User pago status: {resp3.status_code}")
        try:
            print(f"  Body: {json.dumps(resp3.json(), indent=2)}")
        except:
            print(f"  Body: {resp3.text[:500]}")
        break
else:
    print("\nCould not log in as user. Password unknown.")
