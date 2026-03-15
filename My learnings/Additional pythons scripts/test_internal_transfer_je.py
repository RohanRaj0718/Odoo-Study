"""
COMPREHENSIVE TEST: Internal Transfers & Journal Entries in Odoo 19
===================================================================
Creates test products with different valuation configs, performs internal
transfers between branches, and checks for journal entry creation.

Test Matrix:
  A) Periodic + Standard Cost  (current default)
  B) Perpetual + Standard Cost
  C) Perpetual + AVCO
  D) Perpetual + FIFO

Transfer Types:
  1) Within same company (warehouse to warehouse)
  2) Inter-company (KG → Devika branch)
"""
import xmlrpc.client
import time

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
assert uid, "Authentication failed!"
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
print(f"✅ Authenticated as UID={uid}\n")

def ex(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kw)

def sr(model, domain, fields, limit=50):
    return ex(model, 'search_read', [domain], {'fields': fields, 'limit': limit})

def create(model, vals):
    return ex(model, 'create', [vals])

# ════════════════════════════════════════════════════════════════════
# STEP 1: Create test product categories with different valuations
# ════════════════════════════════════════════════════════════════════
print("=" * 70)
print("STEP 1: Creating test product categories")
print("=" * 70)

# First, find stock valuation accounts for perpetual mode
# We need: Stock Input, Stock Output, Stock Valuation accounts
# Check what accounts exist
print("\nLooking for stock-related accounts...")
stock_accounts = sr('account.account', 
    [['name', 'ilike', 'stock'], ['company_id', '=', 1]], 
    ['name', 'code', 'account_type'], limit=20)

if not stock_accounts:
    # Try inventory-related
    stock_accounts = sr('account.account', 
        [['name', 'ilike', 'inventor'], ['company_id', '=', 1]], 
        ['name', 'code', 'account_type'], limit=20)

if not stock_accounts:
    # Try all asset accounts
    stock_accounts = sr('account.account', 
        [['account_type', 'ilike', 'asset'], ['company_id', '=', 1]], 
        ['name', 'code', 'account_type'], limit=30)

print("Available accounts that could serve as stock accounts:")
for a in stock_accounts:
    print(f"  [{a['id']:4d}] {a['code']:8s} | {a['name']:40s} | {a['account_type']}")

# Also check expense accounts for stock output
expense_accounts = sr('account.account',
    [['account_type', 'in', ['expense', 'expense_direct_cost']], ['company_id', '=', 1]],
    ['name', 'code', 'account_type'], limit=15)
print("\nExpense accounts (for COGS/stock output):")
for a in expense_accounts:
    print(f"  [{a['id']:4d}] {a['code']:8s} | {a['name']:40s} | {a['account_type']}")

# Check existing category 'Goods' (id=1) for any accounts set
goods_cat = sr('product.category', [['id', '=', 1]], 
    ['name', 'property_cost_method', 'property_valuation',
     'property_stock_account_input_categ_id', 'property_stock_account_output_categ_id',
     'property_stock_valuation_account_id', 'property_stock_journal'])
print(f"\nExisting 'Goods' category config:")
for k, v in goods_cat[0].items():
    if k != 'id':
        print(f"  {k}: {v}")

# ════════════════════════════════════════════════════════════════════
# Now create test categories
# ════════════════════════════════════════════════════════════════════

test_categories = {}
cat_configs = [
    ("TEST-Periodic-Std", "standard", "periodic"),
    ("TEST-Perpetual-Std", "standard", "real_time"),
    ("TEST-Perpetual-AVCO", "average", "real_time"),
    ("TEST-Perpetual-FIFO", "fifo", "real_time"),
]

# Check if test categories already exist
existing = sr('product.category', [['name', 'ilike', 'TEST-']], ['name'])
existing_names = {e['name'] for e in existing}

