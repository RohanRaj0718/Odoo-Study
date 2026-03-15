"""Check internal transfer JEs and inventory valuation journal entries."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=20):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# ── 1. Check internal transfer stock moves for linked journal entries ──
print("=" * 70)
print("1. INTERNAL TRANSFER STOCK MOVES — DO THEY HAVE JOURNAL ENTRIES?")
print("=" * 70)

# Get internal transfer moves (done)
int_pickings = sr('stock.picking', [['picking_type_code', '=', 'internal'], ['state', '=', 'done']], 
    ['name', 'company_id', 'location_id', 'location_dest_id'])

for p in int_pickings:
    # Get stock.move lines for this picking
    moves = sr('stock.move', [['picking_id', '=', p['id']], ['state', '=', 'done']], 
        ['reference', 'product_id', 'quantity', 'account_move_id'])
    for m in moves:
        je = m['account_move_id'][1] if m['account_move_id'] else "❌ NO JOURNAL ENTRY"
        prod = m['product_id'][1] if m['product_id'] else 'N/A'
        comp = p['company_id'][1] if p['company_id'] else 'N/A'
        src = p['location_id'][1] if p['location_id'] else 'N/A'
        dst = p['location_dest_id'][1] if p['location_dest_id'] else 'N/A'
        print(f"  {p['name']:15s} | {prod[:25]:25s} | {src[:20]} → {dst[:20]} | JE: {je}")

# ── 2. Check what's in inventory valuation journals (STJ) ──
print("\n" + "=" * 70)
print("2. ENTRIES IN INVENTORY VALUATION JOURNALS (STJ)")
print("=" * 70)

stj_journal_ids = [13, 23, 33, 39]  # STJ journals for all companies
for jid in stj_journal_ids:
    entries = sr('account.move', [['journal_id', '=', jid]], 
        ['name', 'date', 'state', 'amount_total', 'company_id', 'ref'], limit=10)
    journal_info = sr('account.journal', [['id', '=', jid]], ['name', 'company_id'])
    jname = journal_info[0]['name'] if journal_info else 'Unknown'
    comp = journal_info[0]['company_id'][1] if journal_info and journal_info[0]['company_id'] else 'Unknown'
    
    if entries:
        print(f"\n  Journal: {jname} ({comp}) — {len(entries)} entries:")
        for e in entries:
            print(f"    {e['name']:20s} | {e['date']} | State: {e['state']:10s} | Amount: {e['amount_total']:>10,.2f} | Ref: {e.get('ref', 'N/A')}")
    else:
        print(f"\n  Journal: {jname} ({comp}) — ❌ NO ENTRIES")

# ── 3. Check ALL stock moves with account_move_id set (ANY stock move that created a JE) ──
print("\n" + "=" * 70)
print("3. ANY STOCK MOVE WITH A LINKED JOURNAL ENTRY")
print("=" * 70)

moves_with_je = sr('stock.move', [['account_move_id', '!=', False]], 
    ['reference', 'product_id', 'quantity', 'account_move_id', 'company_id', 'picking_id'], limit=20)
if moves_with_je:
    for m in moves_with_je:
        je = m['account_move_id'][1] if m['account_move_id'] else 'N/A'
        prod = m['product_id'][1] if m['product_id'] else 'N/A'
        comp = m['company_id'][1] if m['company_id'] else 'N/A'
        print(f"  {m['reference']:20s} | {prod[:25]:25s} | JE: {je} | {comp}")
else:
    print("  ❌ NO STOCK MOVES have linked journal entries — confirming periodic valuation behavior")

# ── 4. Verify the product type meaning in Odoo 19 ──
print("\n" + "=" * 70)
print("4. PRODUCT TYPE FIELD OPTIONS (Odoo 19)")
print("=" * 70)

try:
    prod_fields = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'fields_get', ['type'], {'attributes': ['string', 'selection', 'help']})
    type_field = prod_fields.get('type', {})
    print(f"  Field: {type_field.get('string', 'N/A')}")
    print(f"  Help: {type_field.get('help', 'N/A')}")
    selections = type_field.get('selection', [])
    for sel in selections:
        print(f"    '{sel[0]}' = {sel[1]}")
except Exception as e:
    print(f"  Error: {e}")

# ── 5. Check property_valuation field options ──
print("\n" + "=" * 70)
print("5. VALUATION FIELD OPTIONS ON product.category")
print("=" * 70)

try:
    cat_fields = models.execute_kw(DB, uid, PASSWORD, 'product.category', 'fields_get', ['property_valuation'], 
        {'attributes': ['string', 'selection', 'help']})
    val_field = cat_fields.get('property_valuation', {})
    print(f"  Field: {val_field.get('string', 'N/A')}")
    print(f"  Help: {val_field.get('help', 'N/A')}")
    for sel in val_field.get('selection', []):
        print(f"    '{sel[0]}' = {sel[1]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== DONE ===")
