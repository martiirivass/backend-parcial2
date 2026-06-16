from dotenv import load_dotenv; load_dotenv('.env')
import os, requests
h = {'Authorization': f'Bearer {os.getenv("MP_ACCESS_TOKEN")}'}
r = requests.get('https://api.mercadopago.com/v1/payments/search', headers=h, params={'external_reference': '33'}, timeout=15)
results = r.json().get('results', [])
print(f'Results: {len(results)}')
if results:
    print(f'  ID={results[0]["id"]} status={results[0]["status"]} amount={results[0]["transaction_amount"]}')
else:
    print('  No payment found in MP for external_reference=33')
