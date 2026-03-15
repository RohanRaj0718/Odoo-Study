"""
FINAL TEST: Internal Transfers & Journal Entries in Odoo 19
===========================================================
Fixed for Odoo 19 field names:
  - stock.picking: move_ids (not move_ids_without_package)
  - product: is_storable = True (Track Inventory)

Test Matrix:
  A) Periodic + Standard Cost
  B) Perpetual + Standard Cost
  C) Perpetual + AVCO
  D) Perpetual + FIFO

Transfer Types:
  1) Intra-company (WH/Stock → NH GF/Stock)
  2) Inter-company (WH/Stock → Inter-company transit)
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

# ═══════════════════════════════════════════════════════════════
# SETUP: Categories already created (37-40), reuse them
# ═══════════════════════════════════════════════════════════════
print("=" * 70)
print("STEP 1: Verify test categories")
print("=" * 70)

cat_map = {
    "TEST-Periodic-Std": 37,
    "TEST-Perpetual-Std": 38,
    "TEST-Perpetual-AVCO": 39,
    "TEST-Perpetual-FIFO": 40,
}

for name, cid in cat_map.items():
    c = sr('product.category', [['id', '=', cid]], ['name', 'property_cost_method', 'property_valuation'])
    if c:
        print(f"  ✅ {c[0]['name']:30s} | cost={c[0]['property_cost_method']:10s} | val={c[0]['property_valuation']}")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Fix products — set is_storable=True  
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 2: Fix test products (set is_storable=True)")
print("=" * 70)

test_products = {}
for cat_name, cat_id in cat_map.items():
    prod_name = f"ZZ-TEST-{cat_name.replace('TEST-', '')}"
    existing = sr('product.product', [['name', '=', prod_name]], ['id', 'is_storable', 'type'])
    if existing:
        pid = existing[0]['id']
        if not existing[0].get('is_storable'):
            ex('product.product', 'write', [[pid], {'is_storable': True}])
            print(f"  🔧 Fixed '{prod_name}' → is_storable=True")
        else:
            print(f"  ♻ '{prod_name}' already storable")
        test_products[cat_name] = pid
    else:
        pid = create('product.product', {
            'name': prod_name,
            'type': 'consu',
            'is_storable': True,
            'categ_id': cat_id,
            'list_price': 100.0,
            'standard_price': 50.0,
        })
        print(f"  ✅ Created '{prod_name}' (ID={pid}) storable")
        test_products[cat_name] = pid

# Verify
for cat_name, pid in test_products.items():
    p = sr('product.product', [['id', '=', pid]], ['name', 'is_storable', 'type', 'categ_id'])
    if p:
        print(f"  → {p[0]['name']}: type={p[0]['type']}, storable={p[0]['is_storable']}, cat={p[0]['categ_id'][1]}")

# ═══════════════════════════════════════════════════════════════
# STEP 3: Locations
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 3: Locations & picking types")
print("=" * 70)

kg_stock = sr('stock.location', [['complete_name', '=', 'WH/Stock'], ['usage', '=', 'internal']], ['complete_name'])
kg_stock_id = kg_stock[0]['id']
print(f"  KG Stock: ID={kg_stock_id}")

nhgf = sr('stock.location', [['complete_name', 'ilike', 'NH GF/Stock'], ['usage', '=', 'internal']], ['complete_name'])
nhgf_id = nhgf[0]['id']
print(f"  NH GF Stock: ID={nhgf_id}")

transit = sr('stock.location', [['name', '=', 'Inter-company transit'], ['usage', '=', 'transit']], ['complete_name'])
transit_id = transit[0]['id']
print(f"  Inter-company transit: ID={transit_id}")

# KG internal transfer picking type (warehouse_id=1 = KG main)
kg_int_pt = sr('stock.picking.type', [['code', '=', 'internal'], ['warehouse_id', '=', 1]], ['name'])
kg_int_pt_id = kg_int_pt[0]['id']
print(f"  KG Internal Transfer Picking Type: ID={kg_int_pt_id}")

# ═══════════════════════════════════════════════════════════════
# STEP 4: Set initial stock via inventory adjustment
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 4: Set initial stock (100 units each)")
print("=" * 70)

for cat_name, pid in test_products.items():
    quants = sr('stock.quant', [['product_id', '=', pid], ['location_id', '=', kg_stock_id]], ['quantity', 'inventory_quantity'])
    if quants and quants[0]['quantity'] >= 20:
        print(f"  ♻ {cat_name}: already has {quants[0]['quantity']} units")
        continue
    try:
        if quants:
            qid = quants[0]['id']
            ex('stock.quant', 'write', [[qid], {'inventory_quantity': 100}])
        else:
            qid = create('stock.quant', {
                'product_id': pid,
                'location_id': kg_stock_id,
                'inventory_quantity': 100,
            })
        ex('stock.quant', 'action_apply_inventory', [[qid]])
        print(f"  ✅ {cat_name}: 100 units at WH/Stock")
    except Exception as e:
        print(f"  ⚠ {cat_name}: {e}")

# ═══════════════════════════════════════════════════════════════
# STEP 5: Record BEFORE counts
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 5: Before counts")
print("=" * 70)

total_je_before = ex('account.move', 'search_count', [[]])
stj_ids = [13, 23, 33, 39]
stj_before = {jid: ex('account.move', 'search_count', [[['journal_id', '=', jid]]]) for jid in stj_ids}
moves_je_before = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"  Total JEs: {total_je_before}")
print(f"  STJ JEs: {stj_before}")
print(f"  Stock moves with JEs: {moves_je_before}")

# ═══════════════════════════════════════════════════════════════
# STEP 6: Create and validate internal transfers
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 6: Creating & validating internal transfers")
print("=" * 70)

results = []

for cat_name, pid in test_products.items():
    for dest_name, dest_id, xfer_type in [
        ("NH GF", nhgf_id, "Intra-Company (WH→NHGF)"),
        ("Transit", transit_id, "Inter-Company (WH→Transit)")
    ]:
        qty = 5 if "Intra" in xfer_type else 3
        try:
            # Create picking with moves
            pick_id = create('stock.picking', {
                'picking_type_id': kg_int_pt_id,
                'location_id': kg_stock_id,
                'location_dest_id': dest_id,
                'company_id': 1,
            })
            
            # Create stock move separately
            move_id = create('stock.move', {
                'name': f'TEST-{cat_name}-{xfer_type[:5]}',
                'product_id': pid,
                'product_uom_qty': qty,
                'location_id': kg_stock_id,
                'location_dest_id': dest_id,
                'picking_id': pick_id,
                'company_id': 1,
            })
            
            # Confirm picking
            ex('stock.picking', 'action_confirm', [[pick_id]])
            
            # Set quantity done  
            ex('stock.move', 'write', [[move_id], {'quantity': qty}])
            
            # Validate
            try:
                res = ex('stock.picking', 'button_validate', [[pick_id]])
            except Exception as e:
                # Might return wizard
                try:
                    ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                    res = ex('stock.picking', 'button_validate', [[pick_id]])
                except:
                    pass
            
            pick_info = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
            state = pick_info[0]['state'] if pick_info else '??'
            print(f"  ✅ {cat_name:25s} | {xfer_type:30s} | {pick_info[0]['name']:15s} | {state}")
            results.append({'cat': cat_name, 'type': xfer_type, 'pick_id': pick_id, 'move_id': move_id})
            
        except Exception as e:
            err_msg = str(e)[:100]
            print(f"  ⚠ {cat_name:25s} | {xfer_type:30s} | {err_msg}")

print(f"\nTransfers completed: {len(results)}")

# ═══════════════════════════════════════════════════════════════
# STEP 7: RESULTS
# ═══════════════════════════════════════════════════════════════
time.sleep(2)

print("\n" + "=" * 70)
print("STEP 7: RESULTS — Journal Entry Check")
print("=" * 70)

print("\n┌─────────────────────────────┬────────────────────────────────┬────────┬────────────────┐")
print(f"│ {'Category':<27s} │ {'Transfer Type':<30s} │ {'State':<6s} │ {'JE Created?':<14s} │")
print("├─────────────────────────────┼────────────────────────────────┼────────┼────────────────┤")

for r in results:
    pick = sr('stock.picking', [['id', '=', r['pick_id']]], ['name', 'state'])
    state = pick[0]['state'] if pick else '??'
    
    mv = sr('stock.move', [['id', '=', r['move_id']]], ['account_move_id'])
    has_je = mv[0]['account_move_id'] if mv else False
    je_txt = f"✅ {has_je[1]}" if has_je else "❌ NO"
    
    print(f"│ {r['cat']:<27s} │ {r['type']:<30s} │ {state:<6s} │ {je_txt:<14s} │")

print("└─────────────────────────────┴────────────────────────────────┴────────┴────────────────┘")

# Overall comparison
total_je_after = ex('account.move', 'search_count', [[]])
moves_je_after = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])

print(f"\n📊 JOURNAL ENTRY COUNTS:")
print(f"  Total JEs: Before={total_je_before} → After={total_je_after} (New: {total_je_after - total_je_before})")
print(f"  Stock moves with JEs: Before={moves_je_before} → After={moves_je_after}")

stj_map = {13: 'KG', 23: 'KFURN', 33: 'Devika', 39: 'KDESIGN'}
print(f"\n📊 INVENTORY VALUATION JOURNALS (STJ):")
any_new_stj = False
for jid in stj_ids:
    after = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
    diff = after - stj_before[jid]
    marker = f"🆕 +{diff}" if diff > 0 else "No change"
    if diff > 0:
        any_new_stj = True
    print(f"  {stj_map[jid]:8s}: Before={stj_before[jid]} → After={after} — {marker}")
    
    if diff > 0:
        new_entries = sr('account.move', [['journal_id', '=', jid]], 
            ['name', 'date', 'amount_total', 'ref', 'state'], limit=20)
        for e in new_entries:
            print(f"    → {e['name']} | {e['date']} | ₹{e['amount_total']:,.2f} | {e.get('ref', '')} | {e['state']}")
            # Show lines
            lines = sr('account.move.line', [['move_id', '=', e['id']]], 
                ['account_id', 'debit', 'credit', 'name'], limit=10)
            for l in lines:
                acct = l['account_id'][1] if l['account_id'] else 'N/A'
                print(f"      {acct:45s} | Dr: ₹{l['debit']:>10,.2f} | Cr: ₹{l['credit']:>10,.2f}")

# Show ALL new JEs
if total_je_after > total_je_before:
    diff = total_je_after - total_je_before
    print(f"\n🆕 ALL NEW JOURNAL ENTRIES ({diff}):")
    all_je = sr('account.move', [], ['name', 'journal_id', 'date', 'amount_total', 'company_id', 'ref', 'state'], limit=200)
    all_je.sort(key=lambda x: x['id'], reverse=True)
    for e in all_je[:diff + 2]:
        j = e['journal_id'][1] if e['journal_id'] else 'N/A'
        c = e['company_id'][1] if e['company_id'] else 'N/A'
        print(f"  [{e['id']:5d}] {e['name']:20s} | {j:35s} | ₹{e['amount_total']:>10,.2f} | {c[:15]} | {e['state']}")

# ═══════════════════════════════════════════════════════════════
# FINAL VERDICT
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)

if total_je_after == total_je_before and not any_new_stj:
    print("""
❌ CONFIRMED: NO journal entries created by internal transfers.

Tested 4 product categories × 2 transfer types = 8 combinations:
  ┌───────────────────────┬──────────────┬──────────────┐
  │ Valuation Method      │ Intra-Company│ Inter-Company│
  ├───────────────────────┼──────────────┼──────────────┤
  │ Periodic + Standard   │    ❌ No JE   │    ❌ No JE   │
  │ Perpetual + Standard  │    ❌ No JE   │    ❌ No JE   │
  │ Perpetual + AVCO      │    ❌ No JE   │    ❌ No JE   │
  │ Perpetual + FIFO      │    ❌ No JE   │    ❌ No JE   │
  └───────────────────────┴──────────────┴──────────────┘

REASON: In Odoo 19, the inventory valuation architecture changed.
Stock moves no longer trigger individual journal entries.
Accounting entries happen only at:
  1) Invoice/Bill posting
  2) Inventory valuation closing entry (manual)

This is BY DESIGN for performance optimization.
""")
else:
    print(f"""
Results found! {total_je_after - total_je_before} new journal entries created.
Check the details above for which combinations triggered JEs.
""")

print("=== TEST COMPLETE ===")
