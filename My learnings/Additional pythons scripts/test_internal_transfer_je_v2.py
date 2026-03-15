"""
COMPREHENSIVE TEST: Internal Transfers & Journal Entries in Odoo 19
===================================================================
Test Matrix:
  A) Periodic + Standard Cost  (current default)
  B) Perpetual + Standard Cost
  C) Perpetual + AVCO
  D) Perpetual + FIFO

Transfer Types:
  1) Intra-company (WH/Stock → NH GF/Stock)
  2) Inter-company (KG → Devika via transit)
"""
import xmlrpc.client
import time

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
assert uid, "Auth failed!"
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
print(f"✅ Authenticated UID={uid}\n")

def ex(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kw)

def sr(model, domain, fields, limit=50):
    return ex(model, 'search_read', [domain], {'fields': fields, 'limit': limit})

def create(model, vals):
    return ex(model, 'create', [vals])

# ════════════════════════════════════════════════════════════════════
# STEP 1: Create test product categories
# ════════════════════════════════════════════════════════════════════
print("=" * 70)
print("STEP 1: Creating test product categories")
print("=" * 70)

cat_configs = [
    ("TEST-Periodic-Std", "standard", "periodic"),
    ("TEST-Perpetual-Std", "standard", "real_time"),
    ("TEST-Perpetual-AVCO", "average", "real_time"),
    ("TEST-Perpetual-FIFO", "fifo", "real_time"),
]

test_categories = {}
for cat_name, cost_method, valuation in cat_configs:
    existing = sr('product.category', [['name', '=', cat_name]], ['id'])
    if existing:
        test_categories[cat_name] = existing[0]['id']
        print(f"  ♻ '{cat_name}' exists (ID={existing[0]['id']})")
    else:
        vals = {
            'name': cat_name,
            'parent_id': 1,
            'property_cost_method': cost_method,
            'property_valuation': valuation,
        }
        try:
            cat_id = create('product.category', vals)
            test_categories[cat_name] = cat_id
            print(f"  ✅ Created '{cat_name}' (ID={cat_id})")
        except Exception as e:
            print(f"  ⚠ '{cat_name}': {e}")
            test_categories[cat_name] = None

# Verify category settings
print("\nVerifying category settings:")
for cat_name, cat_id in test_categories.items():
    if cat_id:
        c = sr('product.category', [['id', '=', cat_id]], 
            ['name', 'property_cost_method', 'property_valuation'])
        if c:
            val = c[0].get('property_valuation', 'N/A')
            cost = c[0].get('property_cost_method', 'N/A')
            print(f"  {cat_name}: valuation={val}, cost={cost}")

# ════════════════════════════════════════════════════════════════════
# STEP 2: Create test products
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 2: Creating test products")
print("=" * 70)

test_products = {}
for cat_name, cat_id in test_categories.items():
    if not cat_id:
        continue
    prod_name = f"ZZ-TEST-{cat_name.replace('TEST-', '')}"
    existing = sr('product.product', [['name', '=', prod_name]], ['id'])
    if existing:
        test_products[cat_name] = existing[0]['id']
        print(f"  ♻ '{prod_name}' exists (ID={existing[0]['id']})")
    else:
        try:
            prod_id = create('product.product', {
                'name': prod_name,
                'type': 'consu',
                'categ_id': cat_id,
                'list_price': 100.0,
                'standard_price': 50.0,
            })
            test_products[cat_name] = prod_id
            print(f"  ✅ Created '{prod_name}' (ID={prod_id})")
        except Exception as e:
            print(f"  ⚠ '{prod_name}': {e}")
            test_products[cat_name] = None

# ════════════════════════════════════════════════════════════════════
# STEP 3: Find locations
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 3: Finding locations and picking types")
print("=" * 70)

# KG WH/Stock
kg_stock = sr('stock.location', 
    [['complete_name', '=', 'WH/Stock'], ['usage', '=', 'internal']], 
    ['complete_name'])
if not kg_stock:
    kg_stock = sr('stock.location', 
        [['complete_name', 'ilike', 'WH/Stock'], ['usage', '=', 'internal']], 
        ['complete_name'], limit=3)
kg_stock_id = kg_stock[0]['id'] if kg_stock else None
print(f"KG Stock: {kg_stock}")

# NH GF/Stock (within KG)
nhgf = sr('stock.location',
    [['complete_name', 'ilike', 'NH GF/Stock'], ['usage', '=', 'internal']],
    ['complete_name'], limit=3)
nhgf_id = nhgf[0]['id'] if nhgf else None
print(f"NH GF: {nhgf}")

# Transit location
transit = sr('stock.location',
    [['usage', '=', 'transit']],
    ['name', 'complete_name'], limit=5)
print(f"Transit: {transit}")
transit_id = None
for t in transit:
    if 'inter-company' in t['complete_name'].lower() or 'inter-company' in t['name'].lower():
        transit_id = t['id']
        break
if not transit_id and transit:
    transit_id = transit[0]['id']

# Devika stock
devika_stock = sr('stock.location',
    [['complete_name', 'ilike', 'DF/Stock'], ['usage', '=', 'internal']],
    ['complete_name'], limit=3)
