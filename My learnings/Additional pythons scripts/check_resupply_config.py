"""Check resupply configuration between branches in client-cient database."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def search_read(model, domain, fields, limit=100):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})
    except Exception as e:
        return f"Error: {e}"

print("=== WAREHOUSE RESUPPLY CONFIGURATION ===")
# Check warehouse resupply_wh_ids
warehouses = search_read('stock.warehouse', [], ['name', 'code', 'company_id', 'resupply_wh_ids'])
for wh in warehouses:
    resupply_names = []
    if wh.get('resupply_wh_ids'):
        for rwh_id in wh['resupply_wh_ids']:
            rwh = search_read('stock.warehouse', [['id', '=', rwh_id]], ['name', 'code', 'company_id'])
            if rwh:
                resupply_names.append(f"{rwh[0]['name']} ({rwh[0]['company_id'][1]})")
    print(f"\n  Warehouse: {wh['name']} ({wh['code']}) | Company: {wh['company_id'][1]}")
    print(f"    Resupply From: {', '.join(resupply_names) if resupply_names else 'NONE configured'}")

print("\n\n=== ALL STOCK ROUTES ===")
routes = search_read('stock.route', [], ['name', 'company_id', 'active', 'supplied_wh_id', 'supplier_wh_id'])
for r in routes:
    company = r.get('company_id', [False, 'All'])
    supplied = r.get('supplied_wh_id', [False, ''])
    supplier = r.get('supplier_wh_id', [False, ''])
    print(f"  Route: {r['name']} | Company: {company[1] if company else 'All'} | Active: {r.get('active', '?')}")
    if supplied and supplied[0]:
        print(f"    Supplied WH: {supplied[1]} | Supplier WH: {supplier[1] if supplier and supplier[0] else 'N/A'}")

print("\n\n=== INTER-COMPANY TRANSACTION SETTINGS ===")
# Check res.config.settings or ir.config_parameter for inter-company rules
params = search_read('ir.config_parameter', [['key', 'ilike', 'intercompany']], ['key', 'value'])
if params and not isinstance(params, str):
    for p in params:
        print(f"  {p['key']} = {p['value']}")
else:
    print(f"  Result: {params}")

# Check if inter-company rules model exists
print("\n\n=== INTER-COMPANY RULES (res.company) ===")
companies = search_read('res.company', [], [
    'name', 'parent_id', 
    'rule_type',           # might not exist
    'intercompany_user_id',
])
if companies and not isinstance(companies, str):
    for c in companies:
        print(f"  {c['name']}")
        for k, v in c.items():
            if k not in ('id', 'name'):
                print(f"    {k}: {v}")
else:
    print(f"  Result: {companies}")

print("\n\n=== STOCK RULES (PULL/PUSH) FOR RESUPPLY ROUTES ===")
# Get rules for routes that have supplier_wh_id
route_ids = [r['id'] for r in routes if r.get('supplier_wh_id') and r['supplier_wh_id'][0]]
if route_ids:
    rules = search_read('stock.rule', [['route_id', 'in', route_ids]], 
                        ['name', 'route_id', 'action', 'location_src_id', 'location_dest_id', 'company_id', 'picking_type_id'])
    for rule in rules:
        print(f"  Rule: {rule['name']}")
        print(f"    Route: {rule.get('route_id', ['',''])[1]} | Action: {rule.get('action')}")
        print(f"    From: {rule.get('location_src_id', ['',''])[1]} -> To: {rule.get('location_dest_id', ['',''])[1]}")
        print(f"    Company: {rule.get('company_id', ['','All'])[1]}")
else:
    print("  No resupply routes with supplier warehouse found")

print("\n\n=== CAN BRANCHES SEE EACH OTHER'S WAREHOUSES FOR RESUPPLY? ===")
# Check if Devika Furniture or KDESIGN INTERIOR warehouses have resupply configured
for wh in warehouses:
    if wh['company_id'][1] in ['Devika Furniture', 'KDESIGN INTERIOR', 'KDESIGN INTERIOR FURNISHING']:
        print(f"\n  {wh['name']} ({wh['company_id'][1]}):")
        print(f"    Resupply WH IDs: {wh.get('resupply_wh_ids', [])}")

print("\n\n=== DONE ===")
