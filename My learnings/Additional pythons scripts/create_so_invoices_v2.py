"""
Fix invoices: Delete draft invoices, recreate with correct company taxes.
- KG (1), Devika (2), KDESIGN (3) are same group → use KG tax ID 36 (5% GST S)
- KFURN (4) is separate → use KFURN tax ID 328 (5% GST S)

Actually: let's NOT specify taxes and let Odoo pick from product defaults.
Or better: look up what tax the product ACTUALLY uses for that company.
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def create(model, vals):
    return models.execute_kw(DB, uid, PASSWORD, model, 'create', [vals])

def write(model, ids, vals):
    return models.execute_kw(DB, uid, PASSWORD, model, 'write', [ids, vals])

def unlink(model, ids):
    return models.execute_kw(DB, uid, PASSWORD, model, 'unlink', [ids])

def action(model, method, ids):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, [ids])
    except Exception as e:
        if "cannot marshal None" in str(e):
            return True
        raise

def sr(model, domain, fields, limit=50):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# ── Step 1: Delete draft invoices 57-61 ──
print("Step 1: Deleting broken draft invoices...")
draft_ids = [57, 58, 59, 60, 61]
# First delete any lines on them
lines = sr('account.move.line', [['move_id', 'in', draft_ids]], ['id'])
if lines:
    line_ids = [l['id'] for l in lines]
    print(f"  Deleting {len(line_ids)} move lines...")
    # Can't easily delete lines on a move, let's just try deleting the move (which cascades)

try:
    # Need to cancel first if posted, but they are draft so can delete directly
    # Actually in Odoo, we may need to use button_draft first
    unlink('account.move', draft_ids)
    print(f"  Deleted invoices {draft_ids}")
except Exception as e:
    print(f"  Could not delete: {e}")
    # Try one by one
    for did in draft_ids:
        try:
            unlink('account.move', [did])
            print(f"  Deleted invoice {did}")
        except Exception as e2:
            print(f"  Cannot delete {did}: {e2}")

# ── Step 2: Tax mapping per company ──
# For KG (1) and its branches Devika (2), KDESIGN (3): use tax 36 (5% GST S from KG)
# For KFURN (4): use tax 328 (5% GST S from KFURN)
# Let's also check: existing invoices use what taxes?
print("\nStep 2: Checking existing posted invoices for tax usage...")
existing_inv = sr('account.move', [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']], 
                  ['name', 'company_id'], limit=3)
if existing_inv:
    inv_id = existing_inv[0]['id']
    inv_lines = sr('account.move.line', [['move_id', '=', inv_id], ['product_id', '!=', False]], 
                   ['name', 'tax_ids', 'product_id'])
    print(f"  Sample: {existing_inv[0]['name']} ({existing_inv[0]['company_id'][1]})")
    for l in inv_lines:
        print(f"    Product: {l['product_id'][1] if l['product_id'] else 'N/A'}, Tax IDs: {l['tax_ids']}")

# ── Step 3: Create invoices properly ──
# Tax approach: Use only company-appropriate taxa
# KG/Devika/KDESIGN branches share KG's taxes
TAX_MAP = {
    1: [36],   # KG: 5% GST S
    2: [36],   # Devika: uses KG's tax (branch)
    3: [36],   # KDESIGN: uses KG's tax (branch)
    4: [328],  # KFURN: own 5% GST S
}

# Partner IDs
RAJAN = 57
VARGHESE = 53

# Company/Journal
KG = 1; DEVIKA = 2; KDESIGN = 3; KFURN = 4
BANK_KG = 12; BANK_DEVIKA = 30; BANK_KDESIGN = 36; BANK_KFURN = 21

invoices_to_create = [
    {
        'partner_id': RAJAN,
        'company_id': KG,
        'lines': [
            {'product_id': 18, 'quantity': 1, 'price_unit': 24000, 'name': '1/9097 Carolina Lithgow Black Recliner'},
            {'product_id': 49, 'quantity': 2, 'price_unit': 8500, 'name': 'BLDC Designer Ceiling Fan 48inch'},
        ],
        'pay': True, 'pay_amount': 41000, 'journal_id': BANK_KG,
        'label': 'KG: Rajan Pillai [Invoice + Full Pay ₹41K]'
    },
    {
        'partner_id': RAJAN,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 2, 'quantity': 10, 'price_unit': 2499, 'name': 'Atlantic Classic Bedsheet'},
            {'product_id': 43, 'quantity': 20, 'price_unit': 280, 'name': 'Blackout Lining Fabric 48inch'},
        ],
        'pay': False,
        'label': 'Devika: Rajan Pillai [Invoice, NO Pay]'
    },
    {
        'partner_id': VARGHESE,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 17, 'quantity': 2, 'price_unit': 39000, 'name': 'Las Vegas Recliner Ivory'},
            {'product_id': 53, 'quantity': 5, 'price_unit': 2500, 'name': 'Canvas Abstract Wall Art 24x36'},
        ],
        'pay': True, 'pay_amount': 50000, 'journal_id': BANK_DEVIKA,
        'label': 'Devika: Varghese [Invoice + Partial Pay ₹50K]'
    },
    {
        'partner_id': RAJAN,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 13, 'quantity': 4, 'price_unit': 4500, 'name': 'Somfy Track'},
            {'product_id': 7, 'quantity': 10, 'price_unit': 350, 'name': 'Roller Blind Clutch With Chain'},
        ],
        'pay': True, 'pay_amount': 21500, 'journal_id': BANK_KDESIGN,
        'label': 'KDESIGN: Rajan Pillai [Invoice + Full Pay ₹21.5K]'
    },
    {
        'partner_id': VARGHESE,
        'company_id': KFURN,
        'lines': [
            {'product_id': 27, 'quantity': 2, 'price_unit': 18500, 'name': 'Built-in Chimney 60cm Auto Clean'},
            {'product_id': 28, 'quantity': 2, 'price_unit': 14500, 'name': 'Built-in Hob 4 Burner SS'},
        ],
        'pay': False,
        'label': 'KFURN: Varghese [Invoice, NO Pay]'
    },
]

print("\n" + "=" * 60)
print("CREATING INVOICES WITH CORRECT COMPANY TAXES")
print("=" * 60)

for i, inv in enumerate(invoices_to_create):
    cid = inv['company_id']
    tax_ids = TAX_MAP[cid]
    print(f"\n[{i+1}] {inv['label']}")
    
    try:
        # Create invoice with inline lines using (0, 0, vals) command
        line_vals = []
        for line in inv['lines']:
            line_vals.append((0, 0, {
                'product_id': line['product_id'],
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'name': line['name'],
                'tax_ids': [(6, 0, tax_ids)],
            }))
        
        inv_id = create('account.move', {
            'partner_id': inv['partner_id'],
            'company_id': cid,
            'move_type': 'out_invoice',
            'invoice_date': '2026-03-03',
            'invoice_line_ids': line_vals,
        })
        print(f"  Created invoice ID: {inv_id}")

        # Post invoice
        action('account.move', 'action_post', [inv_id])
        
        # Get posted invoice details
        posted = sr('account.move', [['id', '=', inv_id]], ['name', 'amount_total', 'state', 'payment_state'])
        if posted:
            p = posted[0]
            print(f"  POSTED: {p['name']} | Total: ₹{p['amount_total']:,.2f} | State: {p['state']} | Payment: {p['payment_state']}")

        # Register payment if needed
        if inv.get('pay'):
            pay_id = create('account.payment', {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': inv['partner_id'],
                'amount': inv['pay_amount'],
                'journal_id': inv['journal_id'],
                'company_id': cid,
                'date': '2026-03-03',
            })
            action('account.payment', 'action_post', [pay_id])
            print(f"  Payment POSTED: ₹{inv['pay_amount']:,}")

    except Exception as e:
        print(f"  ERROR: {e}")

# ── Final counts ──
print("\n" + "=" * 60)
print("FINAL COMPREHENSIVE COUNTS")
print("=" * 60)

companies = sr('res.company', [], ['name'], limit=10)
for c in sorted(companies, key=lambda x: x['id']):
    cid = c['id']
    so_total = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid]]])
    so_confirmed = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'sale']]])
    so_draft = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    po_total = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid]]])
    po_confirmed = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'purchase']]])
    po_draft = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    inv_total = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice']]])
    inv_posted = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice'], ['state', '=', 'posted']]])
    inv_paid = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['payment_state', 'in', ['paid', 'in_payment']]]])
    inv_partial = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['payment_state', '=', 'partial']]])
    inv_unpaid = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['payment_state', '=', 'not_paid']]])
    bill_total = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice']]])
    bill_posted = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice'], ['state', '=', 'posted']]])
    bill_paid = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice'], ['state', '=', 'posted'], ['payment_state', 'in', ['paid', 'in_payment']]]])
    bill_unpaid = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice'], ['state', '=', 'posted'], ['payment_state', '=', 'not_paid']]])
    pay_total = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['company_id', '=', cid], ['state', '=', 'posted']]])
    
    print(f"\n{'─'*50}")
    print(f"  {c['name']} (ID={cid})")
    print(f"{'─'*50}")
    print(f"  Sales Orders:    {so_total:3d} total ({so_confirmed} confirmed, {so_draft} draft)")
    print(f"  Purchase Orders: {po_total:3d} total ({po_confirmed} confirmed, {po_draft} draft)")
    print(f"  Invoices (Cust): {inv_total:3d} total ({inv_posted} posted → {inv_paid} paid, {inv_partial} partial, {inv_unpaid} unpaid)")
    print(f"  Bills (Vendor):  {bill_total:3d} total ({bill_posted} posted → {bill_paid} paid, {bill_unpaid} unpaid)")
    print(f"  Payments:        {pay_total:3d} posted")

# ── Clean partners check ──
print("\n" + "=" * 60)
print("CLEAN PARTNERS (preserved for live demo)")
print("=" * 60)

clean_custs = [56, 52]  # Mohammed Ashraf, Priya Thomas
clean_vendors = [66, 67, 65]  # Decor World, Godrej, Nizar
for pid in clean_custs:
    p = sr('res.partner', [['id', '=', pid]], ['name'])
    inv_count = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['partner_id', '=', pid], ['move_type', '=', 'out_invoice']]])
    pay_count = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['partner_id', '=', pid]]])
    so_count = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['partner_id', '=', pid]]])
    print(f"  ✓ {p[0]['name']}: SO={so_count}, INV={inv_count}, PAY={pay_count}")

for pid in clean_vendors:
    p = sr('res.partner', [['id', '=', pid]], ['name'])
    bill_count = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['partner_id', '=', pid], ['move_type', '=', 'in_invoice']]])
    pay_count = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['partner_id', '=', pid]]])
    po_count = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['partner_id', '=', pid]]])
    print(f"  ✓ {p[0]['name']}: PO={po_count}, BILL={bill_count}, PAY={pay_count}")

print("\n=== ALL DONE ===")
