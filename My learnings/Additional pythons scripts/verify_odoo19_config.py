"""Verify Odoo 19 configurations for the setup guide."""
import xmlrpc.client, socket, ssl
socket.setdefaulttimeout(60)

url = 'https://last-demo.odoo.com'
db = 'last-demo'
uid = 2
pwd = 'Rohanraj@1'
ctx = ssl._create_unverified_context()
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=ctx)

# 1. Check active routes
routes = models.execute_kw(db, uid, pwd, 'stock.route', 'search_read', [[]], {'fields': ['name','active'], 'limit': 30})
print('=== ACTIVE ROUTES ===')
for r in routes:
    print(f"  {r['name']}")

# 2. Archived routes (like MTO)
archived_routes = models.execute_kw(db, uid, pwd, 'stock.route', 'search_read', [[['active','=',False]]], {'fields': ['name'], 'limit': 20})
print('\n=== ARCHIVED ROUTES ===')
for r in archived_routes:
    print(f"  {r['name']}")

# 3. Payment terms
terms = models.execute_kw(db, uid, pwd, 'account.payment.term', 'search_read', [[]], {'fields': ['name'], 'limit': 20})
print('\n=== PAYMENT TERMS ===')
for t in terms:
    print(f"  {t['name']}")

# 4. Check key modules
mods = ['sale_purchase', 'purchase_requisition', 'account_online_synchronization',
        'stock_dropshipping', 'mrp_subcontracting', 'sale_loyalty', 'crm',
        'website', 'stock_landed_costs', 'product_expiry', 'mrp_plm']
print('\n=== MODULE STATUS ===')
for m in mods:
    r = models.execute_kw(db, uid, pwd, 'ir.module.module', 'search_read', [[['name','=',m]]], {'fields': ['name','state']})
    state = r[0]['state'] if r else 'NOT FOUND'
    print(f"  {m}: {state}")

# 5. BOM type field options
bom_fields = models.execute_kw(db, uid, pwd, 'mrp.bom', 'fields_get', [['type']], {'attributes': ['selection']})
print('\n=== BOM TYPE OPTIONS ===')
print(bom_fields.get('type', {}).get('selection', 'N/A'))

# 6. Check product fields for lead times
prod_fields = models.execute_kw(db, uid, pwd, 'product.template', 'fields_get', [
    ['sale_delay', 'produce_delay', 'days_to_prepare_mo']
], {'attributes': ['string', 'type']})
print('\n=== PRODUCT LEAD TIME FIELDS ===')
for k, v in prod_fields.items():
    print(f"  {k}: {v.get('string','')} ({v.get('type','')})")

# 7. Check BOM fields for lead times
bom_lt_fields = models.execute_kw(db, uid, pwd, 'mrp.bom', 'fields_get', [
    ['produce_delay', 'days_to_prepare_mo']
], {'attributes': ['string', 'type']})
print('\n=== BOM LEAD TIME FIELDS ===')
for k, v in bom_lt_fields.items():
    print(f"  {k}: {v.get('string','')} ({v.get('type','')})")

# 8. Check supplier info fields (vendor lead time)
supp_fields = models.execute_kw(db, uid, pwd, 'product.supplierinfo', 'fields_get', [
    ['delay', 'price']
], {'attributes': ['string', 'type']})
print('\n=== SUPPLIER INFO FIELDS ===')
for k, v in supp_fields.items():
    print(f"  {k}: {v.get('string','')} ({v.get('type','')})")

# 9. Credit note - check account.move fields
move_fields = models.execute_kw(db, uid, pwd, 'account.move', 'fields_get', [
    ['move_type']
], {'attributes': ['string', 'selection']})
print('\n=== MOVE TYPE OPTIONS ===')
print(move_fields.get('move_type', {}).get('selection', 'N/A'))

# 10. Check purchase.requisition fields for blanket orders
try:
    pr_fields = models.execute_kw(db, uid, pwd, 'purchase.requisition', 'fields_get', [
        ['type_id', 'ordering_date', 'date_end', 'vendor_id']
    ], {'attributes': ['string', 'type']})
    print('\n=== PURCHASE REQUISITION FIELDS ===')
    for k, v in pr_fields.items():
        print(f"  {k}: {v.get('string','')} ({v.get('type','')})")
except Exception as e:
    print(f'\nPurchase requisition error: {e}')

# 11. Check settings fields
settings_fields = models.execute_kw(db, uid, pwd, 'res.config.settings', 'fields_get', [
    ['use_security_lead', 'security_lead', 'use_po_lead', 'po_lead',
     'group_stock_multi_locations', 'group_stock_adv_location',
     'module_stock_dropshipping', 'module_mrp_subcontracting',
     'module_stock_landed_costs', 'group_lot_on_delivery_slip']
], {'attributes': ['string', 'type']})
print('\n=== SETTINGS FIELDS ===')
for k, v in settings_fields.items():
    print(f"  {k}: {v.get('string','')} ({v.get('type','')})")

print('\n=== DONE ===')
