"""
FIX SCRIPT V2 — Fix remaining issues:
  1. Make products storable (is_storable = True) — Odoo 19 uses this instead of type='product'
  2. Set opening stock via quants after products are storable
  3. Fix internal transfer move lines (currently 0 moves)
  4. Verify customer ranks
"""
import xmlrpc.client
import time, sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 70)
print("FIX V2 — Storable Products, Opening Stock, Transfer Moves")
print("=" * 70)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("Auth failed!"); sys.exit(1)
print(f"Connected as UID={uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def ex(model, method, *args, **kwargs):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
    except Exception as e:
        print(f"  ERR {model}.{method}: {e}")
        return None

def sr(model, domain=[], fields=[], limit=100):
    return ex(model, 'search_read', [domain], {'fields': fields, 'limit': limit}) or []

def sc(model, domain, limit=100):
    return ex(model, 'search', [domain], {'limit': limit}) or []

def wr(model, ids, vals):
    if not isinstance(ids, list): ids = [ids]
    return ex(model, 'write', [ids, vals])

def cr(model, vals):
    return ex(model, 'create', [vals])

COMPANY_ID = 1

# ════════════════════════════════════════════════════
# STEP 1: Discover the correct field for storable
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 1: DISCOVER STORABLE PRODUCT FIELD")
print("─" * 70)

# Check product.template fields related to storable/tracking
pt_fields = ex('product.template', 'fields_get', [], {'attributes': ['string', 'type', 'selection']})
storable_candidates = ['is_storable', 'tracking', 'detailed_type', 'type']
for f in storable_candidates:
    if f in pt_fields:
        info = pt_fields[f]
        print(f"  {f}: type={info.get('type')}, string='{info.get('string')}'"
              f", selection={info.get('selection', 'N/A')}")
    else:
        print(f"  {f}: NOT FOUND")

# Also check product.product for the same
pp_fields = ex('product.product', 'fields_get', [], {'attributes': ['string', 'type', 'selection']})
for f in storable_candidates:
    if f in pp_fields:
        info = pp_fields[f]
        print(f"  [product.product] {f}: type={info.get('type')}, string='{info.get('string')}'")

# Read current product data to see what we're dealing with
our_products = [
    "SmartDesk Pro X1", "ErgoChair Elite", "Standing Desk Converter",
    "LED Smart Monitor 27\"", "Wireless Keyboard Combo", "Bluetooth Speaker Pro",
    "USB-C Hub 7-in-1", "Laptop Stand Adjustable", "Cable Organizer Kit",
    "Smart LED Strip 5m", "WiFi Smart Plug Pack", "Smart Security Camera"
]

read_fields = ['name', 'type', 'id']
if 'is_storable' in pt_fields:
    read_fields.append('is_storable')
if 'tracking' in pt_fields:
    read_fields.append('tracking')
if 'detailed_type' in pt_fields:
    read_fields.append('detailed_type')

print("\n  Current product states:")
product_ids = {}
for pname in our_products:
    prods = sr('product.template', [['name', '=', pname]], read_fields)
    if prods:
        p = prods[0]
        product_ids[pname] = p['id']
        extra = {k: p[k] for k in p if k not in ['id', 'name']}
        print(f"    {p['name']}: {extra}")


# ════════════════════════════════════════════════════
# STEP 2: Fix product to be storable
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 2: MAKE PRODUCTS STORABLE")
print("─" * 70)

# In Odoo 19, if 'is_storable' field exists, set it to True
# Otherwise try 'detailed_type' = 'product'
fix_vals = {}
if 'is_storable' in pt_fields:
    fix_vals = {'is_storable': True}
    print("  Strategy: Set is_storable = True")
elif 'detailed_type' in pt_fields:
    fix_vals = {'detailed_type': 'product'}
    print("  Strategy: Set detailed_type = 'product'")
else:
    # Try tracking
    fix_vals = {'tracking': 'lot'}
    print("  Strategy: Set tracking = 'lot' (fallback)")

if fix_vals:
    success = 0
    for pname, pid in product_ids.items():
        result = wr('product.template', pid, fix_vals)
        if result is not None and result is not False:
            success += 1
            print(f"    ✅ {pname}")
        elif result is False:
            # False from write can still mean success in Odoo
            # Check if it actually changed
            check = sr('product.template', [['id', '=', pid]], list(fix_vals.keys()))
            if check:
                actual = check[0]
                if all(actual.get(k) == v for k, v in fix_vals.items()):
                    success += 1
                    print(f"    ✅ {pname} (verified)")
                else:
                    print(f"    ❌ {pname} — value didn't change: {actual}")
            else:
                success += 1  # write returned False but might have worked
                print(f"    ⚠️  {pname} — write returned False, may need manual check")
        else:
            print(f"    ❌ {pname}")
    
    print(f"\n  Fixed {success}/{len(product_ids)} products")
    time.sleep(2)

# Verify the change
print("\n  Verifying product changes:")
for pname, pid in product_ids.items():
    p = sr('product.template', [['id', '=', pid]], read_fields)
    if p:
        extra = {k: p[0][k] for k in p[0] if k not in ['id', 'name']}
        print(f"    {pname}: {extra}")


# ════════════════════════════════════════════════════
# STEP 3: Set Opening Stock
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 3: SET OPENING STOCK")
print("─" * 70)

# Get warehouse stock locations
whs = sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['name', 'code', 'id'])
wh_ids = {w['code']: w['id'] for w in whs}

