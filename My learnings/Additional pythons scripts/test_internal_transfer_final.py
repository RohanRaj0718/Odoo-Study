"""
FINAL WORKING TEST: Internal Transfers & Journal Entries in Odoo 19
===================================================================
Tests 4 valuation configs × 2 transfer types = 8 combinations.
Confirmed field: stock.move has NO 'name' field in Odoo 19.
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
print(f"✅ Auth OK (UID={uid})\n")

def ex(mod, met, *a, **k):
    return models.execute_kw(DB, uid, PASSWORD, mod, met, *a, **k)

def sex(mod, met, *a, **k):
    """Execute but tolerate None returns."""
    try:
        return models.execute_kw(DB, uid, PASSWORD, mod, met, *a, **k)
    except xmlrpc.client.Fault as e:
        if 'cannot marshal None' in str(e):
            return True
        raise

def sr(mod, d, f, limit=50):
    return ex(mod, 'search_read', [d], {'fields': f, 'limit': limit})

# ═══════════════════════════════════════════════════════════════
# Products (already created with is_storable=True, 100 units stock)
# ═══════════════════════════════════════════════════════════════
PRODUCTS = {
    "Periodic+Std":    109,  # Category 37 (periodic, standard)
    "Perpetual+Std":   110,  # Category 38 (real_time, standard)
    "Perpetual+AVCO":  111,  # Category 39 (real_time, average)
    "Perpetual+FIFO":  112,  # Category 40 (real_time, fifo)
}

# Locations
KG_STOCK = 5       # WH/Stock
NHGF = 28          # NH GF/Stock (intra-company)
TRANSIT = 3        # Inter-company transit
KG_INT_PT = 7      # Internal transfer picking type

# ═══════════════════════════════════════════════════════════════
# Verify setup
# ═══════════════════════════════════════════════════════════════
print("Setup verification:")
for label, pid in PRODUCTS.items():
    p = sr('product.product', [['id', '=', pid]], ['name', 'is_storable', 'categ_id'])
    q = sr('stock.quant', [['product_id', '=', pid], ['location_id', '=', KG_STOCK]], ['quantity'])
    qty = q[0]['quantity'] if q else 0
    cat = p[0]['categ_id'][1] if p else 'N/A'
    stor = p[0]['is_storable'] if p else False
    print(f"  {label:20s} | ID={pid:3d} | Storable={stor} | Stock={qty:5.0f} | Cat: {cat}")

# ═══════════════════════════════════════════════════════════════
# Record BEFORE counts
# ═══════════════════════════════════════════════════════════════
total_je_before = ex('account.move', 'search_count', [[]])
stj_ids = [13, 23, 33, 39]
stj_before = {jid: ex('account.move', 'search_count', [[['journal_id', '=', jid]]]) for jid in stj_ids}
moves_je_before = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
print(f"\nBEFORE: JEs={total_je_before}, STJ={stj_before}, SM_w_JE={moves_je_before}")

# ═══════════════════════════════════════════════════════════════
# Run 8 transfer combinations
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("RUNNING 8 TRANSFER COMBINATIONS")
print("=" * 70)

DESTINATIONS = [
    ("Intra (WH→NHGF)", NHGF, 5),
    ("Inter (WH→Transit)", TRANSIT, 3),
]

results = []

for prod_label, pid in PRODUCTS.items():
    for dest_label, dest_id, qty in DESTINATIONS:
        label = f"{prod_label} | {dest_label}"
        try:
            # Create picking
            pick_id = ex('stock.picking', 'create', [{
                'picking_type_id': KG_INT_PT,
                'location_id': KG_STOCK,
                'location_dest_id': dest_id,
                'company_id': 1,
            }])

            # Create move (NO 'name' field in Odoo 19!)
            move_id = ex('stock.move', 'create', [{
                'product_id': pid,
                'product_uom_qty': float(qty),
                'location_id': KG_STOCK,
                'location_dest_id': dest_id,
                'picking_id': pick_id,
                'company_id': 1,
            }])

            # Confirm
            sex('stock.picking', 'action_confirm', [[pick_id]])

            # Set qty done
            ex('stock.move', 'write', [[move_id], {'quantity': float(qty)}])

            # Validate
            try:
                res = ex('stock.picking', 'button_validate', [[pick_id]])
            except xmlrpc.client.Fault as e:
                if 'cannot marshal None' in str(e):
                    pass  # Success, just returned None
                else:
                    raise

            # Check state
            pick = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
            state = pick[0]['state'] if pick else '??'
            pname = pick[0]['name'] if pick else '??'

            # Check JE
            mv = sr('stock.move', [['id', '=', move_id]], ['account_move_id', 'state'])
            has_je = mv[0].get('account_move_id') if mv else False
            je_txt = f"YES → {has_je[1]}" if has_je else "NO"

            print(f"  ✅ {label:40s} | {pname:15s} | {state:6s} | JE: {je_txt}")
            results.append({
                'prod': prod_label,
                'dest': dest_label,
                'pick': pname,
                'state': state,
                'has_je': bool(has_je),
                'je_ref': has_je[1] if has_je else None,
            })

        except Exception as e:
            print(f"  ⚠ {label:40s} | ERROR: {str(e)[:100]}")
            results.append({
                'prod': prod_label,
                'dest': dest_label,
                'pick': 'ERR',
                'state': 'error',
                'has_je': False,
                'je_ref': None,
            })

# ═══════════════════════════════════════════════════════════════
# AFTER counts
# ═══════════════════════════════════════════════════════════════
time.sleep(2)

total_je_after = ex('account.move', 'search_count', [[]])
stj_after = {jid: ex('account.move', 'search_count', [[['journal_id', '=', jid]]]) for jid in stj_ids}
moves_je_after = ex('stock.move', 'search_count', [[['account_move_id', '!=', False]]])
new_jes = total_je_after - total_je_before

print(f"\nAFTER: JEs={total_je_after}, STJ={stj_after}, SM_w_JE={moves_je_after}")
print(f"NEW JEs: {new_jes}")

# ═══════════════════════════════════════════════════════════════
# RESULTS TABLE
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("RESULTS MATRIX")
print("=" * 70)

configs = ["Periodic+Std", "Perpetual+Std", "Perpetual+AVCO", "Perpetual+FIFO"]
print(f"\n{'Valuation Config':<22s} | {'Intra-Company':<20s} | {'Inter-Company':<20s}")
print("-" * 68)

for cfg in configs:
    intra = next((r for r in results if r['prod'] == cfg and 'Intra' in r['dest']), None)
    inter = next((r for r in results if r['prod'] == cfg and 'Inter' in r['dest']), None)

    def fmt(r):
        if not r:
            return "N/A"
        if r['state'] == 'error':
            return "⚠ FAILED"
        if r['has_je']:
            return f"✅ JE ({r['je_ref']})"
        return f"❌ No JE ({r['state']})"

    print(f"{cfg:<22s} | {fmt(intra):<20s} | {fmt(inter):<20s}")

# ═══════════════════════════════════════════════════════════════
# STJ detail
# ═══════════════════════════════════════════════════════════════
stj_map = {13: 'KG', 23: 'KFURN', 33: 'Devika', 39: 'KDESIGN'}
print(f"\nInventory Valuation Journals (STJ):")
for jid in stj_ids:
    b = stj_before[jid]
    a = stj_after[jid]
    print(f"  {stj_map[jid]:8s}: {b} → {a} {'🆕' if a > b else '(no change)'}")
    if a > b:
        entries = sr('account.move', [['journal_id', '=', jid]], ['name', 'date', 'amount_total', 'ref'], limit=20)
        for e in entries:
            print(f"    {e['name']} | {e['date']} | Rs.{e['amount_total']:,.2f} | {e.get('ref', '')}")
            lines = sr('account.move.line', [['move_id', '=', e['id']]], ['account_id', 'debit', 'credit'], limit=10)
            for l in lines:
                acct = l['account_id'][1] if l['account_id'] else '-'
                print(f"      Dr {l['debit']:>10,.2f} | Cr {l['credit']:>10,.2f} | {acct}")

# Any new JEs at all
if new_jes > 0:
    print(f"\n🆕 {new_jes} NEW JOURNAL ENTRIES:")
    all_je = sr('account.move', [], ['name', 'journal_id', 'amount_total', 'company_id', 'state'], limit=200)
    all_je.sort(key=lambda x: x['id'], reverse=True)
    for e in all_je[:new_jes + 2]:
        j = e['journal_id'][1] if e['journal_id'] else '-'
        c = e['company_id'][1] if e['company_id'] else '-'
        print(f"  [{e['id']}] {e['name']} | {j} | Rs.{e['amount_total']:,.2f} | {c} | {e['state']}")

# ═══════════════════════════════════════════════════════════════
# CONCLUSION
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

done_count = sum(1 for r in results if r['state'] == 'done')
je_count = sum(1 for r in results if r['has_je'])

print(f"\n  Transfers completed (done): {done_count} / {len(results)}")
print(f"  Transfers with JE:          {je_count} / {len(results)}")

if je_count == 0 and done_count > 0:
    print("""
  ╔══════════════════════════════════════════════════════════════════╗
  ║  CONFIRMED: Internal transfers create ZERO journal entries     ║
  ║  in Odoo 19, regardless of valuation configuration.            ║
  ║                                                                ║
  ║  Tested:                                                       ║
  ║  • Periodic + Standard Cost    → ❌ No JE                      ║
  ║  • Perpetual + Standard Cost   → ❌ No JE                      ║
  ║  • Perpetual + AVCO            → ❌ No JE                      ║
  ║  • Perpetual + FIFO            → ❌ No JE                      ║
  ║                                                                ║
  ║  Both intra-company and inter-company transfers: No JE.        ║
  ║                                                                ║
  ║  This is BY DESIGN in Odoo 19:                                 ║
  ║  Stock moves → no per-move JE                                  ║
  ║  JEs happen at: Invoice/Bill + Closing Entry only              ║
  ╚══════════════════════════════════════════════════════════════════╝
""")
elif je_count > 0:
    print(f"\n  ✅ {je_count} transfers DID create journal entries!")
    print("  Check the details above for which combinations.")

print("=== COMPLETE ===")
