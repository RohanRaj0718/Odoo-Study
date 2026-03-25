"""
Discover the correct database name for the Odoo instance
"""
import requests
import json

URL = "https://rohanraj0718-infintor.odoo.com"

# Method 1: Try the database list endpoint
try:
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "db",
            "method": "list",
            "args": []
        },
        "id": 1
    }
    resp = requests.post(f"{URL}/jsonrpc", json=payload)
    result = resp.json()
    print("Database list result:", json.dumps(result, indent=2))
except Exception as e:
    print(f"Method 1 failed: {e}")

# Method 2: Try the web/database/list endpoint
try:
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {},
        "id": 2
    }
    resp = requests.post(f"{URL}/web/database/list", json=payload)
    result = resp.json()
    print("\nWeb database list result:", json.dumps(result, indent=2))
except Exception as e:
    print(f"Method 2 failed: {e}")

# Method 3: Try common variations of the DB name
USERNAME = "rohanraj.infintor@gmail.com"
PASSWORD = "Virat@ronaldo1"

db_names = [
    "rohanraj0718-infintor-main-18321695",
    "rohanraj0718-infintor-main",
    "rohanraj0718_infintor",
    "main",
    "odoo",
]

for db in db_names:
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [db, USERNAME, PASSWORD, {}]
            },
            "id": 1
        }
        resp = requests.post(f"{URL}/jsonrpc", json=payload)
        result = resp.json()
        if result.get("result"):
            print(f"\n✓ SUCCESS with DB name: '{db}' -> UID: {result['result']}")
            break
        elif "error" in result:
            err_msg = result['error'].get('data', {}).get('name', '')
            print(f"✗ DB '{db}': {err_msg[:80]}")
    except Exception as e:
        print(f"✗ DB '{db}': {e}")

# Method 4: Try to get session info from web
try:
    session = requests.Session()
    # Login via web
    login_resp = session.post(f"{URL}/web/session/authenticate", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": "",
            "login": USERNAME,
            "password": PASSWORD,
        },
        "id": 3
    })
    result = login_resp.json()
    if result.get("result"):
        db_name = result["result"].get("db", "")
        uid = result["result"].get("uid", "")
        print(f"\n✓ Session authenticate - DB: '{db_name}', UID: {uid}")
    else:
        print(f"\nSession authenticate result: {json.dumps(result, indent=2)[:300]}")
except Exception as e:
    print(f"Method 4 failed: {e}")
