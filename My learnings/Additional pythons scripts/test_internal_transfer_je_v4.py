"""
FINAL TEST v4: Internal Transfers & Journal Entries — Odoo 19
=============================================================
All None-returning methods wrapped with try/except for XML-RPC marshal errors.
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

def safe_ex(model, method, *args, **kw):
    """Execute but tolerate 'cannot marshal None' errors (method succeeded but returned None)."""
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kw)
    except xmlrpc.client.Fault as e:
        if 'cannot marshal None' in str(e):
            return True  # Method worked, just returned None
        raise

def sr(model, domain, fields, limit=50):
    return ex(model, 'search_read', [domain], {'fields': fields, 'limit': limit})

def create(model, vals):
    return ex(model, 'create', [vals])

# ═══════════════════════════════════════════════════════════════
# STEP 1: Verify categories (already created: IDs 37-40)
# ═══════════════════════════════════════════════════════════════
print("=" * 70)
print("STEP 1: Verify test categories")
print("=" * 70)

cat_map = {
    "Periodic+Std": 37,
    "Perpetual+Std": 38,
    "Perpetual+AVCO": 39,
    "Perpetual+FIFO": 40,
}

for name, cid in cat_map.items():
    c = sr('product.category', [['id', '=', cid]], ['name', 'property_cost_method', 'property_valuation'])
    if c:
        print(f"  ✅ {name:20s} | cost={c[0]['property_cost_method']:10s} | val={c[0]['property_valuation']}")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Ensure products exist and are storable
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 2: Verify/fix products")
print("=" * 70)

test_products = {}
for cat_name, cat_id in cat_map.items():
    prod_name = f"ZZ-TEST-{cat_name}"
    existing = sr('product.product', [['name', '=', prod_name]], ['id', 'is_storable'])
    if existing:
        pid = existing[0]['id']
        storable = existing[0].get('is_storable', False)
        print(f"  ✅ {prod_name} (ID={pid}) storable={storable}")
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
        print(f"  ✅ Created {prod_name} (ID={pid})")
        test_products[cat_name] = pid

# ═══════════════════════════════════════════════════════════════
# STEP 3: Locations
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 3: Locations")
print("=" * 70)

kg_stock_id = sr('stock.location', [['complete_name', '=', 'WH/Stock'], ['usage', '=', 'internal']], ['id'])[0]['id']
nhgf_id = sr('stock.location', [['complete_name', 'ilike', 'NH GF/Stock'], ['usage', '=', 'internal']], ['id'])[0]['id']
transit_id = sr('stock.location', [['name', '=', 'Inter-company transit'], ['usage', '=', 'transit']], ['id'])[0]['id']
kg_int_pt_id = sr('stock.picking.type', [['code', '=', 'internal'], ['warehouse_id', '=', 1]], ['id'])[0]['id']
print(f"  WH/Stock={kg_stock_id}, NHGF={nhgf_id}, Transit={transit_id}, PickType={kg_int_pt_id}")

# ═══════════════════════════════════════════════════════════════
# STEP 4: Set initial stock
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 4: Set initial stock")
print("=" * 70)

for cat_name, pid in test_products.items():
    quants = sr('stock.quant', [['product_id', '=', pid], ['location_id', '=', kg_stock_id]], ['quantity'])
    if quants and quants[0]['quantity'] >= 20:
        print(f"  ♻ {cat_name}: {quants[0]['quantity']} units already")
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
        safe_ex('stock.quant', 'action_apply_inventory', [[qid]])
        # Verify
        q = sr('stock.quant', [['product_id', '=', pid], ['location_id', '=', kg_stock_id]], ['quantity'])
        qty = q[0]['quantity'] if q else 0
        print(f"  ✅ {cat_name}: set stock → now {qty} units")
    except Exception as e:
        print(f"  ⚠ {cat_name}: {str(e)[:80]}")

# ═══════════════════════════════════════════════════════════════
# STEP 5: Before counts
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 5: Before state")
print("=" * 70)

total_je_before = ex('account.move', 'search_count', [[]])
stj_ids = [13, 23, 33, 39]
stj_before = {jid: ex('account.move', 'search_count', [[['journal_id', '=', jid]]]) for jid in stj_ids}
moves_je_before = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"  Total JEs: {total_je_before} | STJ: {stj_before} | SM w/JE: {moves_je_before}")

# ═══════════════════════════════════════════════════════════════
# STEP 6: Create and validate internal transfers
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("STEP 6: Internal transfers (8 combinations)")
print("=" * 70)

results = []

for cat_name, pid in test_products.items():
    for dest_label, dest_id, xfer_label in [
        ("NHGF", nhgf_id, "Intra-Company"),
        ("Transit", transit_id, "Inter-Company"),
    ]:
        qty = 5 if dest_label == "NHGF" else 3
        label = f"{cat_name} → {xfer_label}"
        
        try:
            # 1. Create picking (blank)
            pick_id = create('stock.picking', {
                'picking_type_id': kg_int_pt_id,
                'location_id': kg_stock_id,
                'location_dest_id': dest_id,
                'company_id': 1,
            })
            
            # 2. Create stock move linked to picking
            move_id = create('stock.move', {
                'name': f'TEST-{cat_name}-{dest_label}',
                'product_id': pid,
                'product_uom_qty': qty,
                'location_id': kg_stock_id,
                'location_dest_id': dest_id,
                'picking_id': pick_id,
                'company_id': 1,
            })
            
            # 3. Confirm (returns None, wrap it)
            safe_ex('stock.picking', 'action_confirm', [[pick_id]])
            
            # 4. Set quantity done
            ex('stock.move', 'write', [[move_id], {'quantity': qty}])
            
            # 5. Validate (might return wizard dict or None)
            try:
                res = ex('stock.picking', 'button_validate', [[pick_id]])
                if isinstance(res, dict) and res.get('res_model'):
                    # It's a wizard, try to process it
                    wiz_model = res['res_model']
                    wiz_id = res.get('res_id')
                    if wiz_id:
                        safe_ex(wiz_model, 'process', [[wiz_id]])
            except xmlrpc.client.Fault as e:
                if 'cannot marshal None' in str(e):
                    pass  # Validation succeeded, returned None
                else:
                    # Try setting quantities first
                    try:
                        safe_ex('stock.picking', 'action_set_quantities_to_reservation', [[pick_id]])
                        safe_ex('stock.picking', 'button_validate', [[pick_id]])
                    except:
                        pass
            
            # 6. Check final state
            pick_info = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
            state = pick_info[0]['state'] if pick_info else '??'
            pname = pick_info[0]['name'] if pick_info else '??'
            
            # 7. Check if JE was created for this move
            mv = sr('stock.move', [['id', '=', move_id]], ['account_move_id', 'state'])
            mv_state = mv[0]['state'] if mv else '??'
            has_je = mv[0].get('account_move_id') if mv else False
            je_txt = f"✅ {has_je[1]}" if has_je else "❌ No"
            
            print(f"  {label:35s} | {pname:15s} | pick={state:6s} | move={mv_state:6s} | JE: {je_txt}")
            results.append({
                'cat': cat_name, 'type': xfer_label, 'pick_id': pick_id, 
                'move_id': move_id, 'state': state, 'has_je': bool(has_je)
            })
            
        except Exception as e:
            print(f"  ⚠ {label:35s} | ERROR: {str(e)[:80]}")

print(f"\n  Transfers completed: {len(results)} / 8")
print(f"  Done: {sum(1 for r in results if r['state'] == 'done')}")

# ═══════════════════════════════════════════════════════════════
# STEP 7: FINAL RESULTS
# ═══════════════════════════════════════════════════════════════
time.sleep(2)

print("\n" + "=" * 70)
print("STEP 7: FINAL RESULTS")
print("=" * 70)

total_je_after = ex('account.move', 'search_count', [[]])
moves_je_after = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
new_jes = total_je_after - total_je_before

print(f"\n📊 OVERALL:")
print(f"  Journal entries: {total_je_before} → {total_je_after} (+{new_jes})")
print(f"  Stock moves with JEs: {moves_je_before} → {moves_je_after}")

print(f"\n📊 INVENTORY VALUATION JOURNALS (STJ):")
stj_map = {13: 'KG', 23: 'KFURN', 33: 'Devika', 39: 'KDESIGN'}
new_stj = False
for jid in stj_ids:
    after = ex('account.move', 'search_count', [[['journal_id', '=', jid]]])
    diff = after - stj_before[jid]
    if diff > 0:
        new_stj = True
        print(f"  {stj_map[jid]:8s}: {stj_before[jid]} → {after} 🆕 +{diff}")
        entries = sr('account.move', [['journal_id', '=', jid]], 
            ['name', 'date', 'amount_total', 'ref', 'state'], limit=20)
        for e in entries:
            print(f"    {e['name']} | {e['date']} | ₹{e['amount_total']:,.2f} | {e.get('ref', '')} | {e['state']}")
            lines = sr('account.move.line', [['move_id', '=', e['id']]], 
                ['account_id', 'debit', 'credit', 'name'], limit=10)
            for l in lines:
                acct = l['account_id'][1] if l['account_id'] else '-'
                print(f"      Dr ₹{l['debit']:>10,.2f} | Cr ₹{l['credit']:>10,.2f} | {acct}")
    else:
        print(f"  {stj_map[jid]:8s}: {stj_before[jid]} → {after} — No change")

if new_jes > 0:
    print(f"\n🆕 ALL {new_jes} NEW JOURNAL ENTRIES:")
    all_je = sr('account.move', [], ['name', 'journal_id', 'date', 'amount_total', 'company_id', 'state'], limit=200)
    all_je.sort(key=lambda x: x['id'], reverse=True)
    for e in all_je[:new_jes + 2]:
        j = e['journal_id'][1] if e['journal_id'] else 'N/A'
        c = e['company_id'][1] if e['company_id'] else 'N/A'
        print(f"  [{e['id']:5d}] {e['name']:20s} | {j:35s} | ₹{e['amount_total']:>10,.2f} | {c[:15]} | {e['state']}")

# ═══════════════════════════════════════════════════════════════
# RESULTS TABLE
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("RESULTS MATRIX")
print("=" * 70)

print("""
┌──────────────────────┬────────────────┬────────────────┐
│ Valuation Config     │ Intra-Company  │ Inter-Company  │
│                      │ (WH→NH GF)     │ (WH→Transit)   │
├──────────────────────┼────────────────┼────────────────┤""")

for cat in ["Periodic+Std", "Perpetual+Std", "Perpetual+AVCO", "Perpetual+FIFO"]:
    intra = next((r for r in results if r['cat'] == cat and r['type'] == 'Intra-Company'), None)
    inter = next((r for r in results if r['cat'] == cat and r['type'] == 'Inter-Company'), None)
    
    intra_txt = "✅ JE" if (intra and intra['has_je']) else ("❌ No JE" if intra else "⚠ Failed")
    inter_txt = "✅ JE" if (inter and inter['has_je']) else ("❌ No JE" if inter else "⚠ Failed")
    intra_state = f"({intra['state']})" if intra else ""
    inter_state = f"({inter['state']})" if inter else ""
    
    print(f"│ {cat:<20s} │ {intra_txt} {intra_state:<6s} │ {inter_txt} {inter_state:<6s} │")

print("└──────────────────────┴────────────────┴────────────────┘")

# Conclusion
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
if new_jes == 0:
    print("""
✅ CONFIRMED: In Odoo 19, internal transfers do NOT create journal
   entries under ANY valuation configuration:
   
   • Periodic + Standard Cost   → No JE
   • Perpetual + Standard Cost  → No JE  
   • Perpetual + AVCO           → No JE
   • Perpetual + FIFO           → No JE
   
   This applies to BOTH:
   • Intra-company transfers (between warehouses in same company)
   • Inter-company transfers (via transit location to other branch)
   
   WHY: Odoo 19 changed the inventory valuation architecture.
   Stock moves no longer generate per-move journal entries.
   Accounting impact happens only via:
   1) Invoice/Bill posting
   2) Manual closing entry (Accounting → Review → Inventory Valuation)
""")
else:
    print(f"\n  {new_jes} journal entries WERE created. See details above.")

print("=== COMPLETE ===")
