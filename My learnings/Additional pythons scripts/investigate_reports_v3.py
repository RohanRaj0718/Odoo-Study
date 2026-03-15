"""
DEEP DIVE Part 3: Create test transactions & verify analytic reporting (Odoo 19 fixes)
"""
import xmlrpc.client, sys, json
from collections import defaultdict

URL = 'https://client-cient.odoo.com'; DB = 'client-cient'
U = 'rohan.raj@infintor.com'; P = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, U, P, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def sr(model, domain, fields, limit=0, order=''):
    kw = {'fields': fields}
    if limit: kw['limit'] = limit
    if order: kw['order'] = order
    return models.execute_kw(DB, uid, P, model, 'search_read', [domain], kw)

def create(model, vals):
    return models.execute_kw(DB, uid, P, model, 'create', [vals])

def execute(model, method, args=[], kwargs={}):
    return models.execute_kw(DB, uid, P, model, method, args, kwargs)

def fields_get(model):
    return models.execute_kw(DB, uid, P, model, 'fields_get', [], {'attributes': ['string','type']})

def count(model, domain):
    return models.execute_kw(DB, uid, P, model, 'search_count', [domain])

print("=" * 80)
print("  PART 3: CREATE TEST DATA & VERIFY REPORTING")
print("=" * 80)

# Get analytic accounts
analytics = sr('account.analytic.account', [], ['name', 'plan_id'])
analytic_map = {a['name']: a['id'] for a in analytics}
print(f"\nAnalytic Accounts: {analytic_map}")

# Get key data (without company_id filter on account.account)
income_accts = sr('account.account', [['account_type', '=', 'income']], ['name', 'code'], limit=5)
print(f"Income Accounts: {[(a['code'], a['name']) for a in income_accts]}")

expense_accts = sr('account.account', [['account_type', '=', 'expense']], ['name', 'code'], limit=5)
print(f"Expense Accounts: {[(a['code'], a['name']) for a in expense_accts]}")

customers = sr('res.partner', [['customer_rank', '>', 0]], ['name'], limit=5)
print(f"Customers: {[(c['name'], c['id']) for c in customers]}")

vendors = sr('res.partner', [['supplier_rank', '>', 0]], ['name'], limit=5)
print(f"Vendors: {[(v['name'], v['id']) for v in vendors]}")

products = sr('product.product', [], ['name'], limit=5)
print(f"Products: {[(p['name'], p['id']) for p in products]}")

journals_sale = sr('account.journal', [['type', '=', 'sale']], ['name', 'company_id'], limit=5)
print(f"Sale Journals: {[(j['name'], j['company_id'][1] if j['company_id'] else 'N/A') for j in journals_sale]}")

journals_purch = sr('account.journal', [['type', '=', 'purchase']], ['name', 'company_id'], limit=5)
print(f"Purchase Journals: {[(j['name'], j['company_id'][1] if j['company_id'] else 'N/A') for j in journals_purch]}")

# ── CREATE INVOICES FOR EACH BRANCH ──
print("\n" + "═" * 80)
print("  CREATING TEST INVOICES PER BRANCH (with analytic distribution)")
print("═" * 80)

krishnadas_id = 1  # Krishnadas Group
branch_data = [
    ('Krishnadas group', analytic_map.get('Krishnadas group'), 5000),
    ('Devika Furniture', analytic_map.get('Devika Furniture'), 7500),
    ('KDesign Interior', analytic_map.get('KDesign Interior'), 3000),
]

# Get sale journal for Krishnadas Group
sale_j = [j for j in journals_sale if j['company_id'] and j['company_id'][0] == krishnadas_id]
purch_j = [j for j in journals_purch if j['company_id'] and j['company_id'][0] == krishnadas_id]