wh_locations = {}
for wh in whs:
    locs = sr('stock.location',
        [['usage', '=', 'internal'], ['warehouse_id', '=', wh['id']],
         ['name', '=', 'Stock']],
        ['complete_name', 'id'])
    if locs:
        wh_locations[wh['code']] = locs[0]['id']
        print(f"  {wh['code']} stock location: {locs[0]['complete_name']} (ID={locs[0]['id']})")

opening_stock = {
    'KOCHI': {
        "SmartDesk Pro X1": 50, "ErgoChair Elite": 40,
        "Standing Desk Converter": 30, "LED Smart Monitor 27\"": 60,
        "Wireless Keyboard Combo": 100, "Bluetooth Speaker Pro": 45,
        "USB-C Hub 7-in-1": 80, "Laptop Stand Adjustable": 35,
        "Cable Organizer Kit": 200, "Smart LED Strip 5m": 70,
        "WiFi Smart Plug Pack": 90, "Smart Security Camera": 25,
    },
    'BANG': {
        "SmartDesk Pro X1": 15, "ErgoChair Elite": 12,
        "Standing Desk Converter": 10, "LED Smart Monitor 27\"": 20,
        "Wireless Keyboard Combo": 40, "Bluetooth Speaker Pro": 15,
        "USB-C Hub 7-in-1": 30, "Laptop Stand Adjustable": 10,
        "Cable Organizer Kit": 60, "Smart LED Strip 5m": 25,
        "WiFi Smart Plug Pack": 30, "Smart Security Camera": 8,
    },
    'CHEN': {
        "SmartDesk Pro X1": 8, "ErgoChair Elite": 6,
        "Standing Desk Converter": 5, "LED Smart Monitor 27\"": 10,
        "Wireless Keyboard Combo": 20, "Bluetooth Speaker Pro": 8,
        "USB-C Hub 7-in-1": 15, "Laptop Stand Adjustable": 5,
        "Cable Organizer Kit": 30, "Smart LED Strip 5m": 12,
        "WiFi Smart Plug Pack": 15, "Smart Security Camera": 3,
    },
}

total_success = 0
total_fail = 0

