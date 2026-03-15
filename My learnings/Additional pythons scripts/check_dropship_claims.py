import xmlrpc.client
URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
UID = 2
PWD = 'Rohanraj@1'
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

# 1. Check if 'Subcontracted checkbox' exists on vendor pricelist or PO line
print('=== Checking for Subcontracted checkbox ===')
pol_fields = models.execute_kw(DB, UID, PWD, 'purchase.order.line', 'fields_get', [], {'attributes': ['string']})
subcontract_fields = {}
for k, v in pol_fields.items():
    if 'subcontract' in k.lower() or 'subcontract' in v['string'].lower():
        subcontract_fields[k] = v['string']
print('PO Line subcontract fields:', subcontract_fields)

si_fields = models.execute_kw(DB, UID, PWD, 'product.supplierinfo', 'fields_get', [], {'attributes': ['string']})
si_sub = {}
for k, v in si_fields.items():
    if 'subcontract' in k.lower() or 'subcontract' in v['string'].lower():
        si_sub[k] = v['string']
print('Vendor Pricelist subcontract fields:', si_sub)

# 2. All routes
print('\n=== All Stock Routes ===')
routes = models.execute_kw(DB, UID, PWD, 'stock.route', 'search_read', 
    [[]], {'fields': ['name', 'active']})
for r in routes:
    name = r['name']
    active = r['active']
    print(f'  {name} (active={active})')

# 3. Module status
print('\n=== Dropshipping modules ===')
ds_mods = models.execute_kw(DB, UID, PWD, 'ir.module.module', 'search_read',
    [[['name', 'in', ['stock_dropshipping', 'mrp_subcontracting_dropshipping']]]],
    {'fields': ['name', 'state']})
for m in ds_mods:
    print(f'  {m["name"]}: {m["state"]}')

# 4. Route rules
print('\n=== Stock rules with "subcontract" ===')
rules = models.execute_kw(DB, UID, PWD, 'stock.rule', 'search_read',
    [[['name', 'ilike', 'subcontract']]],
    {'fields': ['name', 'route_id', 'action', 'picking_type_id']})
for r in rules:
    route_name = r['route_id'][1] if r['route_id'] else ''
    pt_name = r['picking_type_id'][1] if r['picking_type_id'] else ''
    print(f'  Rule: {r["name"]}')
    print(f'    Route: {route_name} | Action: {r["action"]} | Picking Type: {pt_name}')

print('\n=== Stock rules with "dropship" ===')
rules2 = models.execute_kw(DB, UID, PWD, 'stock.rule', 'search_read',
    [[['name', 'ilike', 'dropship']]],
    {'fields': ['name', 'route_id', 'action']})
for r in rules2:
    route_name = r['route_id'][1] if r['route_id'] else ''
    print(f'  Rule: {r["name"]} | Route: {route_name} | Action: {r["action"]}')
if not rules2:
    print('  (none found)')
