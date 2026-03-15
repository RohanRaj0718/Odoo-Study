"""Gather remaining data needed for setup"""
import xmlrpc.client
URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
U = "rohan.raj@infintor.com"
P = "Rohanraj@1"
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, U, P, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Check taxes including inactive
print("=== ALL TAXES ===")
taxes = m.execute_kw(DB, uid, P, 'account.tax', 'search_read', [[]], 
    {'fields': ['name', 'type_tax_use', 'amount', 'company_id', 'active', 'price_include'], 'limit': 50})
for t in taxes:
    print(f"  {t['id']}: {t['name']} (use={t['type_tax_use']}, rate={t['amount']}%, active={t['active']})")

# Check product categories
print("\n=== PRODUCT CATEGORIES ===")
cats = m.execute_kw(DB, uid, P, 'product.category', 'search_read', [[]], 
    {'fields': ['name', 'complete_name', 'parent_id'], 'limit': 20})
for c in cats:
    print(f"  {c['id']}: {c['complete_name']}")

# Check country/state for India
print("\n=== INDIAN STATES (Kerala, Karnataka, Tamil Nadu) ===")
india = m.execute_kw(DB, uid, P, 'res.country', 'search', [[['code', '=', 'IN']]])
print(f"  India country ID: {india}")
states = m.execute_kw(DB, uid, P, 'res.country.state', 'search_read', 
    [[['country_id', '=', india[0]], ['code', 'in', ['KL', 'KA', 'TN']]]], 
    {'fields': ['name', 'code', 'country_id']})
for s in states:
    print(f"  {s['id']}: {s['name']} ({s['code']})")

# Check config settings fields
print("\n=== CONFIG SETTINGS KEY FIELDS ===")
try:
    sf = m.execute_kw(DB, uid, P, 'res.config.settings', 'fields_get', [], 
        {'attributes': ['string', 'type']})
    for f in sorted(sf.keys()):
        fname = f.lower()
        if any(kw in fname for kw in ['multi', 'location', 'route', 'warehouse', 'analytic', 'margin', 'pricelist', 'inter_company']):
            print(f"  {f}: {sf[f]['string']} ({sf[f]['type']})")
except Exception as e:
    print(f"  Error: {e}")

# Check stock.location fields
print("\n=== STOCK.LOCATION KEY FIELDS ===")
lf = m.execute_kw(DB, uid, P, 'stock.location', 'fields_get', [], {'attributes': ['string', 'type']})
for f in ['name', 'complete_name', 'location_id', 'usage', 'company_id', 'warehouse_id', 'active', 'replenish_location', 'barcode']:
    if f in lf:
        print(f"  {f}: {lf[f]['string']} ({lf[f]['type']})")

# Check analytic plan fields 
print("\n=== ANALYTIC PLAN FIELDS ===")
try:
    apf = m.execute_kw(DB, uid, P, 'account.analytic.plan', 'fields_get', [], {'attributes': ['string', 'type']})
    for f in sorted(apf.keys()):
        if not f.startswith('_'):
            print(f"  {f}: {apf[f]['string']} ({apf[f]['type']})")
except Exception as e:
    print(f"  Error: {e}")

print("\nDONE")