for wh_code, stock_map in opening_stock.items():
    loc_id = wh_locations.get(wh_code)
    if not loc_id:
        print(f"\n  ⚠️  Skipping {wh_code} — stock location not found")
        continue
    
    print(f"\n  [{wh_code}] Setting opening stock at location ID={loc_id}...")
    wh_success = 0
    for pname, qty in stock_map.items():
        pid = product_ids.get(pname)
        if not pid:
            continue
        pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        if not pp:
            continue
        pp_id = pp[0]['id']
        
        # Check existing quant
        existing = sr('stock.quant',
            [['product_id', '=', pp_id], ['location_id', '=', loc_id]],
            ['id', 'quantity', 'inventory_quantity'])
        
        if existing:
            q = existing[0]
            if q['quantity'] >= qty:
                wh_success += 1
                continue
            # Update inventory_quantity and apply
            wr('stock.quant', q['id'], {'inventory_quantity': qty})
            result = ex('stock.quant', 'action_apply_inventory', [[q['id']]])
            if result is not None:
                wh_success += 1
        else:
            # Create new quant with inventory_quantity
            quant_id = cr('stock.quant', {
                'product_id': pp_id,
                'location_id': loc_id,
                'inventory_quantity': qty,
            })
            if quant_id:
                result = ex('stock.quant', 'action_apply_inventory', [[quant_id]])
                wh_success += 1
            else:
                total_fail += 1
    
    total_success += wh_success
    print(f"    {wh_code}: {wh_success}/{len(stock_map)} products stocked")

print(f"\n  Total: {total_success} quants created/updated, {total_fail} failures")


# ════════════════════════════════════════════════════
# STEP 4: Fix Internal Transfer Move Lines
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 4: FIX INTERNAL TRANSFER MOVE LINES")
print("─" * 70)

picks = sr('stock.picking',
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['name', 'location_id', 'location_dest_id', 'state', 'origin', 'move_ids'])

for p in picks:
    print(f"\n  Transfer {p['name']}: {p['location_id'][1]} → {p['location_dest_id'][1]}")
    print(f"    State: {p['state']}, Moves: {len(p.get('move_ids', []))}")
    
    if len(p.get('move_ids', [])) == 0:
        # Need to add moves
        src_loc = p['location_id'][0]
        dest_loc = p['location_dest_id'][0]
        
        # Determine which lines based on destination
        if 'BANG' in p['location_dest_id'][1]:
            lines = [("SmartDesk Pro X1", 5), ("ErgoChair Elite", 10), ("Wireless Keyboard Combo", 20)]
        elif 'CHEN' in p['location_dest_id'][1]:
            lines = [("Standing Desk Converter", 3), ("Smart LED Strip 5m", 15), ("Cable Organizer Kit", 25)]
        else:
            print(f"    ⚠️  Unknown destination, skipping")
            continue
        
        move_count = 0
        for pname, qty in lines:
            pid = product_ids.get(pname)
            if not pid:
                continue
            pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id', 'uom_id'])
            if not pp:
                continue
            pp_id = pp[0]['id']
            uom_id = pp[0]['uom_id'][0] if pp[0].get('uom_id') else 1
            
            move_id = cr('stock.move', {
                'name': f'Transfer: {pname}',
                'product_id': pp_id,
                'product_uom_qty': qty,
                'product_uom': uom_id,
                'picking_id': p['id'],
                'location_id': src_loc,
                'location_dest_id': dest_loc,
                'company_id': COMPANY_ID,
            })
            if move_id:
                move_count += 1
        
        print(f"    ✅ Added {move_count} move lines")
    else:
        print(f"    ✓ Already has {len(p['move_ids'])} moves")


# ════════════════════════════════════════════════════
# STEP 5: Verify/Fix Customer Ranks
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 5: VERIFY CUSTOMER CONTACTS")
print("─" * 70)

customer_names = [
    'Kerala Tech Solutions', 'Cochin Startups Hub', 'Marine Drive Interiors',
    'InnoTech Bangalore', 'Silicon Valley Cowork', 'Namma Office Supplies',
    'Tamil Digital Solutions', 'Marina Bay Enterprises', 'SpaceTech Workspace'
]

for cname in customer_names:
    contacts = sr('res.partner', [['name', '=', cname]], ['name', 'customer_rank', 'city'])
    if contacts:
        c = contacts[0]
        if c['customer_rank'] == 0:
            wr('res.partner', c['id'], {'customer_rank': 1})
            print(f"  ✅ Fixed rank: {cname} (city={c.get('city', '?')})")
        else:
            print(f"  ✓  OK: {cname} (rank={c['customer_rank']}, city={c.get('city', '?')})")
    else:
        print(f"  ❌ Not found: {cname}")