for cat_name, cost_method, valuation in cat_configs:
    if cat_name in existing_names:
        cat = sr('product.category', [['name', '=', cat_name]], ['id'])
        test_categories[cat_name] = cat[0]['id']
        print(f"  ♻ Category '{cat_name}' already exists (ID={cat[0]['id']})")
    else:
        vals = {
            'name': cat_name,
            'parent_id': 1,  # Under 'Goods'
            'property_cost_method': cost_method,
            'property_valuation': valuation,
        }
        # For perpetual, we might need stock accounts — try creating without first
        try:
            cat_id = create('product.category', vals)
            test_categories[cat_name] = cat_id
            print(f"  ✅ Created '{cat_name}' (ID={cat_id}) — {cost_method}/{valuation}")
        except Exception as e:
            print(f"  ⚠ Error creating '{cat_name}': {e}")
            # If it fails, we'll try with accounts
            test_categories[cat_name] = None

print(f"\nTest categories: {test_categories}")

# ════════════════════════════════════════════════════════════════════
# STEP 2: Create test products
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 2: Creating test products")
print("=" * 70)

test_products = {}
for cat_name, cat_id in test_categories.items():
    if cat_id is None:
        continue
    
    prod_name = f"ZZ-TEST-{cat_name.replace('TEST-', '')}"
    
    # Check if product exists
    existing_prod = sr('product.product', [['name', '=', prod_name]], ['id'])
    if existing_prod:
        test_products[cat_name] = existing_prod[0]['id']
        print(f"  ♻ Product '{prod_name}' already exists (ID={existing_prod[0]['id']})")
        continue
    
    vals = {
        'name': prod_name,
        'type': 'consu',  # Goods in Odoo 19
        'categ_id': cat_id,
        'list_price': 100.0,
        'standard_price': 50.0,
    }
    try:
        prod_id = create('product.product', vals)
        test_products[cat_name] = prod_id
        print(f"  ✅ Created '{prod_name}' (ID={prod_id}) — Category: {cat_name}")
    except Exception as e:
        print(f"  ⚠ Error creating '{prod_name}': {e}")
        test_products[cat_name] = None

print(f"\nTest products: {test_products}")

# ════════════════════════════════════════════════════════════════════
# STEP 3: Add initial stock via inventory adjustment for KG (company 1)
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 3: Setting initial stock via stock.quant")
print("=" * 70)

# Find KG main warehouse stock location
kg_stock_loc = sr('stock.location', 
    [['complete_name', 'ilike', 'WH/Stock'], ['company_id', '=', 1], ['usage', '=', 'internal']], 
    ['name', 'complete_name'], limit=5)
print(f"KG stock locations: {[(l['id'], l['complete_name']) for l in kg_stock_loc]}")

if kg_stock_loc:
    kg_stock_loc_id = kg_stock_loc[0]['id']
    print(f"Using location: {kg_stock_loc[0]['complete_name']} (ID={kg_stock_loc_id})")
    
    for cat_name, prod_id in test_products.items():
        if prod_id is None:
            continue
        
        # Check current stock
        quants = sr('stock.quant', 
            [['product_id', '=', prod_id], ['location_id', '=', kg_stock_loc_id]], 
            ['quantity', 'inventory_quantity'])
        
        if quants and quants[0]['quantity'] >= 50:
            print(f"  ♻ Product {prod_id} already has stock: {quants[0]['quantity']}")
            continue
        
        # Use inventory adjustment
        try:
            # Set inventory quantity
            if quants:
                quant_id = quants[0]['id']
                ex('stock.quant', 'write', [[quant_id], {'inventory_quantity': 100}])
            else:
                # Create a quant
                quant_id = create('stock.quant', {
                    'product_id': prod_id,
                    'location_id': kg_stock_loc_id,
                    'inventory_quantity': 100,
                })
            
            # Apply inventory adjustment
            try:
                ex('stock.quant', 'action_apply_inventory', [[quant_id]])
                print(f"  ✅ Set 100 units stock for product {prod_id} at {kg_stock_loc[0]['complete_name']}")
            except Exception as e:
                print(f"  ⚠ Could not apply inventory for product {prod_id}: {e}")
                
        except Exception as e:
            print(f"  ⚠ Error setting stock for product {prod_id}: {e}")

# ════════════════════════════════════════════════════════════════════
# STEP 4: Record journal entries BEFORE transfers
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 4: Recording journal entries BEFORE transfers")
print("=" * 70)

stj_journal_ids = [13, 23, 33, 39]
all_journal_ids = [j['id'] for j in sr('account.journal', [['type', '=', 'general']], ['id'])]

