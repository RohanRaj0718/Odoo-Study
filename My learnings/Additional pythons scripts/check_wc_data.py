import xmlrpc.client
URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
UID = 2
PWD = 'Rohanraj@1'
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

wcs = models.execute_kw(DB, UID, PWD, 'mrp.workcenter', 'search_read', [[]], {'fields': ['name', 'code', 'id'], 'order': 'id'})
print('=== Work Centers ===')
for wc in wcs:
    print(f'  ID {wc["id"]}: {wc["name"]} ({wc["code"]})')

mos = models.execute_kw(DB, UID, PWD, 'mrp.production', 'search_read', [[]], {'fields': ['name', 'product_id', 'state', 'id']})
print('\n=== Manufacturing Orders ===')
for mo in mos:
    print(f'  ID {mo["id"]}: {mo["name"]} - {mo["product_id"][1]} (state={mo["state"]})')

wos = models.execute_kw(DB, UID, PWD, 'mrp.workorder', 'search_read', [[]], {'fields': ['name', 'workcenter_id', 'state', 'production_id'], 'order': 'id'})
print('\n=== Work Orders ===')
for wo in wos:
    print(f'  {wo["name"]} at {wo["workcenter_id"][1]} (state={wo["state"]})')

boms = models.execute_kw(DB, UID, PWD, 'mrp.bom', 'search_read', [[]], {'fields': ['product_tmpl_id', 'type', 'operation_ids', 'bom_line_ids']})
print('\n=== BoMs ===')
for b in boms:
    print(f'  {b["product_tmpl_id"][1]} - type={b["type"]}, ops={len(b["operation_ids"])}, lines={len(b["bom_line_ids"])}')

prods = models.execute_kw(DB, UID, PWD, 'product.template', 'search_read', [[['name', 'ilike', 'Executive']]], {'fields': ['name', 'id']})
print('\n=== Executive Standing Desk ===')
for p in prods:
    print(f'  ID {p["id"]}: {p["name"]}')
