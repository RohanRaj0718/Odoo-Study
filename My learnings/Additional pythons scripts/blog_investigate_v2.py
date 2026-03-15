#!/usr/bin/env python3
"""Investigate failures - Part 2."""
import xmlrpc.client

URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

print('=== ISSUE 3 DEEP DIVE: Route product_selectable ===')
# The routes have product_selectable=False which means they can't be added to products
resupply = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
    [[['name', 'ilike', 'subcontract']]],
    {'fields': ['name', 'id', 'product_selectable', 'product_categ_selectable', 'active']})
for r in resupply:
    print(f'  Route: {r["name"]}')
    print(f'    product_selectable: {r["product_selectable"]}')
    print(f'    product_categ_selectable: {r["product_categ_selectable"]}')

# Try making it product_selectable
print('\nMaking "Resupply Subcontractor on Order" product_selectable...')
for r in resupply:
    if 'on Order' in r['name']:
        models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'write',
            [[r['id']], {'product_selectable': True}])
        r2 = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
            [[['id', '=', r['id']]]],
            {'fields': ['product_selectable']})
        print(f'  After write: product_selectable = {r2[0]["product_selectable"]}')

print('\n=== ISSUE 4 DEEP DIVE: All pickings ===')
all_picks = models.execute_kw(DB, uid, PASSWORD, 'stock.picking', 'search_read',
    [[]], {'fields': ['name', 'picking_type_id', 'state', 'origin', 
                       'location_id', 'location_dest_id']})
print(f'Total pickings: {len(all_picks)}')
for p in all_picks:
    ptype = p['picking_type_id'][1] if p['picking_type_id'] else 'N/A'
    loc_from = p['location_id'][1] if p['location_id'] else 'N/A'
    loc_to = p['location_dest_id'][1] if p['location_dest_id'] else 'N/A'
    print(f'  {p["name"]} | {ptype} | state={p["state"]}')
    print(f'    From: {loc_from} -> To: {loc_to}')
    print(f'    Origin: {p["origin"]}')

# Check picking types
print('\n=== Picking types ===')
pick_types = models.execute_kw(DB, uid, PASSWORD, 'stock.picking.type', 'search_read',
    [[]], {'fields': ['name', 'code', 'sequence_code']})
for pt in pick_types:
    print(f'  {pt["name"]} | code={pt["code"]} | seq={pt["sequence_code"]}')

print('\n=== ISSUE 5 DEEP DIVE: Product type ===')
# What product types are available in Odoo 19?
prod_fields = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'fields_get',
    [['type']], {'attributes': ['selection', 'string', 'help']})
print(f'Product type field:')
print(f'  Label: {prod_fields["type"]["string"]}')
print(f'  Selections: {prod_fields["type"]["selection"]}')
print(f'  Help: {prod_fields["type"].get("help", "none")}')

# Check if 'storable' is a valid option
type_selections = dict(prod_fields['type']['selection'])
print(f'\n  Available types: {type_selections}')
print(f'  Has "product" (storable): {"product" in type_selections}')
print(f'  Has "consu": {"consu" in type_selections}')

# Check stock quants
quants = models.execute_kw(DB, uid, PASSWORD, 'stock.quant', 'search_read',
    [[]], {'fields': ['product_id', 'quantity', 'location_id'], 'limit': 20})
print(f'\nAll stock quants: {len(quants)}')
for q in quants:
    print(f'  {q["product_id"][1]} x {q["quantity"]} at {q["location_id"][1]}')

# Blog says "Set the contact as a Company" - in Odoo 19 UI, is there a 
# Company/Individual toggle?
print('\n=== Check Odoo 19 contact fields ===')
partner_fields = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'fields_get',
    [['is_company']], {'attributes': ['string', 'help', 'type']})
print(f'is_company field: {partner_fields.get("is_company")}')

# Blog says "the subcontracting workflow is triggered through a Purchase Order, 
# not a Manufacturing Order" - verify: was any MO created?  
print('\n=== Check Manufacturing Orders ===')
mos = models.execute_kw(DB, uid, PASSWORD, 'mrp.production', 'search_read',
    [[]], {'fields': ['name', 'product_id', 'state', 'origin']})
print(f'Manufacturing Orders: {len(mos)}')
for mo in mos:
    print(f'  {mo["name"]} | {mo["product_id"][1]} | state={mo["state"]} | origin={mo["origin"]}')
