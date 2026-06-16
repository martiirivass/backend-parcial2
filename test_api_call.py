"""Test the EXACT API call the frontend makes"""
import requests as r

BASE = "http://localhost:8001"

# 1) Login as admin first to check pedido owner
login = r.post(f"{BASE}/auth/login", json={
    "email": "gonzifracchia@gmail.com",
    "password": "gonzalo123"
})
print(f"Login: {login.status_code}")
cookie = login.cookies.get("access_token", "")
print(f"Cookie: {'present' if cookie else 'MISSING!'}")

# If no cookie from set-cookie, try getting it from response
if not cookie:
    for c in login.cookies:
        print(f"  Cookie: {c.name}={c.value}")

cookies = {"access_token": cookie}

# 2) Hit the pago status endpoint exactly like frontend does
for attempt in range(3):
    resp = r.get(f"{BASE}/api/v1/pagos/32", cookies=cookies, timeout=10)
    print(f"\nAttempt {attempt+1}: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Response: {data}")
        if data.get("status") == "approved":
            print("  >>> SYNC WORKED!")
            break
    else:
        print(f"  Error: {resp.text[:300]}")
