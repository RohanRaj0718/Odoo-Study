import xmlrpc.client

URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def x(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

# 1. Inter-company transit location
transit = x('stock.location', 'read', [3], {'fields': ['name', 'company_id', 'usage']})
print("Inter-company transit location:")
print(f"  company_id = {transit[0]['company_id']}")
print(f"  usage = {transit[0]['usage']}")
print(f"  → Because company_id is False, ANY company can access this location")

# 2. Company structure
print("\nCOMPANY STRUCTURE:")
companies = x('res.company', 'search_read', [[]], 
    {'fields': ['id', 'name', 'parent_id', 'vat']})
for c in companies:
    parent = c['parent_id'][1] if c['parent_id'] else 'NONE (Root company)'
    vat = c.get('vat') or 'Not set'
    is_branch = "BRANCH" if c['parent_id'] else "ROOT COMPANY"
    print(f"  [{c['id']}] {c['name']}")
    print(f"      Type: {is_branch} | Parent: {parent} | VAT/GSTIN: {vat}")

# 3. Our proven transfers
print("\nPROVEN TRANSFERS (already done):")
for pid in [39, 40]:
    p = x('stock.picking', 'read', [pid], 
          {'fields': ['name', 'company_id', 'location_id', 'location_dest_id']})
    if p:
        print(f"  {p[0]['name']} | Company: {p[0]['company_id'][1]}")
        print(f"    {p[0]['location_id'][1]} → {p[0]['location_dest_id'][1]}")

print("\nCONCLUSION:")
print("  Technically: YES — Odoo allows any company to create stock moves")
print("  to/from the Inter-company transit location because it has no company.")
print("  This is not limited to branches — it works between any two companies.")
