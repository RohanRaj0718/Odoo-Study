"""
FIX V3 — Fix internal transfer move lines + verify stock quants
In Odoo 19, stock.move 'name' field was likely renamed.
"""
import xmlrpc.client
import sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def ex(model, method, *args, **kwargs):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
    except Exception as e:
        print(f"  ERR {model}.{method}: {e}")
        return None

def sr(model, domain=[], fields=[], limit=100):
    return ex(model, 'search_read', [domain], {'fields': fields, 'limit': limit}) or []

def cr(model, vals):
    return ex(model, 'create', [vals])

def wr(model, ids, vals):
    if not isinstance(ids, list): ids = [ids]
    return ex(model, 'write', [ids, vals])

COMPANY_ID = 1
print("=" * 70)
print("FIX V3 — Transfer Move Lines & Verification")
print("=" * 70)

# ═══════════════════════════════════════════
# STEP 1: Discover stock.move fields
# ═══════════════════════════════════════════
print("\n  Discovering stock.move fields...")
sm_fields = ex('stock.move', 'fields_get', [], {'attributes': ['string', 'type', 'required']})

# Check key fields
check_fields = ['name', 'description', 'reference', 'product_id', 'product_uom_qty', 
                'product_uom', 'picking_id', 'location_id', 'location_dest_id', 
                'company_id', 'description_picking']
print("  stock.move field check:")
for f in check_fields:
    if f in sm_fields:
        info = sm_fields[f]
        print(f"    ✅ {f}: type={info.get('type')}, string='{info.get('string')}', required={info.get('required', False)}")
    else:
        print(f"    ❌ {f}: NOT FOUND")

# Find any required fields
print("\n  Required stock.move fields:")
required_fields = {k: v for k, v in sm_fields.items() if v.get('required')}
for f, info in sorted(required_fields.items()):
    print(f"    {f}: {info.get('string')} (type={info.get('type')})")


# ═══════════════════════════════════════════
# STEP 2: Delete existing empty transfers and recreate
# ═══════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 2: RECREATE INTERNAL TRANSFERS WITH CORRECT FIELD NAMES")
print("─" * 70)

# Get warehouse locations
whs = sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['name', 'code', 'id'])
wh_ids = {w['code']: w['id'] for w in whs}

wh_locations = {}
for wh in whs:
    locs = sr('stock.location', [['usage', '=', 'internal'], ['warehouse_id', '=', wh['id']], ['name', '=', 'Stock']], ['id'])
    if locs:
        wh_locations[wh['code']] = locs[0]['id']

# Get product IDs
our_products = [
    "SmartDesk Pro X1", "ErgoChair Elite", "Standing Desk Converter",
    "LED Smart Monitor 27\"", "Wireless Keyboard Combo", "Bluetooth Speaker Pro",
    "USB-C Hub 7-in-1", "Laptop Stand Adjustable", "Cable Organizer Kit",
    "Smart LED Strip 5m", "WiFi Smart Plug Pack", "Smart Security Camera"
]
product_ids = {}
for pname in our_products:
    prods = sr('product.template', [['name', '=', pname]], ['id'])
    if prods:
        product_ids[pname] = prods[0]['id']

def get_pp_id(pname):
    pid = product_ids.get(pname)
    if pid:
        pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id', 'uom_id'])
        return pp[0] if pp else None
    return None

# Delete existing empty transfers
old_picks = sr('stock.picking',
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID], ['state', '=', 'draft']],
    ['id', 'name', 'move_ids'])

for p in old_picks:
    if not p.get('move_ids') or len(p['move_ids']) == 0:
        print(f"  Deleting empty transfer {p['name']} (ID={p['id']})...")
        ex('stock.picking', 'unlink', [[p['id']]])

# Get internal picking type from Kochi
int_types = sr('stock.picking.type',
    [['code', '=', 'internal'], ['warehouse_id', '=', wh_ids.get('KOCHI')]],
    ['id', 'name'])
kochi_internal = int_types[0]['id'] if int_types else None

