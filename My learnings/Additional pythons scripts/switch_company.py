"""
Switch user's default company to Devika Furniture (2) via API,
then verify Shop Floor via Playwright.
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def x(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kw)

# Switch user's company to Devika Furniture (id=2)
print("Switching default company to Devika Furniture (id=2)...")
try:
    x('res.users', 'write', [[uid], {'company_id': 2}])
    print("  ✓ Done")
except Exception as e:
    print(f"  Error: {e}")

# Verify
user = x('res.users', 'search_read', [[['id', '=', uid]]], {'fields': ['company_id']})
print(f"  Current company: {user[0]['company_id']}")
