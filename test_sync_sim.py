import sys; sys.path.insert(0, '.')
from app.db.database import engine
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv('.env', override=True)
import os, requests
from datetime import datetime, timezone

token = os.getenv('MP_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

resp = requests.get(
    'https://api.mercadopago.com/v1/payments/search',
    headers=headers,
    params={'external_reference': '32'},
    timeout=15
)
print(f'Search status: {resp.status_code}')
data = resp.json()
results = data.get('results', [])
print(f'Results: {len(results)}')

if results:
    r = results[0]
    pid = r.get('id')
    status = r.get('status')
    amount = r.get('transaction_amount')
    print(f'ID: {pid} type: {type(pid).__name__}')
    print(f'Status: {status}')
    print(f'Amount: {amount} type: {type(amount).__name__}')
    print(f'Date: {r.get("date_approved")}')

    with engine.connect() as conn:
        conn.execute(text(
            'UPDATE pagos SET mp_payment_id = :mid, mp_status = :s, transaction_amount = :a WHERE external_reference = :ref'
        ), {
            'mid': pid,
            's': status,
            'a': amount,
            'ref': '32'
        })
        conn.commit()
        print('DB update successful!')
