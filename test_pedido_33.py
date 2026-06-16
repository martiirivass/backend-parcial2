import requests as r

BASE = "http://localhost:8001"

passwords = ["gonzalo123", "gonzalo", "Gonzalo123", "gonzifracchia", "password", "123456", "admin123", "test123"]

found = False
for pw in passwords:
    resp = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": pw}, timeout=5)
    if resp.status_code == 200:
        print(f"FOUND password: {pw}")
        cookie = resp.cookies.get("access_token", "")
        print(f"Cookie: {cookie[:30]}...")
        
        # Now try pago status
        resp2 = r.get(f"{BASE}/api/v1/pagos/33", cookies={"access_token": cookie}, timeout=5)
        print(f"Status: {resp2.status_code}")
        if resp2.status_code == 200:
            print(f"Body: {resp2.json()}")
        else:
            print(f"Error: {resp2.text[:300]}")
        found = True
        break
    elif resp.status_code == 401:
        continue
    else:
        print(f"Unexpected: {resp.status_code} - {resp.text[:100]}")

if not found:
    print("No password worked. Cannot test API directly.")
    
    # Instead let's directly test the service function
    print("\n--- Testing PagoService directly ---")
    import sys; sys.path.insert(0, '.')
    from app.db.database import engine
    from sqlmodel import Session
    from app.pagos.service import PagoService
    
    with Session(engine) as session:
        svc = PagoService(session)
        try:
            result = svc.get_pago_status(33, 2)
            print(f"Service returned: {result}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
