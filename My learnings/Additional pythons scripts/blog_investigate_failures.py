#!/usr/bin/env python3
"""Investigate the 5 failures from subcontracting verification."""
import xmlrpc.client

URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

print('=== ISSUE 1: Dropship Subcontractor route ===')
# Check if mrp_subcontracting_dropshipping module exists
dropship_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'ilike', 'subcontracting_dropship']]],
    {'fields': ['name', 'state', 'shortdesc']})
print(f'Dropship subcontracting module: {dropship_mod}')

# Check ALL routes
all_routes = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
    [[]], {'fields': ['name'], 'order': 'name'})
print('All routes:')
for r in all_routes:
    print(f'  {r["name"]}')

print('\n=== ISSUE 2: is_company field ===')
# Read the partner we created
partner = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search_read',
    [[['name', '=', 'ProAssemble Subcontractors']]],
    {'fields': ['name', 'is_company']})
print(f'ProAssemble data: {partner}')

# Check what fields exist
all_partner_fields = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 
    'fields_get', [], {'attributes': ['string']})
has_is_company = 'is_company' in all_partner_fields
has_company_type = 'company_type' in all_partner_fields
print(f'has is_company field: {has_is_company}')
print(f'has company_type field: {has_company_type}')

if partner and not partner[0]['is_company']:
    print('is_company is False! Trying to fix...')
    models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'write',
        [[partner[0]['id']], {'is_company': True}])
    partner2 = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'read',
        [partner[0]['id']], {'fields': ['is_company']})
    print(f'After explicit write: is_company = {partner2[0]["is_company"]}')

print('\n=== ISSUE 3: Route assignment to components ===')
# Check the resupply route details
resupply = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
    [[['name', 'ilike', 'resupply subcontract']]],
    {'fields': ['name', 'id', 'product_selectable', 'product_categ_selectable']})
print(f'Resupply route: {resupply}')

# Check "Resupply Subcontractor on Order"
resupply2 = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
    [[['name', 'ilike', 'resupply']]],
    {'fields': ['name', 'id', 'product_selectable']})
print(f'All resupply routes: {resupply2}')

# Check component route_ids
comp = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'search_read',
    [[['name', '=', 'Steel Tube Frame']]],
    {'fields': ['name', 'route_ids']})
print(f'Steel Tube Frame routes: {comp}')

# Try re-assigning with the correct route
if resupply:
    route_id = resupply[0]['id']
    if comp:
        models.execute_kw(DB, uid, PASSWORD, 'product.template', 'write',
            [[comp[0]['id']], {'route_ids': [(4, route_id)]}])
        comp2 = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'read',
            [comp[0]['id']], {'fields': ['route_ids']})
        print(f'After reassign: route_ids = {comp2[0]["route_ids"]}')

print('\n=== ISSUE 4: Missing delivery order ===')
# Check all pickings
all_picks = models.execute_kw(DB, uid, PASSWORD, 'stock.picking', 'search_read',
    [[]], {'fields': ['name', 'picking_type_id', 'state', 'origin', 
                       'location_id', 'location_dest_id', 'move_ids']})
print(f'Total pickings in system: {len(all_picks)}')
for p in all_picks:
    print(f'  {p["name"]} | {p["picking_type_id"][1]} | state={p["state"]} | origin={p["origin"]}')
    # Get moves
    if p['move_ids']:
        moves = models.execute_kw(DB, uid, PASSWORD, 'stock.move', 'read',
            p['move_ids'][:5], {'fields': ['product_id', 'product_uom_qty']})
        for m in moves:
            print(f'    -> {m["product_id"][1]} x {m["product_uom_qty"]}')

# Check picking types
pick_types = models.execute_kw(DB, uid, PASSWORD, 'stock.picking.type', 'search_read',
    [[]], {'fields': ['name', 'code', 'sequence_code']})
print('\nPicking types:')
for pt in pick_types:
    print(f'  {pt["name"]} (code={pt["code"]}, seq={pt["sequence_code"]})')

# Check subcontracting orders
subcon_orders = models.execute_kw(DB, uid, PASSWORD, 'stock.picking', 'search_read',
    [[['picking_type_id.code', '=', 'mrp_operation']]],
    {'fields': ['name', 'state']})
print(f'\nSubcontracting operations: {subcon_orders}')

print('\n=== ISSUE 5: Product type and stock tracking ===')
prod = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'search_read',
    [[['name', '=', 'ErgoChair Pro (Subcontracted)']]],
    {'fields': ['name', 'type', 'tracking']})
print(f'Product: {prod}')
print('NOTE: In Odoo 19, type=consu means goods (consumable). There is no "product" (storable) type.')
print('Consumable products do NOT create stock.quant entries by default.')

# Check if there's a way to make it tracked
prod_fields = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'fields_get',
    [['type']], {'attributes': ['selection', 'string']})
print(f'\nproduct.template.type field: {prod_fields["type"]}')
