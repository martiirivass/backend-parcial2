import requests, os, json
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

token = os.environ.get("MP_ACCESS_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"}

# Get ALL recent payments (limit 10)
resp = requests.get(
    "https://api.mercadopago.com/v1/payments/search",
    headers=headers,
    params={"limit": 10, "sort": "date_created", "criteria": "desc"},
    timeout=15
)
print(f"Status: {resp.status_code}")
data = resp.json()
results = data.get("results", [])
print(f"Total payments found: {data.get('paging', {}).get('total', 0)}")
for r in results:
    print(f"  ID={r.get('id')} status={r.get('status')} external_ref={r.get('external_reference')} amount={r.get('transaction_amount')}")
