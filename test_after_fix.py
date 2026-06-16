import requests as r
for name, url in [('Backend','http://localhost:8001/docs'),('Store','http://localhost:5174'),('Admin','http://localhost:5173')]:
    try:
        resp = r.get(url, timeout=5)
        print(f'{name}: OK ({resp.status_code})')
    except Exception as e:
        print(f'{name}: FAIL')

print()
try:
    resp = r.post('http://localhost:5174/auth/login', json={'email':'gonzifracchia@gmail.com','password':'test123'}, timeout=10)
    print(f'Login via store proxy: {resp.status_code}')
    if resp.status_code == 200:
        cookie = resp.cookies.get('access_token', '')[:30]
        print(f'  OK - cookie: {cookie}...')
    else:
        print(f'  Body: {resp.text[:200]}')
except Exception as e:
    print(f'Login via store proxy: FAIL ({type(e).__name__})')