if sale_j and customers and products:
    for branch_name, analytic_id, amount in branch_data:
        if not analytic_id:
            print(f"  ⚠️ No analytic for {branch_name}")
            continue
        
        print(f"\n  📄 Creating invoice for {branch_name} (analytic ID: {analytic_id})...")
        try:
            inv_id = create('account.move', {
                'move_type': 'out_invoice',
                'partner_id': customers[0]['id'],
                'journal_id': sale_j[0]['id'],
                'invoice_date': '2026-02-20',
                'invoice_line_ids': [(0, 0, {
                    'name': f'Branch Sale - {branch_name}',
                    'quantity': 1,
                    'price_unit': amount,
                    'analytic_distribution': {str(analytic_id): 100},
                })]
            })
            print(f"     ✅ Created: ID {inv_id}")
            
            try:
                execute('account.move', 'action_post', [[inv_id]])
                print(f"     ✅ Posted!")
            except Exception as e:
                print(f"     ⚠️ Post error: {str(e)[:100]}")
        except Exception as e:
            print(f"     ❌ Error: {str(e)[:150]}")

    # Also create bills
    if purch_j and vendors:
        for branch_name, analytic_id, amount in branch_data:
            if not analytic_id:
                continue
            print(f"\n  📄 Creating bill for {branch_name}...")
            try:
                bill_id = create('account.move', {
                    'move_type': 'in_invoice',
                    'partner_id': vendors[0]['id'],
                    'journal_id': purch_j[0]['id'],
                    'invoice_date': '2026-02-20',
                    'invoice_line_ids': [(0, 0, {
                        'name': f'Branch Purchase - {branch_name}',
                        'quantity': 1,
                        'price_unit': amount * 0.6,
                        'analytic_distribution': {str(analytic_id): 100},
                    })]
                })
                print(f"     ✅ Created: ID {bill_id}")
                try:
                    execute('account.move', 'action_post', [[bill_id]])
                    print(f"     ✅ Posted!")
                except Exception as e:
                    print(f"     ⚠️ Post error: {str(e)[:100]}")
            except Exception as e:
                print(f"     ❌ Error: {str(e)[:150]}")

# Also create entries for WAREHOUSE analytic accounts
print("\n" + "═" * 80)
print("  CREATING TEST INVOICES PER WAREHOUSE")
print("═" * 80)

wh_data = [
    ('Near Home GF', analytic_map.get('Near Home GF'), 2000),
    ('Near Home FF', analytic_map.get('Near Home FF'), 1500),
    ('Factory Building', analytic_map.get('Factory Building'), 4000),
]

if sale_j and customers:
    for wh_name, analytic_id, amount in wh_data:
        if not analytic_id:
            print(f"  ⚠️ No analytic for {wh_name}")
            continue
        print(f"\n  🏭 Creating invoice for WH: {wh_name}...")
        try:
            inv_id = create('account.move', {
                'move_type': 'out_invoice',
                'partner_id': customers[1]['id'] if len(customers) > 1 else customers[0]['id'],
                'journal_id': sale_j[0]['id'],
                'invoice_date': '2026-02-22',
                'invoice_line_ids': [(0, 0, {
                    'name': f'Warehouse Sale - {wh_name}',
                    'quantity': 1,
                    'price_unit': amount,
                    'analytic_distribution': {str(analytic_id): 100},
                })]
            })
            print(f"     ✅ Created: ID {inv_id}")
            try:
                execute('account.move', 'action_post', [[inv_id]])
                print(f"     ✅ Posted!")
            except Exception as e:
                print(f"     ⚠️ Post error: {str(e)[:100]}")
        except Exception as e:
            print(f"     ❌ Error: {str(e)[:150]}")

# ── MULTI-ANALYTIC: Invoice split across 2 branches ──
print("\n" + "═" * 80)
print("  CREATING SPLIT ANALYTIC INVOICE (50% Branch A + 50% Branch B)")
print("═" * 80)

kr_id = analytic_map.get('Krishnadas group')
dev_id = analytic_map.get('Devika Furniture')
if kr_id and dev_id and sale_j and customers:
    try:
        split_inv = create('account.move', {
            'move_type': 'out_invoice',
            'partner_id': customers[0]['id'],
            'journal_id': sale_j[0]['id'],
            'invoice_date': '2026-02-24',
            'invoice_line_ids': [(0, 0, {
                'name': 'Split Sale - 50% Krishnadas + 50% Devika',
                'quantity': 1,
                'price_unit': 10000,
                'analytic_distribution': {str(kr_id): 50, str(dev_id): 50},
            })]
        })
        print(f"  ✅ Created split invoice: ID {split_inv}")
        try:
            execute('account.move', 'action_post', [[split_inv]])
            print(f"  ✅ Posted!")
        except Exception as e:
            print(f"  ⚠️ Post error: {str(e)[:100]}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:150]}")

