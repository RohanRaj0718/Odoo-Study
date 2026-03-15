"""Check inventory valuation configuration and internal transfer journal entries."""
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

def fg(model, attrs=None):
    kw = {}
    if attrs:
        kw['attributes'] = attrs
    return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], kw)

# ── 1. Check product categories for valuation method ──
print("=" * 70)
print("1. PRODUCT CATEGORY VALUATION SETTINGS")
print("=" * 70)

cats = sr('product.category', [], 
    ['name', 'property_cost_method', 'property_valuation'], limit=20)
for c in cats:
    method = c.get('property_cost_method', 'N/A')
    valuation = c.get('property_valuation', 'N/A')
    print(f"  [{c['id']:3d}] {c['name']:30s} | Cost Method: {method:12s} | Valuation: {valuation}")

# ── 2. Check accounting settings for inventory valuation method ──
print("\n" + "=" * 70)
print("2. COMPANY ACCOUNTING SETTINGS (Inventory Valuation)")
print("=" * 70)

# Check res.config.settings or ir.config_parameter for inventory valuation
try:
    params = sr('ir.config_parameter', [['key', 'like', 'valuation']], ['key', 'value'], limit=10)
    for p in params:
        print(f"  {p['key']}: {p['value']}")
except:
    print("  Cannot access ir.config_parameter")

# Check on company
companies = sr('res.company', [], ['name', 'currency_id'], limit=10)
for c in companies:
    print(f"  {c['name']} (ID={c['id']})")

# ── 3. Check if there are ANY stock valuation journal entries ──
print("\n" + "=" * 70)
print("3. STOCK-RELATED JOURNAL ENTRIES")  
print("=" * 70)

# Look for stock valuation journals
journals = sr('account.journal', [], ['name', 'type', 'code', 'company_id'], limit=30)
stock_journals = [j for j in journals if 'stock' in j['name'].lower() or 'inventory' in j['name'].lower() or j['type'] == 'general']
print("\nJournals (General/Stock type):")
for j in journals:
    jtype = j['type']
    comp = j['company_id'][1] if j['company_id'] else 'N/A'
    marker = " *** STOCK" if 'stock' in j['name'].lower() or 'inventory' in j['name'].lower() else ""
    print(f"  [{j['id']:3d}] {j['name']:35s} | Type: {jtype:10s} | Code: {j['code']:6s} | {comp}{marker}")

# ── 4. Look for internal transfer stock moves ──
print("\n" + "=" * 70)
print("4. INTERNAL TRANSFER STOCK MOVES")
print("=" * 70)

# stock.picking with picking_type that is internal
try:
    pickings = sr('stock.picking', [['picking_type_code', '=', 'internal']], 
        ['name', 'state', 'company_id', 'location_id', 'location_dest_id', 'date_done'], limit=10)
    if pickings:
        for p in pickings:
            comp = p['company_id'][1] if p['company_id'] else 'N/A'
            src = p['location_id'][1] if p['location_id'] else 'N/A'
            dst = p['location_dest_id'][1] if p['location_dest_id'] else 'N/A'
            print(f"  {p['name']:15s} | {p['state']:10s} | {comp:20s} | {src} → {dst}")
    else:
        print("  No internal transfers found")
except Exception as e:
    print(f"  Error: {e}")

# ── 5. Check stock.move for any account_move_ids (journal entries from stock moves) ──
print("\n" + "=" * 70)
print("5. STOCK MOVES WITH JOURNAL ENTRIES (account_move_ids)")
print("=" * 70)

try:
    # Check if stock.move has account_move_ids field
    move_fields = fg('stock.move', ['string', 'type'])
    acct_fields = {k: v for k, v in move_fields.items() if 'account' in k.lower() or 'journal' in k.lower()}
    print("Stock move fields related to accounting:")
    for fname, fdata in sorted(acct_fields.items()):
        print(f"  {fname:35s} | {fdata['string']:35s} | {fdata['type']}")
    
    # Get recent stock moves and check for linked journal entries
    moves = sr('stock.move', [['state', '=', 'done']], 
        ['reference', 'product_id', 'quantity', 'company_id', 'date', 'picking_id'], 
        limit=10)
    print(f"\nRecent done stock moves: {len(moves)}")
    for m in moves:
        comp = m['company_id'][1] if m['company_id'] else 'N/A'
        prod = m['product_id'][1] if m['product_id'] else 'N/A'
        pick = m['picking_id'][1] if m['picking_id'] else 'N/A'
        print(f"  [{m['id']:5d}] {m['reference']:20s} | {prod[:25]:25s} | Qty: {m['quantity']:>6.1f} | {comp[:15]:15s} | {pick}")
except Exception as e:
    print(f"  Error: {e}")

# ── 6. Check stock.valuation.layer ──
print("\n" + "=" * 70)
print("6. STOCK VALUATION LAYERS")
print("=" * 70)

try:
    layers = sr('stock.valuation.layer', [], 
        ['product_id', 'quantity', 'value', 'unit_cost', 'company_id', 'stock_move_id', 'account_move_id', 'description'],
        limit=15)
    if layers:
        for l in layers:
            comp = l['company_id'][1] if l['company_id'] else 'N/A'
            prod = l['product_id'][1] if l['product_id'] else 'N/A'
            acct = l['account_move_id'][1] if l['account_move_id'] else 'NO JE'
            stk = l['stock_move_id'][1] if l['stock_move_id'] else 'N/A'
            print(f"  Prod: {prod[:25]:25s} | Qty: {l['quantity']:>6.1f} | Value: {l['value']:>10,.2f} | Cost: {l['unit_cost']:>8,.2f} | JE: {acct} | {comp[:15]}")
    else:
        print("  No valuation layers found")
except Exception as e:
    print(f"  Error: {e}")

# ── 7. Check storeroom product type ──
print("\n" + "=" * 70)
print("7. PRODUCT TYPE CHECK (storable vs consumable)")
print("=" * 70)

prods = sr('product.product', [], ['name', 'type', 'categ_id'], limit=10)
for p in prods:
    cat = p['categ_id'][1] if p['categ_id'] else 'N/A'
    print(f"  {p['name'][:35]:35s} | Type: {p['type']:12s} | Category: {cat}")

print("\n=== DONE ===")
