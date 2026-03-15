"""
============================================================================
INTER-BRANCH TRANSFER VIA INTER-COMPANY TRANSIT LOCATION
============================================================================
Demonstrates: Krishnadas Group WH → Inter-company Transit → Devika Furniture DF

KEY FINDING:
  Location [3] "Inter-company transit" — usage=transit, NO company assigned
  This is the bridge location for moving goods between branches/companies.

FLOW (2-step manual):
  Transfer 1: WH/Stock (Krishnadas) → Inter-company transit  [done by Krishnadas]
  Transfer 2: Inter-company transit  → DF/Stock (Devika)      [done by Devika]

This simulates real-world inter-branch stock movement.
============================================================================
"""

import xmlrpc.client
import sys

URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

print("=" * 70)
print("  INTER-BRANCH TRANSFER: Krishnadas → Transit → Devika")
print("=" * 70)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("  ❌ Auth failed!"); sys.exit(1)
print(f"  ✅ Connected as UID={uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def execute(model, method, *args, **kwargs):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
    except Exception as e:
        print(f"  ⚠️  {model}.{method}: {e}")
        return None

def sr(m, d, f, limit=0):
    kw = {'fields': f}
    if limit: kw['limit'] = limit
    return execute(m, 'search_read', [d], kw) or []

def create(m, v):
    return execute(m, 'create', [v])

def write(m, ids, v):
    if not isinstance(ids, list): ids = [ids]
    return execute(m, 'write', [ids, v])

# ─────────────────────────────────────────────
# IDs we need
# ─────────────────────────────────────────────
KRISHNADAS_ID = 1
DEVIKA_ID = 2

# Locations
INTER_COMPANY_TRANSIT_ID = 3   # Inter-company transit (no company, usage=transit)
WH_STOCK_ID = 5                # WH/Stock (Krishnadas Group)
DF_STOCK_ID = 66               # DF/Stock (Devika Furniture)

# Picking types (operation types) — we need internal transfer types
print("\n[1] Finding operation types...")
picking_types = sr('stock.picking.type', [], ['name', 'code', 'warehouse_id', 'company_id',
                                               'default_location_src_id', 'default_location_dest_id'])
print(f"  Found {len(picking_types)} operation types:")
for pt in picking_types:
    wh = pt['warehouse_id'][1] if pt['warehouse_id'] else 'N/A'
    co = pt['company_id'][1] if pt['company_id'] else 'N/A'
    src = pt['default_location_src_id'][1] if pt['default_location_src_id'] else 'N/A'
    dest = pt['default_location_dest_id'][1] if pt['default_location_dest_id'] else 'N/A'
    print(f"    {pt['name']:35s} | code={pt['code']:12s} | {wh:30s} | {co}")
    print(f"      Default: {src} → {dest}")

# Find internal transfer type for Krishnadas Group
krishnadas_internal = [pt for pt in picking_types 
                        if pt['code'] == 'internal' 
                        and pt['company_id'] and pt['company_id'][0] == KRISHNADAS_ID]

# Find internal transfer type for Devika Furniture  
devika_internal = [pt for pt in picking_types 
                    if pt['code'] == 'internal' 
                    and pt['company_id'] and pt['company_id'][0] == DEVIKA_ID]

# Also find the receipt type for Devika (in case we need it)
devika_receipt = [pt for pt in picking_types 
                   if pt['code'] == 'incoming' 
                   and pt['company_id'] and pt['company_id'][0] == DEVIKA_ID]

# Get products to transfer
print("\n[2] Finding products to transfer...")
products_to_transfer = [
    ('PVC Blinds', 20),
    ('Readymade Blackout Curtain 7ft', 10),
    ('Velvet Cushion Cover 16x16', 15),
]

prod_map = {}
for pname, _ in products_to_transfer:
    pp = sr('product.product', [['name', '=', pname]], ['id', 'uom_id'], limit=1)
    if pp:
        prod_map[pname] = {'id': pp[0]['id'], 'uom_id': pp[0]['uom_id'][0]}
        print(f"  ✅ {pname} (ID:{pp[0]['id']}, UOM: {pp[0]['uom_id'][1]})")
    else:
        print(f"  ⚠️  {pname} not found!")

# Check current stock before transfer
print("\n[3] Current stock BEFORE transfer:")
for pname, _ in products_to_transfer:
    if pname not in prod_map: continue
    pid = prod_map[pname]['id']
    
    # At Krishnadas WH/Stock
    q1 = sr('stock.quant', [['product_id','=',pid],['location_id','=',WH_STOCK_ID]], ['quantity'])
    qty1 = q1[0]['quantity'] if q1 else 0
    
    # At Devika DF/Stock
    q2 = sr('stock.quant', [['product_id','=',pid],['location_id','=',DF_STOCK_ID]], ['quantity'])
    qty2 = q2[0]['quantity'] if q2 else 0
    
    # At Inter-company transit
    q3 = sr('stock.quant', [['product_id','=',pid],['location_id','=',INTER_COMPANY_TRANSIT_ID]], ['quantity'])
    qty3 = q3[0]['quantity'] if q3 else 0
    
    print(f"  {pname:40s} | WH/Stock: {qty1:6.0f} | Transit: {qty3:6.0f} | DF/Stock: {qty2:6.0f}")


# ═══════════════════════════════════════════════
# TRANSFER 1: Krishnadas WH/Stock → Inter-company Transit
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("  TRANSFER 1: Krishnadas WH/Stock → Inter-company Transit")
print("═" * 70)

# Use Krishnadas internal transfer type
if krishnadas_internal:
    k_pt_id = krishnadas_internal[0]['id']
    print(f"  Using picking type: {krishnadas_internal[0]['name']} (ID:{k_pt_id})")
else:
    print("  ⚠️  No internal transfer type for Krishnadas! Trying generic...")
    # Fallback: find any internal type
    all_internal = [pt for pt in picking_types if pt['code'] == 'internal']
    k_pt_id = all_internal[0]['id'] if all_internal else None

if not k_pt_id:
    print("  ❌ No internal picking type found!")
    sys.exit(1)

# Create the picking (internal transfer)
picking1_vals = {
    'picking_type_id': k_pt_id,
    'location_id': WH_STOCK_ID,                  # Source: Krishnadas WH/Stock
    'location_dest_id': INTER_COMPANY_TRANSIT_ID, # Dest: Inter-company transit
    'company_id': KRISHNADAS_ID,
    'origin': 'Inter-Branch: Krishnadas → Devika (Step 1)',
}

picking1_id = create('stock.picking', picking1_vals)
if not picking1_id:
    print("  ❌ Failed to create Transfer 1!")
    sys.exit(1)
print(f"  ✅ Created Transfer 1 (ID:{picking1_id})")

# Add move lines
for pname, qty in products_to_transfer:
    if pname not in prod_map: continue
    move_vals = {
        'product_id': prod_map[pname]['id'],
        'product_uom_qty': qty,
        'product_uom': prod_map[pname]['uom_id'],
        'picking_id': picking1_id,
        'location_id': WH_STOCK_ID,
        'location_dest_id': INTER_COMPANY_TRANSIT_ID,
        'company_id': KRISHNADAS_ID,
    }
    move_id = create('stock.move', move_vals)
    if move_id:
        print(f"    + {pname} x{qty} (move ID:{move_id})")
    else:
        print(f"    ❌ Failed to add move for {pname}")

# Confirm (Mark as Todo) and Validate the transfer
print("\n  Confirming Transfer 1...")
try:
    execute('stock.picking', 'action_confirm', [[picking1_id]])
    print("  ✅ Transfer 1 confirmed (Ready state)")
except Exception as e:
    print(f"  ⚠️  Confirm: {e}")

# Set quantities done on move lines
print("  Setting quantities done...")
moves1 = sr('stock.move', [['picking_id','=',picking1_id]], ['id','product_id','product_uom_qty','quantity'])
for m in moves1:
    write('stock.move', [m['id']], {'quantity': m['product_uom_qty']})
    pname = m['product_id'][1] if m['product_id'] else '?'
    print(f"    ✅ {pname}: qty_done = {m['product_uom_qty']}")

# Validate (complete the transfer)
print("  Validating Transfer 1...")
try:
    result = execute('stock.picking', 'button_validate', [[picking1_id]])
    print(f"  ✅ Transfer 1 validated! (result: {result})")
except Exception as e:
    print(f"  ⚠️  Validate: {e}")
    # Try with immediate transfer wizard if needed
    print("  Trying alternative validation...")
    try:
        # Check picking state
        p1_state = sr('stock.picking', [['id','=',picking1_id]], ['state'])
        print(f"  Current state: {p1_state[0]['state'] if p1_state else 'unknown'}")
    except:
        pass

# Check Transfer 1 result
p1_info = sr('stock.picking', [['id','=',picking1_id]], ['name','state','company_id'])
if p1_info:
    print(f"\n  Transfer 1: {p1_info[0]['name']} — State: {p1_info[0]['state']}")


# ═══════════════════════════════════════════════
# TRANSFER 2: Inter-company Transit → Devika DF/Stock
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("  TRANSFER 2: Inter-company Transit → Devika DF/Stock")
print("═" * 70)

# Use Devika picking type
if devika_internal:
    d_pt_id = devika_internal[0]['id']
    print(f"  Using picking type: {devika_internal[0]['name']} (ID:{d_pt_id})")
elif devika_receipt:
    d_pt_id = devika_receipt[0]['id']
    print(f"  Using receipt type: {devika_receipt[0]['name']} (ID:{d_pt_id})")
else:
    print("  ⚠️  No picking type for Devika! Using Krishnadas internal...")
    d_pt_id = k_pt_id

# Create the picking
picking2_vals = {
    'picking_type_id': d_pt_id,
    'location_id': INTER_COMPANY_TRANSIT_ID,  # Source: Inter-company transit
    'location_dest_id': DF_STOCK_ID,          # Dest: Devika DF/Stock
    'company_id': DEVIKA_ID,
    'origin': 'Inter-Branch: Krishnadas → Devika (Step 2)',
}

picking2_id = create('stock.picking', picking2_vals)
if not picking2_id:
    print("  ❌ Failed to create Transfer 2!")
    sys.exit(1)
print(f"  ✅ Created Transfer 2 (ID:{picking2_id})")

# Add move lines
for pname, qty in products_to_transfer:
    if pname not in prod_map: continue
    move_vals = {
        'product_id': prod_map[pname]['id'],
        'product_uom_qty': qty,
        'product_uom': prod_map[pname]['uom_id'],
        'picking_id': picking2_id,
        'location_id': INTER_COMPANY_TRANSIT_ID,
        'location_dest_id': DF_STOCK_ID,
        'company_id': DEVIKA_ID,
    }
    move_id = create('stock.move', move_vals)
    if move_id:
        print(f"    + {pname} x{qty} (move ID:{move_id})")
    else:
        print(f"    ❌ Failed to add move for {pname}")

# Confirm
print("\n  Confirming Transfer 2...")
try:
    execute('stock.picking', 'action_confirm', [[picking2_id]])
    print("  ✅ Transfer 2 confirmed (Ready state)")
except Exception as e:
    print(f"  ⚠️  Confirm: {e}")

# Set quantities done
print("  Setting quantities done...")
moves2 = sr('stock.move', [['picking_id','=',picking2_id]], ['id','product_id','product_uom_qty','quantity'])
for m in moves2:
    write('stock.move', [m['id']], {'quantity': m['product_uom_qty']})
    pname = m['product_id'][1] if m['product_id'] else '?'
    print(f"    ✅ {pname}: qty_done = {m['product_uom_qty']}")

# Validate
print("  Validating Transfer 2...")
try:
    result = execute('stock.picking', 'button_validate', [[picking2_id]])
    print(f"  ✅ Transfer 2 validated! (result: {result})")
except Exception as e:
    print(f"  ⚠️  Validate: {e}")
    p2_state = sr('stock.picking', [['id','=',picking2_id]], ['state'])
    print(f"  Current state: {p2_state[0]['state'] if p2_state else 'unknown'}")

# Check Transfer 2 result
p2_info = sr('stock.picking', [['id','=',picking2_id]], ['name','state','company_id'])
if p2_info:
    print(f"\n  Transfer 2: {p2_info[0]['name']} — State: {p2_info[0]['state']}")


# ═══════════════════════════════════════════════
# FINAL: CHECK STOCK AFTER TRANSFER
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("  STOCK AFTER INTER-BRANCH TRANSFER")
print("═" * 70)

for pname, qty_transferred in products_to_transfer:
    if pname not in prod_map: continue
    pid = prod_map[pname]['id']
    
    q1 = sr('stock.quant', [['product_id','=',pid],['location_id','=',WH_STOCK_ID]], ['quantity'])
    qty1 = q1[0]['quantity'] if q1 else 0
    
    q2 = sr('stock.quant', [['product_id','=',pid],['location_id','=',DF_STOCK_ID]], ['quantity'])
    qty2 = q2[0]['quantity'] if q2 else 0
    
    q3 = sr('stock.quant', [['product_id','=',pid],['location_id','=',INTER_COMPANY_TRANSIT_ID]], ['quantity'])
    qty3 = q3[0]['quantity'] if q3 else 0
    
    print(f"  {pname:40s} | WH/Stock: {qty1:6.0f} | Transit: {qty3:6.0f} | DF/Stock: {qty2:6.0f}")

# Show all transfer records
print("\n📋 TRANSFER RECORDS:")
transfers = sr('stock.picking', 
    [['id','in',[picking1_id, picking2_id]]], 
    ['name','state','origin','location_id','location_dest_id','company_id','date_done'])
for t in transfers:
    src = t['location_id'][1] if t['location_id'] else 'N/A'
    dest = t['location_dest_id'][1] if t['location_dest_id'] else 'N/A'
    co = t['company_id'][1] if t['company_id'] else 'N/A'
    print(f"  {t['name']:12s} | {t['state']:10s} | {src} → {dest} | {co}")
    print(f"               | {t['origin']}")

print("\n" + "═" * 70)
print("  ✅ INTER-BRANCH TRANSFER COMPLETE!")
print("═" * 70)
print("""
  WHAT HAPPENED:
  ──────────────
  Step 1: Krishnadas WH/Stock → Inter-company Transit
          (Krishnadas sent goods out via internal transfer)
  
  Step 2: Inter-company Transit → Devika DF/Stock
          (Devika received goods via internal transfer)
  
  The "Inter-company transit" location (ID:3) acts as a neutral
  bridge with NO company assigned — both branches can access it.
  
  This is the standard Odoo pattern for inter-branch/inter-company
  stock transfers without needing purchase/sale orders between them.
""")
