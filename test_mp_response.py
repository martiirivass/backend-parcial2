import os, json
from dotenv import load_dotenv
load_dotenv('.env', override=True)
import requests

token = os.getenv('MP_ACCESS_TOKEN')
headers = {"Authorization": f"Bearer {token}"}

# Search for external_reference=32
resp = requests.get(
    "https://api.mercadopago.com/v1/payments/search",
    headers=headers,
    params={"external_reference": "32"},
    timeout=15
)
data = resp.json()
print("Keys:", list(data.keys()))
print("Results count:", len(data.get("results", [])))
r = data["results"][0]
print("Payment keys:", list(r.keys()))
print("ID:", r.get("id"), "type:", type(r.get("id")).__name__)
print("Status:", r.get("status"))
print("Amount:", r.get("transaction_amount"), "type:", type(r.get("transaction_amount")).__name__)
print("Date:", r.get("date_approved"), "type:", type(r.get("date_approved")).__name__)

# Check if external_reference is in the payment
print("external_reference:", r.get("external_reference"))