# ── VERIFY ANALYTIC LINES ──
print("\n" + "═" * 80)
print("  VERIFYING: ANALYTIC LINES CREATED")
print("═" * 80)

al_count = count('account.analytic.line', [])
print(f"\n  Total analytic lines: {al_count}")

if al_count > 0:
    al_fields_raw = fields_get('account.analytic.line')
    safe_fields = ['name', 'amount', 'date', 'account_id']
    for f in ['general_account_id', 'company_id', 'move_line_id', 'category']:
        if f in al_fields_raw:
            safe_fields.append(f)
    
    lines = sr('account.analytic.line', [], safe_fields, limit=30, order='id desc')
    
    by_analytic = defaultdict(lambda: {'debit': 0, 'credit': 0, 'count': 0})
    
    for al in lines:
        acc = al['account_id'][1] if al.get('account_id') and al['account_id'] else 'N/A'
        gen = al.get('general_account_id', False)
        gen_name = gen[1] if isinstance(gen, (list, tuple)) and len(gen) > 1 else str(gen)
        co = al.get('company_id', False)
        co_name = co[1] if isinstance(co, (list, tuple)) and len(co) > 1 else str(co)
        amt = al.get('amount', 0)
        
        print(f"    {al.get('date','?')} | {al.get('name','?'):<45} | Analytic: {acc:<20} | GL: {gen_name:<30} | Amt: {amt:>10.2f}")
        
        if amt >= 0:
            by_analytic[acc]['credit'] += amt
        else:
            by_analytic[acc]['debit'] += abs(amt)
        by_analytic[acc]['count'] += 1
    
    print(f"\n  ═══ SUMMARY BY ANALYTIC ACCOUNT ═══")
    for acc, data in sorted(by_analytic.items()):
        print(f"    {acc:<25} Revenue: {data['credit']:>10.2f}  Expense: {data['debit']:>10.2f}  Lines: {data['count']}")

# ── VERIFY JOURNAL ITEMS — WHICH HAVE ANALYTIC? ──
print("\n" + "═" * 80)
print("  VERIFYING: JOURNAL ITEMS WITH ANALYTIC DISTRIBUTION")
print("═" * 80)

move_lines = sr('account.move.line', [['parent_state', '=', 'posted']], 
    ['account_id', 'analytic_distribution', 'debit', 'credit', 'name'],
    limit=200, order='id desc')

type_map = {}
accounts = sr('account.account', [], ['name', 'code', 'account_type'])
for a in accounts:
    type_map[a['id']] = a

with_analytic = 0
without_analytic = 0
by_type_with = defaultdict(int)
by_type_without = defaultdict(int)

for ml in move_lines:
    acct_id = ml['account_id'][0] if ml['account_id'] else None
    has_ad = bool(ml.get('analytic_distribution'))
    if has_ad:
        with_analytic += 1
    else:
        without_analytic += 1
    
    if acct_id and acct_id in type_map:
        atype = type_map[acct_id]['account_type']
        if has_ad:
            by_type_with[atype] += 1
        else:
            by_type_without[atype] += 1

print(f"\n  Total posted journal items: {len(move_lines)}")
print(f"  WITH analytic distribution: {with_analytic}")
print(f"  WITHOUT analytic distribution: {without_analytic}")

print(f"\n  {'Account Type':<35} {'WITH':<10} {'WITHOUT':<10}")
print(f"  {'-'*35} {'-'*10} {'-'*10}")
all_types = set(list(by_type_with.keys()) + list(by_type_without.keys()))
for atype in sorted(all_types):
    w = by_type_with.get(atype, 0)
    wo = by_type_without.get(atype, 0)
    marker = "✅" if w > 0 else "❌"
    print(f"  {marker} {atype:<33} {w:<10} {wo:<10}")