je_before = {}
for jid in all_journal_ids:
    count = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
    je_before[jid] = count

misc_before = {}
for jid in [9, 18, 32, 38]:  # MISC journals for all companies
    entries = sr('account.move', [['journal_id', '=', jid]], ['name'], limit=100)
    misc_before[jid] = len(entries)

stj_before = {}
for jid in stj_journal_ids:
    entries = sr('account.move', [['journal_id', '=', jid]], ['name'], limit=100)
    stj_before[jid] = len(entries)
    
total_moves_before = ex('account.move', 'search_count', [[]])
print(f"Total journal entries before transfers: {total_moves_before}")
print(f"STJ entries before: {stj_before}")
print(f"MISC entries before: {misc_before}")

# Also record stock moves linked to JEs
moves_with_je_before = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"Stock moves linked to JEs before: {moves_with_je_before}")

# ════════════════════════════════════════════════════════════════════
# STEP 5: Create internal transfers
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 5: Creating internal transfers")
print("=" * 70)

# Find picking types for internal transfers
int_pick_types = sr('stock.picking.type', 
    [['code', '=', 'internal']], 
    ['name', 'warehouse_id', 'company_id', 'default_location_src_id', 'default_location_dest_id'], 
    limit=20)
print("Internal transfer picking types:")
for pt in int_pick_types:
    wh = pt['warehouse_id'][1] if pt['warehouse_id'] else 'N/A'
    comp = pt['company_id'][1] if pt['company_id'] else 'N/A'
    src = pt['default_location_src_id'][1] if pt['default_location_src_id'] else 'N/A'
    dst = pt['default_location_dest_id'][1] if pt['default_location_dest_id'] else 'N/A'
    print(f"  [{pt['id']:3d}] {pt['name']:35s} | WH: {wh:15s} | Comp: {comp[:15]} | {src} → {dst}")

# Find destination locations
# Devika stock location
devika_loc = sr('stock.location', 
    [['complete_name', 'ilike', 'DF'], ['usage', '=', 'internal'], ['company_id', '=', 2]], 
    ['name', 'complete_name'], limit=5)
print(f"\nDevika locations: {[(l['id'], l['complete_name']) for l in devika_loc]}")

# NH GF location (within KG)
nhgf_loc = sr('stock.location', 
    [['complete_name', 'ilike', 'NH GF'], ['usage', '=', 'internal']], 
    ['name', 'complete_name'], limit=5)
print(f"NH GF locations: {[(l['id'], l['complete_name']) for l in nhgf_loc]}")

# KG internal transfer picking type
kg_int_pt = [pt for pt in int_pick_types if pt['company_id'] and pt['company_id'][0] == 1]

if not kg_int_pt:
    print("  ⚠ No internal transfer picking type found for KG!")
else:
    kg_int_pt_id = kg_int_pt[0]['id']
    print(f"\nUsing KG internal transfer picking type: {kg_int_pt[0]['name']} (ID={kg_int_pt_id})")

transfer_results = []