# Also verify vendors
print("\n  Verifying vendors:")
vendor_names = ['TechVision Distributors', 'FurniCraft India Pvt Ltd', 'SmartParts Components']
for vname in vendor_names:
    contacts = sr('res.partner', [['name', '=', vname]], ['name', 'supplier_rank'])
    if contacts:
        v = contacts[0]
        print(f"  ✓  {vname} (rank={v['supplier_rank']})")
    else:
        print(f"  ❌ Not found: {vname}")


# ════════════════════════════════════════════════════
# STEP 6: Verify Products Have Correct Routes
# ════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 6: VERIFY PRODUCT ROUTES")
print("─" * 70)

# Routes that should be on products: Both resupply routes
resupply_routes = sr('stock.route', 
    [['name', 'like', 'Supply Product from'], ['product_selectable', '=', True]], 
    ['name', 'id'])
route_ids_expected = [r['id'] for r in resupply_routes]
print(f"  Expected resupply routes on products: {[r['name'] for r in resupply_routes]}")

for pname, pid in product_ids.items():
    p = sr('product.template', [['id', '=', pid]], ['route_ids'])
    if p:
        current_routes = p[0]['route_ids']
        missing = [r for r in route_ids_expected if r not in current_routes]
        if missing:
            new_routes = list(set(current_routes + route_ids_expected))
            wr('product.template', pid, {'route_ids': [(6, 0, new_routes)]})
            print(f"  ✅ Fixed routes for {pname}")
        else:
            print(f"  ✓  {pname}: routes OK ({len(current_routes)} routes)")


# ════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("FINAL SUMMARY")
print("═" * 70)

# Re-check everything
wh_count = len(sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['id']))
loc_count = len(sr('stock.location', [['usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]], ['id']))

# Check product storable status
storable_field = 'is_storable' if 'is_storable' in pt_fields else 'type'
prods = sr('product.template', [['id', 'in', list(product_ids.values())]], ['name', storable_field])
storable_count = sum(1 for p in prods if p.get(storable_field) in [True, 'product'])

rule_count = len(sr('stock.warehouse.orderpoint', [['company_id', '=', COMPANY_ID]], ['id'], limit=200))
so_count = len(sr('sale.order', [['company_id', '=', COMPANY_ID]], ['id']))
po_count = len(sr('purchase.order', [['company_id', '=', COMPANY_ID]], ['id']))

# Re-count transfers with moves
picks = sr('stock.picking',
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['name', 'move_ids'])
picks_with_moves = sum(1 for p in picks if len(p.get('move_ids', [])) > 0)

quant_count = len(sr('stock.quant', 
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['id'], limit=200))

cust_count = len(sr('res.partner', [['customer_rank', '>', 0], ['is_company', '=', True]], ['id']))
vend_count = len(sr('res.partner', [['supplier_rank', '>', 0]], ['id']))

aa_count = len(sr('account.analytic.account', [['plan_id.name', '=', 'Outlets']], ['id']))
pl_count = len(sr('product.pricelist', [], ['id']))

print(f"""
  🏭 Warehouses:            {wh_count}/3
  📍 Stock Locations:        {loc_count} (internal, incl. sub-locations)
  📦 Products (storable):    {storable_count}/12
  🔄 Reordering Rules:       {rule_count}
  📊 Pricelists:             {pl_count}
  📈 Analytic Accounts:      {aa_count}/3 (Outlets plan)
  📋 Stock Quants:           {quant_count}

  👥 Vendors:                {vend_count}
  👤 Customers:              {cust_count}

  📝 Sale Orders:            {so_count}
  📝 Purchase Orders:        {po_count}
  📝 Transfers (w/ moves):   {picks_with_moves}/{len(picks)}
""")

# List any remaining issues
issues = []
if wh_count < 3: issues.append("Missing warehouses")
if storable_count < 12: issues.append(f"Only {storable_count}/12 products are storable")
if quant_count < 30: issues.append(f"Only {quant_count} stock quants (expected ~36 for opening stock)")
if picks_with_moves < 2: issues.append(f"Only {picks_with_moves}/2 transfers have move lines")
if cust_count < 9: issues.append(f"Only {cust_count}/9 customers")

if issues:
    print("  ⚠️  REMAINING ISSUES:")
    for i in issues:
        print(f"    • {i}")
else:
    print("  ✅ ALL CHECKS PASSED!")
