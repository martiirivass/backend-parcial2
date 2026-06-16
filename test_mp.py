import mercadopago, uuid, os, json
from pathlib import Path

env_path = Path(".env")
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

token = os.environ.get("MP_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(token)

pref_data = {
    "items": [{
        "title": "Test Item",
        "quantity": 1,
        "unit_price": 100.0,
        "currency_id": "ARS"
    }],
    "external_reference": str(uuid.uuid4()),
    "back_urls": {
        "success": "https://localhost:5174/pago-exitoso",
        "failure": "https://localhost:5174/pago-fallido",
        "pending": "https://localhost:5174/pago-pendiente"
    },
    "auto_return": "approved",
}

try:
    response = sdk.preference().create(pref_data)
    resp = response["response"]
    print(f"Status: {response['status']}")
    print(f"Preference ID: {resp.get('id')}")
    print(f"Init point: {resp.get('init_point')}")
    print(f"Back URLs: {resp.get('back_urls')}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
