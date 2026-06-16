import requests, os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

token = os.getenv("MP_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

# Search for external_reference=32
resp = requests.get(
    "https://api.mercadopago.com/v1/payments/search",
    headers=headers,
    params={"external_reference": "32"},
    timeout=15
)
print(f"Status: {resp.status_code}")
data = resp.json()
results = data.get("results", [])
if results:
    for r in results:
        print(f"Found: ID={r.get('id')} status={r.get('status')} amount={r.get('transaction_amount')}")
else:
    print(f"No payments found for external_reference=32")
    print(f"Total results: {data.get('paging', {}).get('total', 0)}")
