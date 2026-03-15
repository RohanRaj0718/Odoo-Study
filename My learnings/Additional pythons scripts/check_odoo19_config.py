"""Check Odoo 19 live database for multi-company and warehouse config"""
import xmlrpc.client

URL = "https://demo-company15.odoo.com"
DB = "demo-company15"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
version = common.version()
print(f"Odoo Version: {version.get('server_version', 'unknown')}")

uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f"UID: {uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Check companies
companies = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search_read', [[]], 
    {'fields': ['name', 'parent_id', 'currency_id']})
print("\n=== COMPANIES ===")
for c in companies:
    print(f"  {c['id']}: {c['name']} (Parent: {c['parent_id']}, Currency: {c['currency_id']})")

# Check warehouses
warehouses = models.execute_kw(DB, uid, PASSWORD, 'stock.warehouse', 'search_read', [[]], 
    {'fields': ['name', 'code', 'company_id', 'resupply_wh_ids', 'reception_steps', 'delivery_steps']})
print("\n=== WAREHOUSES ===")
for w in warehouses:
    print(f"  {w['id']}: {w['name']} (Code: {w['code']}, Company: {w['company_id']}, Resupply: {w['resupply_wh_ids']}, In: {w['reception_steps']}, Out: {w['delivery_steps']})")

# Check stock locations
locations = models.execute_kw(DB, uid, PASSWORD, 'stock.location', 'search_read', 
    [[['usage', 'in', ['internal', 'transit']]]], 
    {'fields': ['name', 'complete_name', 'usage', 'company_id', 'warehouse_id'], 'limit': 30})
print("\n=== STOCK LOCATIONS (Internal + Transit) ===")
for loc in locations:
    print(f"  {loc['id']}: {loc['complete_name']} (Usage: {loc['usage']}, Company: {loc['company_id']}, Warehouse: {loc['warehouse_id']})")

# Check key settings
print("\n=== KEY SETTINGS ===")
settings_fields = ['group_multi_company', 'group_stock_multi_locations', 'group_stock_multi_warehouses']
try:
    settings = models.execute_kw(DB, uid, PASSWORD, 'res.config.settings', 'default_get', [settings_fields])
    for k, v in settings.items():
        if k in settings_fields:
            print(f"  {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# Check installed modules
modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read', 
    [[['state', '=', 'installed'], ['name', 'in', [
        'base', 'account', 'sale', 'purchase', 'stock', 'mrp', 
        'sale_stock', 'purchase_stock', 'stock_account', 'analytic',
        'account_reports', 'sale_management'
    ]]]], 
    {'fields': ['name', 'shortdesc', 'installed_version']})
print("\n=== INSTALLED MODULES ===")
for m in modules:
    print(f"  {m['name']} v{m['installed_version']}: {m['shortdesc']}")

# Check warehouse fields available in Odoo 19
print("\n=== WAREHOUSE FIELDS (Odoo 19) ===")
try:
    wh_fields = models.execute_kw(DB, uid, PASSWORD, 'stock.warehouse', 'fields_get', [], 
        {'attributes': ['string', 'type']})
    interesting = ['resupply_wh_ids', 'route_ids', 'reception_route_id', 'delivery_route_id',
                   'crossdock_route_id', 'mto_pull_id', 'buy_pull_id', 'manufacture_pull_id',
                   'company_id', 'partner_id', 'manufacture_to_resupply', 'buy_to_resupply',
                   'active', 'code', 'reception_steps', 'delivery_steps']
    for field in interesting:
        if field in wh_fields:
            print(f"  {field}: {wh_fields[field]['string']} ({wh_fields[field]['type']})")
except Exception as e:
    print(f"  Error: {e}")

# Check inter-company module
print("\n=== INTER-COMPANY MODULE ===")
ic_modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read', 
    [[['name', 'like', 'inter_company']]], 
    {'fields': ['name', 'shortdesc', 'state', 'installed_version']})
for m in ic_modules:
    print(f"  {m['name']}: {m['shortdesc']} (State: {m['state']}, Version: {m['installed_version']})")

# Check routes
print("\n=== STOCK ROUTES ===")
routes = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read', [[]], 
    {'fields': ['name', 'active', 'company_id', 'product_selectable', 'warehouse_selectable', 'sale_selectable']})
for r in routes:
    print(f"  {r['id']}: {r['name']} (Active: {r['active']}, Company: {r['company_id']}, Product: {r['product_selectable']}, WH: {r['warehouse_selectable']}, Sale: {r['sale_selectable']})")

# Check analytic plans
print("\n=== ANALYTIC PLANS ===")
try:
    plans = models.execute_kw(DB, uid, PASSWORD, 'account.analytic.plan', 'search_read', [[]], 
        {'fields': ['name', 'company_id', 'parent_id']})
    for p in plans:
        print(f"  {p['id']}: {p['name']} (Company: {p['company_id']}, Parent: {p['parent_id']})")
except Exception as e:
    print(f"  Error: {e}")

# Check operation types
print("\n=== OPERATION TYPES ===")
op_types = models.execute_kw(DB, uid, PASSWORD, 'stock.picking.type', 'search_read', [[]], 
    {'fields': ['name', 'warehouse_id', 'code', 'company_id', 'reservation_method']})
for op in op_types:
    print(f"  {op['id']}: {op['name']} (WH: {op['warehouse_id']}, Code: {op['code']}, Company: {op['company_id']}, Reserve: {op['reservation_method']})")

print("\n=== DONE ===")
