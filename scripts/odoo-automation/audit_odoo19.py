"""
Audit the Odoo 19 database at demo-tech.odoo.com
Check existing companies, warehouses, locations, users, modules, settings, etc.
"""
import xmlrpc.client

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def search_read(model, domain=[], fields=[], limit=100):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})
    except Exception as e:
        print(f"  ERROR on {model}: {e}")
        return []

print("=" * 70)
print("ODOO 19 DATABASE AUDIT — demo-tech.odoo.com")
print("=" * 70)

# 1. Companies
print("\n=== 1. COMPANIES ===")
companies = search_read('res.company', [], ['name', 'parent_id', 'currency_id', 'street', 'city', 'country_id', 'vat'])
for c in companies:
    print(f"  ID={c['id']}: {c['name']}")
    print(f"    Address: {c.get('street','')}, {c.get('city','')}")
    print(f"    Currency: {c['currency_id']}, VAT: {c.get('vat','')}")
    print(f"    Parent: {c['parent_id']}")

# 2. Warehouses
print("\n=== 2. WAREHOUSES ===")
warehouses = search_read('stock.warehouse', [], ['name', 'code', 'company_id', 'partner_id', 'resupply_wh_ids', 'reception_steps', 'delivery_steps', 'manufacture_to_resupply', 'buy_to_resupply', 'active'])
for w in warehouses:
    print(f"  ID={w['id']}: {w['name']} (Code: {w['code']})")
    print(f"    Company: {w['company_id']}, Address: {w['partner_id']}")
    print(f"    Resupply From: {w['resupply_wh_ids']}")
    print(f"    Steps: In={w['reception_steps']}, Out={w['delivery_steps']}")
    print(f"    Mfg: {w['manufacture_to_resupply']}, Buy: {w['buy_to_resupply']}")

# 3. Stock Locations 
print("\n=== 3. STOCK LOCATIONS ===")
locations = search_read('stock.location', [['usage', 'in', ['internal', 'transit', 'view']]], ['name', 'complete_name', 'usage', 'company_id', 'warehouse_id', 'active'], limit=50)
for loc in locations:
    print(f"  ID={loc['id']}: {loc['complete_name']} (Usage: {loc['usage']}, WH: {loc['warehouse_id']})")

# 4. Users
print("\n=== 4. USERS ===")
users = search_read('res.users', [['share', '=', False]], ['name', 'login', 'company_id', 'company_ids'])
for u in users:
    print(f"  ID={u['id']}: {u['name']} ({u['login']})")
    print(f"    Company: {u['company_id']}, Allowed: {u['company_ids']}")

# 5. Installed Modules (relevant ones)
print("\n=== 5. KEY MODULES ===")
module_names = ['base', 'account', 'sale', 'sale_management', 'purchase', 'stock', 'mrp', 
    'stock_account', 'purchase_stock', 'sale_stock', 'account_reports', 'analytic',
    'account_inter_company_rules', 'sale_purchase_inter_company_rules',
    'sale_purchase_stock_inter_company_rules', 'point_of_sale',
    'stock_landed_costs', 'sale_margin']
mods = search_read('ir.module.module', [['name', 'in', module_names]], ['name', 'state', 'installed_version'])
for m in mods:
    status = "✅" if m['state'] == 'installed' else "❌"
    print(f"  {status} {m['name']}: {m['state']} (v{m.get('installed_version','')})")

# 6. Products
print("\n=== 6. PRODUCTS ===")
products = search_read('product.template', [['type', '!=', 'service']], ['name', 'type', 'list_price', 'standard_price', 'tracking'], limit=20)
print(f"  Total storable/consumable products found: {len(products)}")
for p in products:
    print(f"  ID={p['id']}: {p['name']} (Type: {p['type']}, Sale: {p['list_price']}, Cost: {p['standard_price']})")

