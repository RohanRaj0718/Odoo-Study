import json
import requests
import sys

URL = "https://rohanraj0718-infintor.odoo.com"
DB = "rohanraj0718-infintor-main-29796979"
USERNAME = "rohanraj.infintor@gmail.com"
PASSWORD = "Virat@ronaldo1"

def main():
    session = requests.Session()
    session.post(f"{URL}/web/session/authenticate", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"db": DB, "login": USERNAME, "password": PASSWORD},
        "id": 1
    })
    
    # Let's search specifically for 'agra' or 'kullu' in website.page
    for search_term in ["agra", "kullu", "manali", "delhi"]:
        search_resp = session.post(f"{URL}/web/dataset/call_kw", json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "website.page",
                "method": "search_read",
                "args": [[["url", "ilike", search_term]]],
                "kwargs": {"fields": ["id", "name", "url", "view_id"]}
            },
            "id": 2
        })
        pages = search_resp.json().get("result", [])
        if pages:
            print(f"--- Pages matching '{search_term}' ---")
            for p in pages:
                print(f"Page ID={p['id']}, Name={p.get('name')}, URL={p.get('url')}, View ID={p.get('view_id')}")
        
if __name__ == "__main__":
    main()
