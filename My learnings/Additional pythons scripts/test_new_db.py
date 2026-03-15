"""Quick test of the new practice database connection"""
import xmlrpc.client

URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
version = common.version()
sv = version.get('server_version', 'unknown')
print(f'Server Version: {sv}')

uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f'UID: {uid}')

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Check existing companies
companies = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search_read', [[]], {'fields': ['name', 'parent_id', 'country_id', 'state_id']})
print(f'\nExisting companies: {len(companies)}')
for c in companies:
    print(f'  ID={c["id"]}: {c["name"]} (parent: {c["parent_id"]}, country: {c["country_id"]}, state: {c["state_id"]})')

# Check installed modules
key_modules = ['sale_management', 'purchase', 'stock', 'account', 'crm', 'l10n_in', 'account_accountant', 'repair', 'stock_barcode', 'planning', 'knowledge']
modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read', 
    [[['name', 'in', key_modules]]], 
    {'fields': ['name', 'shortdesc', 'state']})
print(f'\nKey modules status:')
for m in sorted(modules, key=lambda x: x['name']):
    print(f'  {m["name"]}: {m["state"]}')

# Check warehouses
wh = models.execute_kw(DB, uid, PASSWORD, 'stock.warehouse', 'search_read', [[]], {'fields': ['name', 'code', 'company_id']})
print(f'\nWarehouses: {len(wh)}')
for w in wh:
    print(f'  {w["name"]} ({w["code"]}) - Company: {w["company_id"]}')

# Check product categories
cats = models.execute_kw(DB, uid, PASSWORD, 'product.category', 'search_read', [[]], {'fields': ['name', 'complete_name']})
print(f'\nProduct categories: {len(cats)}')
for cat in cats:
    print(f'  {cat["complete_name"]}')

# Check existing partners
partners = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search_read', 
    [[['is_company', '=', True], ['id', '>', 1]]], 
    {'fields': ['name', 'customer_rank', 'supplier_rank']})
print(f'\nExisting company partners: {len(partners)}')
for p in partners:
    print(f'  {p["name"]} (customer: {p["customer_rank"]}, vendor: {p["supplier_rank"]})')

# Check country/state availability
india = models.execute_kw(DB, uid, PASSWORD, 'res.country', 'search_read', [[['code', '=', 'IN']]], {'fields': ['id', 'name']})
print(f'\nIndia country: {india}')

kerala = models.execute_kw(DB, uid, PASSWORD, 'res.country.state', 'search_read', [[['name', 'like', 'Kerala']]], {'fields': ['id', 'name', 'country_id']})
print(f'Kerala state: {kerala}')