# 7. Routes
print("\n=== 7. STOCK ROUTES ===")
routes = search_read('stock.route', [], ['name', 'active', 'company_id', 'product_selectable', 'warehouse_selectable', 'sale_selectable'])
for r in routes:
    print(f"  ID={r['id']}: {r['name']} (Active: {r['active']}, Company: {r['company_id']})")

# 8. Operation Types
print("\n=== 8. OPERATION TYPES ===")
ops = search_read('stock.picking.type', [], ['name', 'warehouse_id', 'code', 'company_id', 'sequence_code', 'reservation_method'])
for op in ops:
    print(f"  ID={op['id']}: {op['name']} (WH: {op['warehouse_id']}, Code: {op['code']}, Reserve: {op['reservation_method']})")

# 9. Pricelists
print("\n=== 9. PRICELISTS ===")
pricelists = search_read('product.pricelist', [], ['name', 'currency_id', 'company_id', 'active'])
for pl in pricelists:
    print(f"  ID={pl['id']}: {pl['name']} (Currency: {pl['currency_id']}, Company: {pl['company_id']})")

# 10. Journals
print("\n=== 10. ACCOUNTING JOURNALS ===")
journals = search_read('account.journal', [], ['name', 'code', 'type', 'company_id'])
for j in journals:
    print(f"  ID={j['id']}: {j['name']} (Code: {j['code']}, Type: {j['type']}, Company: {j['company_id']})")

# 11. Analytic Plans
print("\n=== 11. ANALYTIC PLANS ===")
try:
    plans = search_read('account.analytic.plan', [], ['name', 'parent_id', 'default_applicability'])
    for p in plans:
        print(f"  ID={p['id']}: {p['name']} (Parent: {p['parent_id']}, Applicability: {p.get('default_applicability','')})")
except:
    print("  Could not read analytic plans")

# 12. Analytic Accounts
print("\n=== 12. ANALYTIC ACCOUNTS ===")
try:
    accounts = search_read('account.analytic.account', [], ['name', 'plan_id', 'active'])
    for a in accounts:
        print(f"  ID={a['id']}: {a['name']} (Plan: {a['plan_id']})")
except:
    print("  Could not read analytic accounts")

# 13. Taxes
print("\n=== 13. TAXES (Active) ===")
taxes = search_read('account.tax', [['active', '=', True]], ['name', 'type_tax_use', 'amount', 'company_id'])
for t in taxes:
    print(f"  ID={t['id']}: {t['name']} (Use: {t['type_tax_use']}, Rate: {t['amount']}%, Company: {t['company_id']})")

# 14. Fiscal Positions
print("\n=== 14. FISCAL POSITIONS ===")
fps = search_read('account.fiscal.position', [], ['name', 'company_id', 'auto_apply'])
for fp in fps:
    print(f"  ID={fp['id']}: {fp['name']} (Company: {fp['company_id']}, Auto: {fp['auto_apply']})")

# 15. Contacts/Partners (customers/vendors)
print("\n=== 15. KEY CONTACTS ===")
partners = search_read('res.partner', [['is_company', '=', True], ['id', '>', 3]], ['name', 'customer_rank', 'supplier_rank', 'company_id', 'city'], limit=20)
for p in partners:
    role = []
    if p['customer_rank'] > 0: role.append("Customer")
    if p['supplier_rank'] > 0: role.append("Vendor")
    print(f"  ID={p['id']}: {p['name']} ({', '.join(role) if role else 'Contact'}, City: {p.get('city','')})")

# 16. Check settings model for multi-company related fields
print("\n=== 16. MULTI-STEP ROUTES / STORAGE LOCATIONS ===")
try:
    groups = search_read('res.groups', [['name', 'in', ['Multi-Step Routes', 'Storage Locations', 'Multi Locations', 'Multi-Warehouses']]], ['name', 'full_name', 'users'])
    for g in groups:
        print(f"  {g['full_name']}: Users={g['users']}")
except:
    print("  Could not check groups")

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