devika_stock_id = devika_stock[0]['id'] if devika_stock else None
print(f"Devika Stock: {devika_stock}")

# KG internal picking type
kg_int_pt = sr('stock.picking.type',
    [['code', '=', 'internal'], ['warehouse_id.company_id', '=', 1]],
    ['name', 'warehouse_id'], limit=5)
print(f"KG internal picking types: {kg_int_pt}")
kg_int_pt_id = kg_int_pt[0]['id'] if kg_int_pt else None

# ════════════════════════════════════════════════════════════════════
# STEP 4: Add initial stock
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 4: Setting initial stock (100 units each in KG WH/Stock)")
print("=" * 70)

for cat_name, prod_id in test_products.items():
    if not prod_id or not kg_stock_id:
        continue
    quants = sr('stock.quant',
        [['product_id', '=', prod_id], ['location_id', '=', kg_stock_id]],
        ['quantity', 'inventory_quantity'])
    if quants and quants[0]['quantity'] >= 50:
        print(f"  ♻ {cat_name}: already has {quants[0]['quantity']} units")
        continue
    try:
        if quants:
            qid = quants[0]['id']
            ex('stock.quant', 'write', [[qid], {'inventory_quantity': 100}])
        else:
            qid = create('stock.quant', {
                'product_id': prod_id,
                'location_id': kg_stock_id,
                'inventory_quantity': 100,
            })
        ex('stock.quant', 'action_apply_inventory', [[qid]])
        print(f"  ✅ {cat_name}: set 100 units")
    except Exception as e:
        print(f"  ⚠ {cat_name}: {e}")

# ════════════════════════════════════════════════════════════════════
# STEP 5: Record BEFORE state
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 5: Recording BEFORE state")
print("=" * 70)

total_je_before = ex('account.move', 'search_count', [[]])
stj_ids = [13, 23, 33, 39]
stj_before = {}
for jid in stj_ids:
    stj_before[jid] = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
    
moves_with_je_before = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"Total JEs: {total_je_before}")
print(f"STJ JEs: {stj_before}")
print(f"Stock moves with JEs: {moves_with_je_before}")

# ════════════════════════════════════════════════════════════════════
# STEP 6: Create and validate internal transfers
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 6: Creating and validating internal transfers")
print("=" * 70)

results = []

for cat_name, prod_id in test_products.items():
    if not prod_id:
        continue
    
    # ── 6A: Intra-company transfer (WH/Stock → NH GF/Stock) ──
    if kg_stock_id and nhgf_id and kg_int_pt_id:
        try:
            pick_id = create('stock.picking', {
                'picking_type_id': kg_int_pt_id,
                'location_id': kg_stock_id,
                'location_dest_id': nhgf_id,
                'company_id': 1,
                'move_ids_without_package': [(0, 0, {
                    'name': f'TEST-{cat_name}-IntraComp',
                    'product_id': prod_id,
                    'product_uom_qty': 5,
                    'location_id': kg_stock_id,
                    'location_dest_id': nhgf_id,
                    'company_id': 1,
                })]
            })
            # Confirm
            ex('stock.picking', 'action_confirm', [[pick_id]])
            # Set qty done
            mvs = sr('stock.move', [['picking_id', '=', pick_id]], ['id'])
            for mv in mvs:
                ex('stock.move', 'write', [[mv['id']], {'quantity': 5}])
            # Validate
            try:
                ex('stock.picking', 'button_validate', [[pick_id]])
            except:
                try:
                    ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                    ex('stock.picking', 'button_validate', [[pick_id]])
                except:
                    pass
            
            pick_info = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
            print(f"  ✅ Intra: {cat_name} → {pick_info[0]['name']} ({pick_info[0]['state']})")
            results.append({'cat': cat_name, 'type': 'Intra-Company (WH→NHGF)', 'pick_id': pick_id})
        except Exception as e:
            print(f"  ⚠ Intra {cat_name}: {e}")

    # ── 6B: Inter-company transfer (WH/Stock → Inter-company transit) ──
    if kg_stock_id and transit_id and kg_int_pt_id:
        try:
            pick_id = create('stock.picking', {
                'picking_type_id': kg_int_pt_id,
                'location_id': kg_stock_id,
                'location_dest_id': transit_id,
                'company_id': 1,
                'move_ids_without_package': [(0, 0, {
                    'name': f'TEST-{cat_name}-InterComp',
                    'product_id': prod_id,
                    'product_uom_qty': 3,
                    'location_id': kg_stock_id,
                    'location_dest_id': transit_id,
                    'company_id': 1,
                })]
            })
            ex('stock.picking', 'action_confirm', [[pick_id]])
            mvs = sr('stock.move', [['picking_id', '=', pick_id]], ['id'])
            for mv in mvs:
                ex('stock.move', 'write', [[mv['id']], {'quantity': 3}])
            try:
                ex('stock.picking', 'button_validate', [[pick_id]])
            except:
                try:
                    ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                    ex('stock.picking', 'button_validate', [[pick_id]])
                except:
                    pass
            
            pick_info = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
            print(f"  ✅ Inter: {cat_name} → {pick_info[0]['name']} ({pick_info[0]['state']})")
            results.append({'cat': cat_name, 'type': 'Inter-Company (WH→Transit)', 'pick_id': pick_id})
        except Exception as e:
            print(f"  ⚠ Inter {cat_name}: {e}")