for cat_name, prod_id in test_products.items():
    if prod_id is None:
        continue
    
    # ── Transfer Type 1: Within KG (WH/Stock → NH GF/Stock) ──
    if nhgf_loc and kg_stock_loc:
        nhgf_id = nhgf_loc[0]['id']
        
        try:
            pick_vals = {
                'picking_type_id': kg_int_pt_id,
                'location_id': kg_stock_loc_id,
                'location_dest_id': nhgf_id,
                'company_id': 1,
                'move_ids_without_package': [(0, 0, {
                    'name': f'TEST-{cat_name}-IntraCompany',
                    'product_id': prod_id,
                    'product_uom_qty': 5,
                    'location_id': kg_stock_loc_id,
                    'location_dest_id': nhgf_id,
                    'company_id': 1,
                })]
            }
            pick_id = create('stock.picking', pick_vals)
            print(f"\n  ✅ Created intra-company transfer for {cat_name} (picking ID={pick_id})")
            
            # Confirm
            try:
                ex('stock.picking', 'action_confirm', [[pick_id]])
                print(f"     Confirmed")
            except Exception as e:
                print(f"     Confirm error: {e}")
            
            # Set quantities done on move lines
            move_lines = sr('stock.move', [['picking_id', '=', pick_id]], ['id', 'quantity'])
            for ml in move_lines:
                ex('stock.move', 'write', [[ml['id']], {'quantity': 5}])
            
            # Validate
            try:
                result = ex('stock.picking', 'button_validate', [[pick_id]])
                print(f"     Validated ✅ (result: {result})")
            except Exception as e:
                # Might need to handle wizard
                print(f"     Validate result: {e}")
                # Try force validate
                try:
                    ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                    result = ex('stock.picking', 'button_validate', [[pick_id]])
                    print(f"     Re-validated ✅")
                except Exception as e2:
                    print(f"     Re-validate error: {e2}")
            
            transfer_results.append({
                'category': cat_name,
                'type': 'Intra-Company (WH→NH GF)',
                'picking_id': pick_id,
                'product_id': prod_id,
            })
            
        except Exception as e:
            print(f"  ⚠ Error creating intra-company transfer for {cat_name}: {e}")

    # ── Transfer Type 2: Inter-company (KG → Devika) ──
    if devika_loc:
        devika_stock_id = devika_loc[0]['id']
        
        # Need inter-company transit location
        transit_loc = sr('stock.location', 
            [['name', 'ilike', 'inter-company'], ['usage', '=', 'transit']], 
            ['name', 'complete_name'], limit=5)
        
        if not transit_loc:
            transit_loc = sr('stock.location', 
                [['usage', '=', 'transit']], 
                ['name', 'complete_name'], limit=5)
        
        if transit_loc:
            transit_id = transit_loc[0]['id']
            
            try:
                pick_vals = {
                    'picking_type_id': kg_int_pt_id,
                    'location_id': kg_stock_loc_id,
                    'location_dest_id': transit_id,
                    'company_id': 1,
                    'move_ids_without_package': [(0, 0, {
                        'name': f'TEST-{cat_name}-InterCompany',
                        'product_id': prod_id,
                        'product_uom_qty': 3,
                        'location_id': kg_stock_loc_id,
                        'location_dest_id': transit_id,
                        'company_id': 1,
                    })]
                }
                pick_id = create('stock.picking', pick_vals)
                print(f"\n  ✅ Created inter-company transfer for {cat_name} (picking ID={pick_id})")
                
                # Confirm
                try:
                    ex('stock.picking', 'action_confirm', [[pick_id]])
                    print(f"     Confirmed")
                except Exception as e:
                    print(f"     Confirm error: {e}")
                
                # Set quantities
                move_lines = sr('stock.move', [['picking_id', '=', pick_id]], ['id'])
                for ml in move_lines:
                    ex('stock.move', 'write', [[ml['id']], {'quantity': 3}])
                
                # Validate
                try:
                    result = ex('stock.picking', 'button_validate', [[pick_id]])
                    print(f"     Validated ✅ (result: {result})")
                except Exception as e:
                    print(f"     Validate result: {e}")
                    try:
                        ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                        result = ex('stock.picking', 'button_validate', [[pick_id]])
                        print(f"     Re-validated ✅")
                    except Exception as e2:
                        print(f"     Re-validate error: {e2}")
                
                transfer_results.append({
                    'category': cat_name,
                    'type': 'Inter-Company (KG→Transit)',
                    'picking_id': pick_id,
                    'product_id': prod_id,
                })
                
            except Exception as e:
                print(f"  ⚠ Error creating inter-company transfer for {cat_name}: {e}")

print(f"\n\nTotal transfers created: {len(transfer_results)}")

# ════════════════════════════════════════════════════════════════════
# STEP 6: Wait and check for journal entries
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 6: CHECKING FOR JOURNAL ENTRIES AFTER TRANSFERS")
print("=" * 70)

time.sleep(2)  # Small wait for any async processing

# Check each transfer for linked JEs
print("\n📋 RESULTS PER TRANSFER:")
print("-" * 70)
for tr in transfer_results:
    pick = sr('stock.picking', [['id', '=', tr['picking_id']]], ['name', 'state'])
    pick_name = pick[0]['name'] if pick else 'N/A'
    pick_state = pick[0]['state'] if pick else 'N/A'
    
    # Check stock moves for this picking
    moves = sr('stock.move', [['picking_id', '=', tr['picking_id']]], 
        ['reference', 'state', 'account_move_id', 'quantity'])
    
    je_found = False
    for m in moves:
        if m['account_move_id']:
            je_found = True
    
    status = "✅ JE CREATED" if je_found else "❌ NO JE"
    je_ref = moves[0]['account_move_id'][1] if moves and moves[0]['account_move_id'] else "None"
    
    print(f"  {pick_name:15s} | {tr['category']:25s} | {tr['type']:30s} | State: {pick_state:7s} | {status} | JE: {je_ref}")