# ── Check specific lines ──
print(f"\n  Sample journal items WITH analytic distribution:")
for ml in move_lines:
    if ml.get('analytic_distribution'):
        acct = ml['account_id'][1] if ml['account_id'] else 'N/A'
        print(f"    ✅ {acct:<40} D:{ml['debit']:>8.2f} C:{ml['credit']:>8.2f} | AD: {json.dumps(ml['analytic_distribution'])}")

print(f"\n  Sample journal items WITHOUT analytic (first 10):")
shown = 0
for ml in move_lines:
    if not ml.get('analytic_distribution') and shown < 10:
        acct = ml['account_id'][1] if ml['account_id'] else 'N/A'
        print(f"    ❌ {acct:<40} D:{ml['debit']:>8.2f} C:{ml['credit']:>8.2f}")
        shown += 1

# ── CHECK KDESIGN INTERIOR FURNISHING (Company 4) SEPARATELY ──
print("\n" + "═" * 80)
print("  KDESIGN INTERIOR FURNISHING (Company 4) — SEPARATE COMPANY")
print("═" * 80)

kid_journals = sr('account.journal', [['company_id', '=', 4]], ['name', 'type'], limit=10)
print(f"  Journals: {[(j['name'], j['type']) for j in kid_journals]}")

kid_moves = sr('account.move', [['company_id', '=', 4], ['state', '=', 'posted']], 
    ['name', 'move_type', 'amount_total'], limit=10)
print(f"  Posted entries: {len(kid_moves)}")
for m in kid_moves:
    print(f"    {m['name']} | {m['move_type']} | {m['amount_total']}")

# ── STOCK REPORTING CAPABILITIES ──
print("\n" + "═" * 80)
print("  STOCK / INVENTORY REPORTING BY WAREHOUSE")
print("═" * 80)

# Check stock.picking for analytic
try:
    sp_fields = fields_get('stock.picking')
    analytic_sp = {k:v for k,v in sp_fields.items() if 'analytic' in k.lower()}
    print(f"  stock.picking analytic fields: {list(analytic_sp.keys()) if analytic_sp else 'NONE'}")
    for k,v in analytic_sp.items():
        print(f"    • {k}: {v.get('string','?')}")
except Exception as e:
    print(f"  ❌ {e}")

try:
    sm_fields = fields_get('stock.move')
    analytic_sm = {k:v for k,v in sm_fields.items() if 'analytic' in k.lower()}
    print(f"  stock.move analytic fields: {list(analytic_sm.keys()) if analytic_sm else 'NONE'}")
    for k,v in analytic_sm.items():
        print(f"    • {k}: {v.get('string','?')}")
except Exception as e:
    print(f"  ❌ {e}")

# Check stock.quant (inventory) groupby warehouse
print(f"\n  Current Inventory by Warehouse:")
quants = sr('stock.quant', [['location_id.usage', '=', 'internal'], ['quantity', '>', 0]], 
    ['product_id', 'location_id', 'quantity', 'warehouse_id'], limit=50)

by_wh = defaultdict(list)
for q in quants:
    wh = q.get('warehouse_id')
    wh_name = wh[1] if isinstance(wh, (list, tuple)) and len(wh) > 1 else 'Unknown'
    prod = q['product_id'][1] if q['product_id'] else 'N/A'
    loc = q['location_id'][1] if q['location_id'] else 'N/A'
    by_wh[wh_name].append(f"{prod}: {q['quantity']} @ {loc}")

for wh_name, items in sorted(by_wh.items()):
    print(f"  📦 {wh_name}:")
    for item in items:
        print(f"      {item}")

# ── SALE ORDER LINE ANALYTIC ──
print("\n" + "═" * 80)
print("  SALE ORDER / PURCHASE ORDER ANALYTIC FIELDS")
print("═" * 80)

for model_name in ['sale.order.line', 'purchase.order.line']:
    try:
        f = fields_get(model_name)
        analytic_f = {k:v for k,v in f.items() if 'analytic' in k.lower()}
        print(f"\n  {model_name}:")
        if analytic_f:
            for k, v in analytic_f.items():
                print(f"    ✅ {k}: {v.get('string','?')} ({v.get('type','?')})")
        else:
            print(f"    ❌ No analytic fields")
    except Exception as e:
        print(f"  {model_name}: {str(e)[:80]}")

print("\n\n  ✅ ALL DONE!")