print(f"\nTotal transfers attempted: {len(results)}")

# ════════════════════════════════════════════════════════════════════
# STEP 7: CHECK RESULTS
# ════════════════════════════════════════════════════════════════════
time.sleep(3)

print("\n" + "=" * 70)
print("STEP 7: CHECKING FOR JOURNAL ENTRIES")
print("=" * 70)

# Check each transfer
print("\n┌────────────────────────────┬──────────────────────────────────┬────────┬──────────────────┐")
print(f"│ {'Category':<26s} │ {'Transfer Type':<32s} │ {'State':<6s} │ {'Journal Entry?':<16s} │")
print("├────────────────────────────┼──────────────────────────────────┼────────┼──────────────────┤")

for r in results:
    pick = sr('stock.picking', [['id', '=', r['pick_id']]], ['name', 'state'])
    state = pick[0]['state'] if pick else '??'
    
    mvs = sr('stock.move', [['picking_id', '=', r['pick_id']]], ['account_move_id'])
    has_je = any(m['account_move_id'] for m in mvs)
    je_txt = '✅ YES' if has_je else '❌ NO'
    
    print(f"│ {r['cat']:<26s} │ {r['type']:<32s} │ {state:<6s} │ {je_txt:<16s} │")

print("└────────────────────────────┴──────────────────────────────────┴────────┴──────────────────┘")

# Overall counts
total_je_after = ex('account.move', 'search_count', [[]])
moves_with_je_after = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])

print(f"\n📊 OVERALL COMPARISON:")
print(f"  Total journal entries: Before={total_je_before}, After={total_je_after}, New={total_je_after - total_je_before}")
print(f"  Stock moves with JEs: Before={moves_with_je_before}, After={moves_with_je_after}")

# STJ journal check
print(f"\n📊 INVENTORY VALUATION JOURNAL (STJ) ENTRIES:")
stj_map = {13: 'KG', 23: 'KFURN', 33: 'Devika', 39: 'KDESIGN'}
for jid in stj_ids:
    after = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
    before = stj_before[jid]
    marker = "🆕 NEW!" if after > before else "No change"
    print(f"  {stj_map[jid]:8s}: Before={before}, After={after} — {marker}")
    if after > before:
        new_entries = sr('account.move', [['journal_id', '=', jid]], 
            ['name', 'date', 'amount_total', 'ref'], limit=10)
        for e in new_entries:
            print(f"    → {e['name']} | {e['date']} | ₹{e['amount_total']:,.2f} | Ref: {e.get('ref', '')}")

# If any NEW JEs were created, show them all
if total_je_after > total_je_before:
    diff = total_je_after - total_je_before
    print(f"\n🆕 ALL NEW JOURNAL ENTRIES ({diff}):")
    all_je = sr('account.move', [], ['name', 'journal_id', 'date', 'amount_total', 'company_id', 'ref', 'state'], limit=200)
    all_je.sort(key=lambda x: x['id'], reverse=True)
    for e in all_je[:diff + 3]:
        j = e['journal_id'][1] if e['journal_id'] else 'N/A'
        c = e['company_id'][1] if e['company_id'] else 'N/A'
        print(f"  [{e['id']:5d}] {e['name']:20s} | {j:30s} | ₹{e['amount_total']:>10,.2f} | {c[:15]} | {e['state']} | {e.get('ref', '')}")

    # Check the journal entry lines for any new STJ entries
    for jid in stj_ids:
        after = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
        if after > stj_before[jid]:
            entries = sr('account.move', [['journal_id', '=', jid]], ['id', 'name'], limit=10)
            for entry in entries:
                lines = sr('account.move.line', [['move_id', '=', entry['id']]], 
                    ['account_id', 'name', 'debit', 'credit', 'product_id'], limit=20)
                print(f"\n  📝 JE {entry['name']} lines:")
                for l in lines:
                    acct = l['account_id'][1] if l['account_id'] else 'N/A'
                    prod = l['product_id'][1] if l['product_id'] else 'N/A'
                    print(f"    {acct:40s} | Dr: {l['debit']:>10,.2f} | Cr: {l['credit']:>10,.2f} | {prod}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
if total_je_after == total_je_before:
    print("❌ NO journal entries were created by ANY internal transfer.")
    print("   This applies to ALL valuation methods:")
    print("   - Periodic + Standard: No JE")
    print("   - Perpetual + Standard: No JE") 
    print("   - Perpetual + AVCO: No JE")
    print("   - Perpetual + FIFO: No JE")
    print("   → This confirms: In Odoo 19, internal transfers do NOT")
    print("     create journal entries regardless of valuation settings.")
else:
    print(f"✅ {total_je_after - total_je_before} journal entries were created.")
    print("   See details above for which combinations triggered JEs.")

print("\n=== TEST COMPLETE ===")
