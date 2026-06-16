import requests, json, os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

token = os.getenv("MP_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

# Check MP API has the payment
resp = requests.get(
    "https://api.mercadopago.com/v1/payments/search",
    headers=headers,
    params={"external_reference": "32"},
    timeout=15
)
results = resp.json().get("results", [])
if results:
    r = results[0]
    print(f"MP payment: id={r.get('id')} status={r.get('status')}")
else:
    print("No MP payment found for external_reference=32")
    exit()

# Call the backend endpoint
# First login as the client
login_resp = requests.post("http://localhost:8001/auth/login", json={
    "email": "gonzifracchia@gmail.com",
    "password": "gonzalo123"
})
print(f"Login: {login_resp.status_code}")
if login_resp.status_code == 200:
    cookie = login_resp.cookies.get("access_token", "")
    h = {"Cookie": f"access_token={cookie}"}
    r2 = requests.get("http://localhost:8001/api/v1/pagos/32", headers=h)
    print(f"Pago status: {r2.status_code} - {r2.text[:500]}")
else:
    print(f"Login failed: {login_resp.json()}")
