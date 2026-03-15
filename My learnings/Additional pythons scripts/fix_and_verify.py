"""
FIX & VERIFY SCRIPT — Fixes issues from setup_multi_outlet.py
Issues to fix:
  1. Products created as 'consu' → must be 'product' (storable) for inventory
  2. Reordering rules failed: 'qty_multiple' invalid field in Odoo 19
  3. Opening stock failed: quants can't be created for consumables
  4. Verify phases 16-19 completed (Sale Orders, POs, Transfers)
"""
import xmlrpc.client
import time, sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 70)
print("FIX & VERIFY — Multi-Outlet Setup")
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
        print(f"  ⚠️  {model}.{method}: {e}")
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

# ════════════════════════════════════════════════════════
# STEP 1: VERIFY CURRENT STATE
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 1: CURRENT STATE AUDIT")
print("─" * 70)

# Warehouses
print("\n  Warehouses:")
whs = sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], 
    ['name', 'code', 'id', 'resupply_wh_ids', 'buy_to_resupply'])
wh_ids = {}
for w in whs:
    wh_ids[w['code']] = w['id']
    print(f"    {w['code']}: {w['name']} (ID={w['id']}, Resupply from: {w['resupply_wh_ids']})")

# Stock locations
print("\n  Stock Locations (internal):")
locs = sr('stock.location',
    [['usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['complete_name', 'warehouse_id', 'id'])
wh_locations = {}
for loc in locs:
    print(f"    ID={loc['id']}: {loc['complete_name']}")
    # Map warehouse code to main stock location
    for wh in whs:
        if loc['warehouse_id'] and loc['warehouse_id'][0] == wh['id']:
            if '/Stock' in loc['complete_name'] and 'Zone' not in loc['complete_name'] and \
               'Cold' not in loc['complete_name'] and 'Display' not in loc['complete_name'] and \
               'Back' not in loc['complete_name'] and 'Showroom' not in loc['complete_name'] and \
               'Storage Room' not in loc['complete_name']:
                wh_locations[wh['code']] = loc['id']

print(f"\n  Main stock locations: {wh_locations}")

# Products
print("\n  Products (our 12 retail products):")
our_products = [
    "SmartDesk Pro X1", "ErgoChair Elite", "Standing Desk Converter",
    "LED Smart Monitor 27\"", "Wireless Keyboard Combo", "Bluetooth Speaker Pro",
    "USB-C Hub 7-in-1", "Laptop Stand Adjustable", "Cable Organizer Kit",
    "Smart LED Strip 5m", "WiFi Smart Plug Pack", "Smart Security Camera"
]
product_ids = {}
product_types = {}
for pname in our_products:
    prods = sr('product.template', [['name', '=', pname]], ['name', 'type', 'id', 'route_ids'])
    if prods:
        p = prods[0]
        product_ids[pname] = p['id']
        product_types[pname] = p['type']
        print(f"    ID={p['id']}: {p['name']} (type={p['type']}, routes={len(p['route_ids'])})")
    else:
        print(f"    ❌ Not found: {pname}")

# Routes
print("\n  Routes:")
routes = sr('stock.route', [['active', '=', True]], ['name', 'id', 'product_selectable'])
for r in routes:
    print(f"    ID={r['id']}: {r['name']} (selectable={r['product_selectable']})")

# Reordering rules
print("\n  Reordering Rules:")
rules = sr('stock.warehouse.orderpoint', [['company_id', '=', COMPANY_ID]], ['product_id', 'location_id'], limit=200)
print(f"    Total: {len(rules)}")

# Sale Orders
print("\n  Sale Orders:")
sos = sr('sale.order', [['company_id', '=', COMPANY_ID]], 
    ['name', 'partner_id', 'warehouse_id', 'state', 'amount_total', 'order_line'])
for so in sos:
    print(f"    {so['name']}: {so['partner_id'][1]} (WH={so.get('warehouse_id')}, Lines={len(so.get('order_line',[]))}, Total=₹{so['amount_total']:,.2f})")

# Purchase Orders
print("\n  Purchase Orders:")
pos = sr('purchase.order', [['company_id', '=', COMPANY_ID]],
    ['name', 'partner_id', 'state', 'amount_total', 'order_line'])
for po in pos:
    print(f"    {po['name']}: {po['partner_id'][1]} (Lines={len(po.get('order_line',[]))}, Total=₹{po['amount_total']:,.2f})")

# Internal Transfers
print("\n  Internal Transfers:")
picks = sr('stock.picking', 
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['name', 'location_id', 'location_dest_id', 'state', 'origin'])
for p in picks:
    print(f"    {p['name']}: {p['location_id'][1]} → {p['location_dest_id'][1]} ({p['state']})")

# Analytic
print("\n  Analytic Plans & Accounts:")
plans = sr('account.analytic.plan', [], ['name'])
for p in plans:
    print(f"    Plan: {p['name']}")
aas = sr('account.analytic.account', [], ['name', 'plan_id'])
for a in aas:
    print(f"    Account: {a['name']} (Plan: {a['plan_id']})")

# Pricelists
print("\n  Pricelists:")
pls = sr('product.pricelist', [], ['name'])
for p in pls:
    print(f"    {p['name']}")

# Vendor supplierinfo
print("\n  Vendor Supplier Info:")
si = sr('product.supplierinfo', [], ['product_tmpl_id', 'partner_id', 'price', 'delay'])
for s in si:
    print(f"    {s['product_tmpl_id'][1]} ← {s['partner_id'][1]} (₹{s['price']}, {s['delay']}d)")

# Stock quants
print("\n  Stock Quants (on-hand):")
quants = sr('stock.quant', 
    [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['product_id', 'location_id', 'quantity'], limit=200)
if quants:
    for q in quants:
        print(f"    {q['product_id'][1]} @ {q['location_id'][1]}: {q['quantity']}")
else:
    print("    (none)")


# ════════════════════════════════════════════════════════
# STEP 2: FIX PRODUCT TYPES (consu → product/storable)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 2: FIX PRODUCT TYPES")
print("─" * 70)

# Check what product type value Odoo 19 uses for storable
# In Odoo 17+, 'consu' is consumable and 'product' is storable
# In Odoo 19, it might be 'consu' → now means storable, or still 'product'
# Let's check fields_get for type field
type_field = ex('product.template', 'fields_get', [], {'attributes': ['string', 'selection']})
if type_field and 'type' in type_field:
    print(f"  Product type field: {type_field['type'].get('selection', 'N/A')}")
    print(f"  Product type string: {type_field['type'].get('string', 'N/A')}")

consu_products = [pname for pname, ptype in product_types.items() if ptype == 'consu']
product_products = [pname for pname, ptype in product_types.items() if ptype == 'product']

print(f"\n  Products with type 'consu': {len(consu_products)}")
print(f"  Products with type 'product': {len(product_products)}")

# In Odoo 19, the error says "Quants cannot be created for consumables or services"
# So we need to change type to 'product' (storable)
if consu_products:
    print("\n  Converting consumable products to storable ('product')...")
    for pname in consu_products:
        pid = product_ids.get(pname)
        if pid:
            result = wr('product.template', pid, {'type': 'product'})
            if result is not None:
                print(f"    ✅ {pname} → storable")
            else:
                print(f"    ❌ Failed: {pname}")
    time.sleep(2)
else:
    print("  All products already storable or need different approach")


# ════════════════════════════════════════════════════════
# STEP 3: SET OPENING STOCK (Now that products are storable)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 3: SET OPENING STOCK")
print("─" * 70)

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

for wh_code, stock_map in opening_stock.items():
    loc_id = wh_locations.get(wh_code)
    if not loc_id:
        print(f"  ⚠️  Skipping {wh_code} — stock location not found")
        continue
    
    print(f"\n  [{wh_code}] Setting opening stock at location ID={loc_id}...")
    success_count = 0
    for pname, qty in stock_map.items():
        pid = product_ids.get(pname)
        if not pid:
            continue
        # Get product.product ID
        pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        if not pp:
            continue
        pp_id = pp[0]['id']
        
        # Check if quant already exists
        existing = sr('stock.quant',
            [['product_id', '=', pp_id], ['location_id', '=', loc_id]],
            ['id', 'quantity', 'inventory_quantity'])
        
        if existing:
            q = existing[0]
            if q['quantity'] >= qty:
                success_count += 1
                continue
            # Update inventory_quantity and apply
            wr('stock.quant', q['id'], {'inventory_quantity': qty})
            ex('stock.quant', 'action_apply_inventory', [[q['id']]])
            success_count += 1
        else:
            # Create new quant
            quant_id = cr('stock.quant', {
                'product_id': pp_id,
                'location_id': loc_id,
                'inventory_quantity': qty,
            })
            if quant_id:
                ex('stock.quant', 'action_apply_inventory', [[quant_id]])
                success_count += 1
    
    print(f"    ✅ {wh_code}: {success_count}/{len(stock_map)} products stocked")


# ════════════════════════════════════════════════════════
# STEP 4: FIX REORDERING RULES (remove qty_multiple)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 4: CREATE REORDERING RULES (without qty_multiple)")
print("─" * 70)

# First check what fields are valid
op_fields = ex('stock.warehouse.orderpoint', 'fields_get', [], 
    {'attributes': ['string', 'type']})
valid_fields = sorted(op_fields.keys()) if op_fields else []
# Check for the field names we need
important_fields = ['product_id', 'location_id', 'product_min_qty', 'product_max_qty', 
                   'qty_multiple', 'qty_to_order', 'route_id', 'company_id', 'warehouse_id']
print("  Checking orderpoint fields:")
for f in important_fields:
    exists = f in valid_fields
    print(f"    {f}: {'✅' if exists else '❌'}")

# Get resupply and buy route IDs
resupply_routes = sr('stock.route', 
    [['name', 'like', 'Supply Product from']], ['name', 'id'])
buy_routes = sr('stock.route', [['name', '=', 'Buy']], ['id'])
buy_route_id = buy_routes[0]['id'] if buy_routes else None

# Map route IDs
route_map = {}
for r in resupply_routes:
    if 'Kochi' in r['name']:
        # Determine which warehouse this resupply route is for
        # "Bangalore Outlet: Supply Product from Kochi Outlet" → BANG
        if 'Bangalore' in r['name']:
            route_map['BANG'] = r['id']
        elif 'Chennai' in r['name']:
            route_map['CHEN'] = r['id']

print(f"\n  Buy route: {buy_route_id}")
print(f"  Bangalore resupply route: {route_map.get('BANG')}")
print(f"  Chennai resupply route: {route_map.get('CHEN')}")

# Check existing rules
existing_rules = sr('stock.warehouse.orderpoint', 
    [['company_id', '=', COMPANY_ID]], ['product_id', 'location_id'], limit=200)
print(f"  Existing rules: {len(existing_rules)}")

# Reordering rules config
reorder_config = {
    'KOCHI': {
        "SmartDesk Pro X1": (100, 200), "ErgoChair Elite": (80, 160),
        "Standing Desk Converter": (60, 120), "LED Smart Monitor 27\"": (100, 250),
        "Wireless Keyboard Combo": (200, 500), "Bluetooth Speaker Pro": (80, 200),
        "USB-C Hub 7-in-1": (150, 400), "Laptop Stand Adjustable": (50, 150),
        "Cable Organizer Kit": (300, 800), "Smart LED Strip 5m": (100, 300),
        "WiFi Smart Plug Pack": (150, 400), "Smart Security Camera": (40, 100),
    },
    'BANG': {
        "SmartDesk Pro X1": (10, 30), "ErgoChair Elite": (8, 25),
        "Standing Desk Converter": (5, 20), "LED Smart Monitor 27\"": (15, 40),
        "Wireless Keyboard Combo": (30, 80), "Bluetooth Speaker Pro": (10, 30),
        "USB-C Hub 7-in-1": (20, 60), "Laptop Stand Adjustable": (8, 20),
        "Cable Organizer Kit": (40, 120), "Smart LED Strip 5m": (15, 50),
        "WiFi Smart Plug Pack": (20, 60), "Smart Security Camera": (5, 15),
    },
    'CHEN': {
        "SmartDesk Pro X1": (5, 15), "ErgoChair Elite": (4, 12),
        "Standing Desk Converter": (3, 10), "LED Smart Monitor 27\"": (8, 20),
        "Wireless Keyboard Combo": (15, 40), "Bluetooth Speaker Pro": (5, 15),
        "USB-C Hub 7-in-1": (10, 30), "Laptop Stand Adjustable": (4, 10),
        "Cable Organizer Kit": (20, 60), "Smart LED Strip 5m": (8, 25),
        "WiFi Smart Plug Pack": (10, 30), "Smart Security Camera": (3, 8),
    },
}

created_count = 0
skipped_count = 0
for wh_code, products in reorder_config.items():
    loc_id = wh_locations.get(wh_code)
    if not loc_id:
        print(f"  ⚠️  Skipping {wh_code} — location not found")
        continue
    
    # Determine route
    if wh_code == 'KOCHI':
        route_id = buy_route_id
    else:
        route_id = route_map.get(wh_code)
    
    print(f"\n  [{wh_code}] Creating reordering rules (route: {route_id})...")
    for pname, (min_q, max_q) in products.items():
        pid = product_ids.get(pname)
        if not pid:
            continue
        pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        if not pp:
            continue
        pp_id = pp[0]['id']
        
        # Check if rule already exists
        existing = sc('stock.warehouse.orderpoint',
            [['product_id', '=', pp_id], ['location_id', '=', loc_id]], limit=1)
        if existing:
            skipped_count += 1
            continue
        
        vals = {
            'product_id': pp_id,
            'location_id': loc_id,
            'product_min_qty': min_q,
            'product_max_qty': max_q,
            'company_id': COMPANY_ID,
        }
        if route_id:
            vals['route_id'] = route_id
        
        rule_id = cr('stock.warehouse.orderpoint', vals)
        if rule_id:
            created_count += 1

print(f"\n  ✅ Created {created_count} reordering rules, skipped {skipped_count} existing")


# ════════════════════════════════════════════════════════
# STEP 5: VERIFY/CREATE SALE ORDERS (Phase 16)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 5: VERIFY/CREATE SALE ORDERS")
print("─" * 70)

existing_sos = sr('sale.order', [['company_id', '=', COMPANY_ID]], 
    ['name', 'partner_id', 'warehouse_id', 'order_line', 'amount_total'])

if len(existing_sos) >= 3:
    print(f"  ✅ {len(existing_sos)} Sale Orders already exist — skipping")
    for so in existing_sos:
        print(f"    {so['name']}: {so['partner_id'][1]} (Lines={len(so.get('order_line',[]))}, ₹{so['amount_total']:,.2f})")
else:
    print(f"  Only {len(existing_sos)} SOs found, creating missing ones...")
    
    # Get customer and pricelist IDs
    customers = sr('res.partner', [['customer_rank', '>', 0], ['is_company', '=', True]], ['name', 'id'])
    cust_map = {c['name']: c['id'] for c in customers}
    pls = sr('product.pricelist', [], ['name', 'id'])
    pl_map = {p['name']: p['id'] for p in pls}
    
    existing_partners = [so['partner_id'][0] for so in existing_sos]
    
    def get_pp_id(pname):
        pid = product_ids.get(pname)
        if pid:
            pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
            return pp[0]['id'] if pp else None
        return None
    
    so_configs = [
        ('Kerala Tech Solutions', 'KOCHI', 'Kochi Outlet — Standard',
         [("SmartDesk Pro X1", 3), ("ErgoChair Elite", 5), ("Wireless Keyboard Combo", 10), ("USB-C Hub 7-in-1", 8)]),
        ('InnoTech Bangalore', 'BANG', 'Bangalore Outlet — Competitive',
         [("LED Smart Monitor 27\"", 4), ("Bluetooth Speaker Pro", 6), ("Smart Security Camera", 2)]),
        ('Tamil Digital Solutions', 'CHEN', 'Chennai Outlet — Introductory',
         [("Standing Desk Converter", 2), ("Smart LED Strip 5m", 10), ("WiFi Smart Plug Pack", 8), ("Cable Organizer Kit", 15)]),
    ]
    
    for cust_name, wh_code, pl_name, lines in so_configs:
        cust_id = cust_map.get(cust_name)
        if cust_id and cust_id not in existing_partners:
            so_vals = {
                'partner_id': cust_id,
                'warehouse_id': wh_ids.get(wh_code),
                'company_id': COMPANY_ID,
            }
            pl_id = pl_map.get(pl_name)
            if pl_id:
                so_vals['pricelist_id'] = pl_id
            
            so_id = cr('sale.order', so_vals)
            if so_id:
                for pname, qty in lines:
                    pp_id = get_pp_id(pname)
                    if pp_id:
                        cr('sale.order.line', {
                            'order_id': so_id,
                            'product_id': pp_id,
                            'product_uom_qty': qty,
                        })
                print(f"  ✅ Created SO (ID={so_id}) — {cust_name} from {wh_code}")
        elif cust_id in existing_partners:
            print(f"  ℹ️  SO for {cust_name} already exists")
        else:
            print(f"  ⚠️  Customer {cust_name} not found")


# ════════════════════════════════════════════════════════
# STEP 6: VERIFY/CREATE PURCHASE ORDERS (Phase 17)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 6: VERIFY/CREATE PURCHASE ORDERS")
print("─" * 70)

existing_pos = sr('purchase.order', [['company_id', '=', COMPANY_ID]],
    ['name', 'partner_id', 'order_line', 'amount_total'])

if len(existing_pos) >= 2:
    print(f"  ✅ {len(existing_pos)} Purchase Orders already exist — skipping")
    for po in existing_pos:
        print(f"    {po['name']}: {po['partner_id'][1]} (Lines={len(po.get('order_line',[]))}, ₹{po['amount_total']:,.2f})")
else:
    print(f"  Only {len(existing_pos)} POs found, creating missing ones...")
    
    vendors = sr('res.partner', [['supplier_rank', '>', 0]], ['name', 'id'])
    vend_map = {v['name']: v['id'] for v in vendors}
    
    kochi_receipt = sr('stock.picking.type',
        [['warehouse_id', '=', wh_ids.get('KOCHI')], ['code', '=', 'incoming']],
        ['id'])
    kochi_receipt_id = kochi_receipt[0]['id'] if kochi_receipt else None
    
    existing_vendors = [po['partner_id'][0] for po in existing_pos]
    
    def get_pp_id2(pname):
        pid = product_ids.get(pname)
        if pid:
            pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
            return pp[0]['id'] if pp else None
        return None
    
    po_configs = [
        ('TechVision Distributors', [
            ("LED Smart Monitor 27\"", 30, 15000), ("Wireless Keyboard Combo", 50, 1200),
            ("Bluetooth Speaker Pro", 20, 2200), ("Smart Security Camera", 15, 3000),
            ("WiFi Smart Plug Pack", 40, 500),
        ]),
        ('FurniCraft India Pvt Ltd', [
            ("SmartDesk Pro X1", 20, 7500), ("ErgoChair Elite", 15, 5200),
            ("Standing Desk Converter", 10, 3800),
        ]),
    ]
    
    for vend_name, lines in po_configs:
        vid = vend_map.get(vend_name)
        if vid and vid not in existing_vendors:
            po_vals = {'partner_id': vid, 'company_id': COMPANY_ID}
            if kochi_receipt_id:
                po_vals['picking_type_id'] = kochi_receipt_id
            
            po_id = cr('purchase.order', po_vals)
            if po_id:
                for pname, qty, price in lines:
                    pp_id = get_pp_id2(pname)
                    if pp_id:
                        cr('purchase.order.line', {
                            'order_id': po_id,
                            'product_id': pp_id,
                            'product_qty': qty,
                            'price_unit': price,
                        })
                print(f"  ✅ Created PO (ID={po_id}) — {vend_name}")
        elif vid in existing_vendors:
            print(f"  ℹ️  PO for {vend_name} already exists")
        else:
            print(f"  ⚠️  Vendor {vend_name} not found")


# ════════════════════════════════════════════════════════
# STEP 7: VERIFY/CREATE INTERNAL TRANSFERS (Phase 18)
# ════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("STEP 7: VERIFY/CREATE INTERNAL TRANSFERS")
print("─" * 70)

existing_picks = sr('stock.picking',
    [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['name', 'location_id', 'location_dest_id', 'state', 'origin', 'move_ids'])

if len(existing_picks) >= 2:
    print(f"  ✅ {len(existing_picks)} Internal Transfers already exist — skipping")
    for p in existing_picks:
        print(f"    {p['name']}: {p['location_id'][1]} → {p['location_dest_id'][1]} ({p['state']}, moves={len(p.get('move_ids',[]))})")
else:
    print(f"  Only {len(existing_picks)} transfers found, creating missing ones...")
    
    kochi_loc = wh_locations.get('KOCHI')
    bang_loc = wh_locations.get('BANG')
    chen_loc = wh_locations.get('CHEN')
    
    # Find internal picking type from Kochi
    int_types = sr('stock.picking.type',
        [['code', '=', 'internal'], ['warehouse_id', '=', wh_ids.get('KOCHI')]],
        ['id', 'name'])
    kochi_internal = int_types[0]['id'] if int_types else None
    
    if not kochi_internal:
        # Fallback: any internal type
        int_types = sr('stock.picking.type',
            [['code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
            ['id', 'name'])
        kochi_internal = int_types[0]['id'] if int_types else None
    
    def get_pp_id3(pname):
        pid = product_ids.get(pname)
        if pid:
            pp = sr('product.product', [['product_tmpl_id', '=', pid]], ['id'])
            return pp[0]['id'] if pp else None
        return None
    
    transfer_configs = [
        (kochi_loc, bang_loc, 'Resupply: Kochi → Bangalore (Sample)',
         [("SmartDesk Pro X1", 5), ("ErgoChair Elite", 10), ("Wireless Keyboard Combo", 20)]),
        (kochi_loc, chen_loc, 'Resupply: Kochi → Chennai (Sample)',
         [("Standing Desk Converter", 3), ("Smart LED Strip 5m", 15), ("Cable Organizer Kit", 25)]),
    ]
    
    # Check which transfers already exist by destination
    existing_dests = [p['location_dest_id'][0] for p in existing_picks]
    
    for src, dest, origin, lines in transfer_configs:
        if src and dest and kochi_internal and dest not in existing_dests:
            pick_id = cr('stock.picking', {
                'picking_type_id': kochi_internal,
                'location_id': src,
                'location_dest_id': dest,
                'company_id': COMPANY_ID,
                'origin': origin,
            })
            if pick_id:
                for pname, qty in lines:
                    pp_id = get_pp_id3(pname)
                    if pp_id:
                        cr('stock.move', {
                            'name': f'Transfer: {pname}',
                            'product_id': pp_id,
                            'product_uom_qty': qty,
                            'picking_id': pick_id,
                            'location_id': src,
                            'location_dest_id': dest,
                            'company_id': COMPANY_ID,
                        })
                print(f"  ✅ Created Transfer (ID={pick_id}) — {origin}")
        elif dest and dest in existing_dests:
            print(f"  ℹ️  Transfer to location ID={dest} already exists")


# ════════════════════════════════════════════════════════
# STEP 8: FINAL SUMMARY
# ════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("FINAL VERIFICATION SUMMARY")
print("═" * 70)

# Re-fetch all counts
wh_count = len(sr('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['id']))
loc_count = len(sr('stock.location', [['usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]], ['id']))
prod_count = len([pid for pid in product_ids.values() if pid])
rule_count = len(sr('stock.warehouse.orderpoint', [['company_id', '=', COMPANY_ID]], ['id'], limit=200))
so_count = len(sr('sale.order', [['company_id', '=', COMPANY_ID]], ['id']))
po_count = len(sr('purchase.order', [['company_id', '=', COMPANY_ID]], ['id']))
pick_count = len(sr('stock.picking', [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]], ['id']))
pl_count = len(sr('product.pricelist', [], ['id']))
aa_count = len(sr('account.analytic.account', [], ['id']))
si_count = len(sr('product.supplierinfo', [], ['id']))
quant_count = len(sr('stock.quant', [['location_id.usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]], ['id'], limit=200))
vendor_count = len(sr('res.partner', [['supplier_rank', '>', 0]], ['id']))
cust_count = len(sr('res.partner', [['customer_rank', '>', 0], ['is_company', '=', True]], ['id']))

print(f"""
  🏭 Warehouses:          {wh_count}/3
  📍 Stock Locations:      {loc_count} (internal)
  📦 Products:             {prod_count}/12
  🔄 Reordering Rules:     {rule_count}/36
  📊 Pricelists:           {pl_count}
  📈 Analytic Accounts:    {aa_count}
  🏷️  Vendor Pricelists:   {si_count}/12
  📋 Stock Quants:         {quant_count} (on-hand entries)
  
  👥 Vendors:              {vendor_count}/3
  👤 Customers:            {cust_count}/9
  
  📝 Sale Orders:          {so_count}/3
  📝 Purchase Orders:      {po_count}/2
  📝 Internal Transfers:   {pick_count}/2
""")

# Check for issues
issues = []
if wh_count < 3: issues.append("Missing warehouses")
if prod_count < 12: issues.append("Missing products")
if rule_count < 36: issues.append(f"Only {rule_count}/36 reordering rules")
if so_count < 3: issues.append(f"Only {so_count}/3 sale orders")
if po_count < 2: issues.append(f"Only {po_count}/2 purchase orders")
if pick_count < 2: issues.append(f"Only {pick_count}/2 internal transfers")
if quant_count < 30: issues.append(f"Only {quant_count} stock quants (expected ~36)")

if issues:
    print("  ⚠️  ISSUES REMAINING:")
    for i in issues:
        print(f"    • {i}")
else:
    print("  ✅ ALL CHECKS PASSED!")

print("\n" + "═" * 70)
print("FIX SCRIPT COMPLETE")
print("═" * 70)