# Check overall JE counts
print("\n📋 OVERALL JOURNAL ENTRY COMPARISON:")
print("-" * 70)

total_moves_after = ex('account.move', 'search_count', [[]])
print(f"Total JEs before: {total_moves_before}")
print(f"Total JEs after:  {total_moves_after}")
print(f"New JEs created:  {total_moves_after - total_moves_before}")

# Check STJ journals
print("\nInventory Valuation Journal (STJ) entries:")
stj_names = {13: 'KG', 23: 'KFURN', 33: 'Devika', 39: 'KDESIGN'}
for jid in stj_journal_ids:
    entries = sr('account.move', [['journal_id', '=', jid]], ['name', 'date', 'amount_total', 'ref'], limit=100)
    after_count = len(entries)
    before_count = stj_before.get(jid, 0)
    marker = "🆕 NEW!" if after_count > before_count else "No change"
    print(f"  STJ {stj_names.get(jid, jid):8s}: Before={before_count}, After={after_count} — {marker}")
    if after_count > before_count:
        for e in entries:
            print(f"    → {e['name']} | {e['date']} | ₹{e['amount_total']:,.2f} | {e.get('ref', 'N/A')}")

# Check MISC journals
print("\nMiscellaneous Journal entries:")
misc_names = {9: 'KG', 18: 'KFURN', 32: 'Devika', 38: 'KDESIGN'}
for jid in [9, 18, 32, 38]:
    entries = sr('account.move', [['journal_id', '=', jid]], ['name'], limit=100)
    after_count = len(entries)
    before_count = misc_before.get(jid, 0)
    marker = "🆕 NEW!" if after_count > before_count else "No change"
    print(f"  MISC {misc_names.get(jid, jid):8s}: Before={before_count}, After={after_count} — {marker}")

# Check ALL new JEs
if total_moves_after > total_moves_before:
    print(f"\n🆕 NEW JOURNAL ENTRIES ({total_moves_after - total_moves_before} found):")
    # Get the latest entries
    new_entries = sr('account.move', [], 
        ['name', 'journal_id', 'date', 'amount_total', 'company_id', 'ref', 'state', 'move_type'],
        limit=total_moves_after - total_moves_before + 5)
    # Sort by ID descending to get newest
    new_entries.sort(key=lambda x: x['id'], reverse=True)
    for e in new_entries[:total_moves_after - total_moves_before + 3]:
        j = e['journal_id'][1] if e['journal_id'] else 'N/A'
        c = e['company_id'][1] if e['company_id'] else 'N/A'
        print(f"  [{e['id']:5d}] {e['name']:20s} | {j:30s} | {e['date']} | ₹{e['amount_total']:>10,.2f} | {c[:15]} | {e['state']} | {e.get('ref', 'N/A')}")

# Stock moves with JEs
moves_with_je_after = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"\nStock moves linked to JEs: Before={moves_with_je_before}, After={moves_with_je_after}")

# ════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL RESULTS MATRIX")
print("=" * 70)
print(f"{'Category':<28s} | {'Transfer Type':<32s} | {'State':<8s} | {'JE?':<15s}")
print("-" * 90)
for tr in transfer_results:
    pick = sr('stock.picking', [['id', '=', tr['picking_id']]], ['name', 'state'])
    pick_state = pick[0]['state'] if pick else 'N/A'
    pick_name = pick[0]['name'] if pick else 'N/A'
    
    moves = sr('stock.move', [['picking_id', '=', tr['picking_id']]], ['account_move_id'])
    je = any(m['account_move_id'] for m in moves)
    
    print(f"{tr['category']:<28s} | {tr['type']:<32s} | {pick_state:<8s} | {'✅ YES' if je else '❌ NO':<15s}")

print("\n=== TEST COMPLETE ===")
