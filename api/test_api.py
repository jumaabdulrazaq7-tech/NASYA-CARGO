"""
================================================================
NASYA CARGO — API Test Script
Run this to verify the API is working correctly

Usage:
    python test_api.py
    python test_api.py --url http://your-server.com:5000
================================================================
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:5000'

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
RESET  = '\033[0m'
BOLD   = '\033[1m'


def test(name, passed, detail=''):
    icon = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
    print(f"  {icon}  {name}")
    if detail:
        print(f"      {YELLOW}{detail}{RESET}")


def request_json(method, path, body=None):
    url  = BASE_URL + path
    data = json.dumps(body).encode() if body else None
    headers = {'Content-Type': 'application/json'}
    req  = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {'error': str(e)}


print(f"\n{BOLD}{'='*50}")
print(f"  NASYA CARGO API — Test Suite")
print(f"  URL: {BASE_URL}")
print(f"{'='*50}{RESET}\n")

# ── Test 1: Health Check ──────────────────────────────────────
print(f"{BOLD}1. Health Check{RESET}")
status, data = request_json('GET', '/api/health')
test('API is online',           status == 200,           f"Status: {status}")
test('Returns success response', data.get('status') == 'online', str(data))
print()

# ── Test 2: Submit Quote ──────────────────────────────────────
print(f"{BOLD}2. Submit Quote (POST /api/quote){RESET}")
quote_payload = {
    "name":        "Ahmed Al-Rashid",
    "email":       "ahmed@example.com",
    "phone":       "+971 54 000 0000",
    "company":     "Al-Rashid Trading LLC",
    "cargo_type":  "Electronics & Gadgets",
    "ship_mode":   "Sea Freight — FCL (Full Container)",
    "origin":      "Dubai, UAE",
    "destination": "Dar es Salaam, Tanzania",
    "weight":      "2500",
    "volume":      "14",
    "cargo_value": "$5,000 – $20,000",
    "notes":       "Fragile items, handle with care"
}
status, data = request_json('POST', '/api/quote', quote_payload)
test('Quote submitted successfully',  status == 201,               f"Status: {status}")
test('Returns quote reference',        'quote_ref' in data,         data.get('quote_ref',''))
test('Returns success flag',           data.get('success') == True, str(data))
quote_ref = data.get('quote_ref', '')
print()

# ── Test 3: Validation ────────────────────────────────────────
print(f"{BOLD}3. Validation (missing fields){RESET}")
status, data = request_json('POST', '/api/quote', {"name": "Test Only"})
test('Rejects incomplete form',    status == 422,               f"Status: {status}")
test('Returns error message',      'error' in data,             data.get('error',''))
print()

# ── Test 4: List Quotes ───────────────────────────────────────
print(f"{BOLD}4. List Quotes (GET /api/quotes){RESET}")
status, data = request_json('GET', '/api/quotes')
test('Returns quotes list',    status == 200,             f"Status: {status}")
test('Has total count',        'total' in data,           f"Total: {data.get('total','?')}")
test('Has quotes array',       isinstance(data.get('quotes'), list), '')
print()

# ── Test 5: Get Stats ─────────────────────────────────────────
print(f"{BOLD}5. Dashboard Stats (GET /api/stats){RESET}")
status, data = request_json('GET', '/api/stats')
test('Returns stats',      status == 200,      f"Status: {status}")
test('Has total stat',     'total' in data.get('stats',{}), str(data.get('stats',{})))
test('Has new stat',       'new'   in data.get('stats',{}), '')
print()

# ── Summary ───────────────────────────────────────────────────
print(f"{BOLD}{'='*50}")
print(f"  Tests complete!")
print(f"  Quote submitted: {quote_ref}")
print(f"{'='*50}{RESET}\n")