if not kochi_internal:
    int_types = sr('stock.picking.type',
        [['code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
        ['id', 'name'])
    kochi_internal = int_types[0]['id'] if int_types else None

print(f"  Internal picking type: {kochi_internal}")

# Build transfer moves using correct fields (no 'name' field)
# Instead of name, use description_picking or just omit it
kochi_loc = wh_locations.get('KOCHI')
bang_loc = wh_locations.get('BANG')
chen_loc = wh_locations.get('CHEN')

transfers = [
    (kochi_loc, bang_loc, 'Resupply: Kochi → Bangalore',
     [("SmartDesk Pro X1", 5), ("ErgoChair Elite", 10), ("Wireless Keyboard Combo", 20)]),
    (kochi_loc, chen_loc, 'Resupply: Kochi → Chennai',
     [("Standing Desk Converter", 3), ("Smart LED Strip 5m", 15), ("Cable Organizer Kit", 25)]),
]

for src, dest, origin, lines in transfers:
    if not src or not dest or not kochi_internal:
        print(f"  ⚠️  Missing data for {origin}")
        continue
    
    # Create the picking with move_ids using one2many command
    move_vals_list = []
    for pname, qty in lines:
        pp = get_pp_id(pname)
        if pp:
            move_data = {
                'product_id': pp['id'],
                'product_uom_qty': qty,
                'location_id': src,
                'location_dest_id': dest,
                'company_id': COMPANY_ID,
            }
            if 'product_uom' in sm_fields:
                move_data['product_uom'] = pp.get('uom_id', [1])[0] if pp.get('uom_id') else 1
            if 'description_picking' in sm_fields:
                move_data['description_picking'] = f'Transfer: {pname}'
            
            move_vals_list.append((0, 0, move_data))
    
    if move_vals_list:
        pick_vals = {
            'picking_type_id': kochi_internal,
            'location_id': src,
            'location_dest_id': dest,
            'company_id': COMPANY_ID,
            'origin': origin,
            'move_ids': move_vals_list,
        }
        pick_id = cr('stock.picking', pick_vals)
        if pick_id:
            # Verify
            pick = sr('stock.picking', [['id', '=', pick_id]], ['name', 'move_ids'])
            if pick:
                print(f"  ✅ Created {pick[0]['name']} — {origin} (moves={len(pick[0].get('move_ids',[]))})")
            else:
                print(f"  ✅ Created transfer ID={pick_id} — {origin}")
        else:
            # Try creating picking without moves first, then add moves
            print(f"  ⚠️  Picking with moves failed, trying separate approach...")
            pick_id = cr('stock.picking', {
                'picking_type_id': kochi_internal,
                'location_id': src,
                'location_dest_id': dest,
                'company_id': COMPANY_ID,
                'origin': origin,
            })
            if pick_id:
                move_count = 0
                for pname, qty in lines:
                    pp = get_pp_id(pname)
                    if pp:
                        move_data = {
                            'product_id': pp['id'],
                            'product_uom_qty': qty,
                            'picking_id': pick_id,
                            'location_id': src,
                            'location_dest_id': dest,
                            'company_id': COMPANY_ID,
                        }
                        if 'product_uom' in sm_fields:
                            move_data['product_uom'] = pp.get('uom_id', [1])[0] if pp.get('uom_id') else 1
                        
                        mid = cr('stock.move', move_data)
                        if mid:
                            move_count += 1
                print(f"  ✅ Created transfer ID={pick_id} — {origin} (moves={move_count})")


# ═══════════════════════════════════════════
# STEP 3: Verify actual stock quantities
# ═══════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 3: VERIFY STOCK QUANTS")
print("─" * 70)

quants = sr('stock.quant',
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID], ['quantity', '>', 0]],
    ['product_id', 'location_id', 'quantity'], limit=200)

if quants:
    # Group by location
    from collections import defaultdict
    by_loc = defaultdict(list)
    for q in quants:
        by_loc[q['location_id'][1]].append((q['product_id'][1], q['quantity']))
    
    for loc, items in sorted(by_loc.items()):
        print(f"\n  {loc}:")
        for pname, qty in sorted(items):
            print(f"    {pname}: {qty}")
else:
    print("  ⚠️  No quants with quantity > 0 found")
    # Check if quants exist but with inventory_quantity only (not applied)
    all_quants = sr('stock.quant',
        [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
        ['product_id', 'location_id', 'quantity', 'inventory_quantity'], limit=200)
    print(f"  Total quants (including qty=0): {len(all_quants)}")
    if all_quants:
        for q in all_quants[:5]:
            print(f"    {q['product_id'][1]} @ {q['location_id'][1]}: qty={q['quantity']}, inv_qty={q['inventory_quantity']}")

# Also check the quants that need to be applied
unapplied = sr('stock.quant',
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID],
     ['inventory_quantity', '>', 0], ['quantity', '=', 0]],
    ['id', 'product_id', 'location_id', 'inventory_quantity'], limit=200)

if unapplied:
    print(f"\n  ⚠️  {len(unapplied)} quants need inventory adjustment applied!")
    print("  Applying inventory adjustments now...")
    for q in unapplied:
        result = ex('stock.quant', 'action_apply_inventory', [[q['id']]])
        # The error is just a serialization issue, the action may still work
    
    # Re-check
    import time
    time.sleep(2)
    quants_after = sr('stock.quant',
        [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID], ['quantity', '>', 0]],
        ['product_id', 'location_id', 'quantity'], limit=200)
    print(f"  After apply: {len(quants_after)} quants with qty > 0")


# ═══════════════════════════════════════════
# FINAL COUNTS
# ═══════════════════════════════════════════
print("\n" + "═" * 70)
print("FINAL VERIFICATION")
print("═" * 70)

wh_count = len(sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['id']))
loc_count = len(sr('stock.location', [['usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]], ['id']))
rule_count = len(sr('stock.warehouse.orderpoint', [['company_id', '=', COMPANY_ID]], ['id'], limit=200))

picks = sr('stock.picking',
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['name', 'move_ids', 'location_id', 'location_dest_id', 'state'])
for p in picks:
    print(f"  Transfer: {p['name']} {p['location_id'][1]}→{p['location_dest_id'][1]} (moves={len(p.get('move_ids',[]))}, state={p['state']})")

quant_count = len(sr('stock.quant',
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID], ['quantity', '>', 0]],
    ['id'], limit=200))
quant_total = len(sr('stock.quant',
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['id'], limit=200))

# Customers - try different query  
all_customers = sr('res.partner', 
    [['name', 'in', ['Kerala Tech Solutions', 'Cochin Startups Hub', 'Marine Drive Interiors',
                      'InnoTech Bangalore', 'Silicon Valley Cowork', 'Namma Office Supplies',
                      'Tamil Digital Solutions', 'Marina Bay Enterprises', 'SpaceTech Workspace']]],
    ['name', 'customer_rank'])
cust_with_rank = [c for c in all_customers if c.get('customer_rank', 0) > 0]

print(f"""
  🏭 Warehouses:           {wh_count}/3
  📍 Internal Locations:    {loc_count}
  🔄 Reordering Rules:     {rule_count}
  📋 Stock Quants:          {quant_count} with qty>0 / {quant_total} total
  📝 Internal Transfers:   {len(picks)}
  👤 Customers w/ rank:     {len(cust_with_rank)}/9
""")
