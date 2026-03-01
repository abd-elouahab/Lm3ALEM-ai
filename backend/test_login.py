"""Verify login works with new passwords."""
import sys
sys.path.insert(0, '.')
import urllib.request, urllib.parse, json

base = 'http://localhost:8000'

def test_login(email, password, label):
    data = urllib.parse.urlencode({'username': email, 'password': password}).encode()
    req = urllib.request.Request(
        f'{base}/auth/login',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            resp = json.loads(r.read().decode())
            print(f'✅ {label}: LOGIN OK (token: {resp["access_token"][:20]}...)')
            return resp.get('access_token')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'❌ {label}: {e.code} {body[:100]}')
    except Exception as e:
        print(f'❌ {label}: {e}')
    return None

print('Testing logins with new passwords:')
test_login('ahmed.zlayji@example.com', 'maalem123', 'Artisan: ahmed.zlayji')
test_login('client1@test.com', 'client123', 'Client: client1')
test_login('driss.electricien@example.com', 'maalem123', 'Artisan: driss.electricien')
