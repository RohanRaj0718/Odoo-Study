"""
Create invoices for the confirmed SOs that couldn't be invoiced via _create_invoices.
Then register payments for selected ones.

SOs needing invoices:
  SO 29 (KG): Rajan Pillai - Recliner(24000)+Fan(8500x2) = 41000 + tax → PAY
  SO 31 (Devika): Rajan Pillai - Bedsheet(2499x10)+Fabric(280x20) = 30590 + tax → NO PAY
  SO 32 (Devika): Varghese - Recliner(39000x2)+Art(2500x5) = 90500 + tax → PARTIAL PAY 50000
  SO 34 (KDESIGN): Rajan Pillai - Track(4500x4)+Blind(350x10) = 21500 + tax → FULL PAY
  SO 36 (KFURN): Varghese - Chimney(18500x2)+Hob(14500x2) = 66000 + tax → NO PAY
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

def action(model, method, ids):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, [ids])
    except Exception as e:
        if "cannot marshal None" in str(e):
            return True
        raise

def sr(model, domain, fields, limit=5):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# Partner IDs
RAJAN = 57
VARGHESE = 53

# Company/Journal
KG = 1; DEVIKA = 2; KDESIGN = 3; KFURN = 4
BANK_KG = 12; BANK_DEVIKA = 30; BANK_KDESIGN = 36; BANK_KFURN = 21

# Tax IDs from products: sale tax [36, 328] = 18% GST split (9% SGST + 9% CGST)
SALE_TAX = [36, 328]

invoices_to_create = [
    {
        'partner_id': RAJAN,
        'company_id': KG,
        'lines': [
            {'product_id': 18, 'quantity': 1, 'price_unit': 24000, 'name': '1/9097 Carolina Lithgow Black Recliner', 'tax_ids': SALE_TAX},
            {'product_id': 49, 'quantity': 2, 'price_unit': 8500, 'name': 'BLDC Designer Ceiling Fan 48inch', 'tax_ids': SALE_TAX},
        ],
        'pay': True, 'pay_amount': 41000, 'journal_id': BANK_KG,
        'label': 'KG: Rajan Pillai [Invoice + Full Pay]'
    },
    {
        'partner_id': RAJAN,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 2, 'quantity': 10, 'price_unit': 2499, 'name': 'Atlantic Classic Bedsheet', 'tax_ids': SALE_TAX},
            {'product_id': 43, 'quantity': 20, 'price_unit': 280, 'name': 'Blackout Lining Fabric 48inch', 'tax_ids': SALE_TAX},
        ],
        'pay': False,
        'label': 'Devika: Rajan Pillai [Invoice, NO Pay]'
    },
    {
        'partner_id': VARGHESE,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 17, 'quantity': 2, 'price_unit': 39000, 'name': 'Las Vegas Recliner Ivory', 'tax_ids': SALE_TAX},
            {'product_id': 53, 'quantity': 5, 'price_unit': 2500, 'name': 'Canvas Abstract Wall Art 24x36', 'tax_ids': SALE_TAX},
        ],
        'pay': True, 'pay_amount': 50000, 'journal_id': BANK_DEVIKA,
        'label': 'Devika: Varghese [Invoice + Partial Pay 50K]'
    },
    {
        'partner_id': RAJAN,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 13, 'quantity': 4, 'price_unit': 4500, 'name': 'Somfy Track', 'tax_ids': SALE_TAX},
            {'product_id': 7, 'quantity': 10, 'price_unit': 350, 'name': 'Roller Blind Clutch With Chain', 'tax_ids': SALE_TAX},
        ],
        'pay': True, 'pay_amount': 21500, 'journal_id': BANK_KDESIGN,
        'label': 'KDESIGN: Rajan Pillai [Invoice + Full Pay]'
    },
    {
        'partner_id': VARGHESE,
        'company_id': KFURN,
        'lines': [
            {'product_id': 27, 'quantity': 2, 'price_unit': 18500, 'name': 'Built-in Chimney 60cm Auto Clean', 'tax_ids': SALE_TAX},
            {'product_id': 28, 'quantity': 2, 'price_unit': 14500, 'name': 'Built-in Hob 4 Burner SS', 'tax_ids': SALE_TAX},
        ],
        'pay': False,
        'label': 'KFURN: Varghese [Invoice, NO Pay]'
    },
]

print("=" * 60)
print("CREATING INVOICES FROM CONFIRMED SALE ORDERS")
print("=" * 60)

for i, inv in enumerate(invoices_to_create):
    print(f"\n[{i+1}] {inv['label']}")
    try:
        # Create invoice header
        inv_id = create('account.move', {
            'partner_id': inv['partner_id'],
            'company_id': inv['company_id'],
            'move_type': 'out_invoice',
            'invoice_date': '2026-03-03',
        })
        print(f"  Created invoice ID: {inv_id}")

        # Add lines
        for line in inv['lines']:
            create('account.move.line', {
                'move_id': inv_id,
                'product_id': line['product_id'],
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'name': line['name'],
                'tax_ids': [(6, 0, line['tax_ids'])],
            })
            print(f"  Line: {line['name']} x{line['quantity']} @ {line['price_unit']}")

        # Post invoice
        action('account.move', 'action_post', [inv_id])
        
        # Get posted invoice details
        posted = sr('account.move', [['id', '=', inv_id]], ['name', 'amount_total', 'state'])
        if posted:
            print(f"  POSTED: {posted[0]['name']} | Total: {posted[0]['amount_total']} | State: {posted[0]['state']}")

        # Pay if needed
        if inv.get('pay'):
            pay_id = create('account.payment', {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': inv['partner_id'],
                'amount': inv['pay_amount'],
                'journal_id': inv['journal_id'],
                'company_id': inv['company_id'],
                'date': '2026-03-03',
            })
            action('account.payment', 'action_post', [pay_id])
            print(f"  Payment POSTED: {inv['pay_amount']}")

    except Exception as e:
        print(f"  ERROR: {e}")

# ── Final counts ──
print("\n" + "=" * 60)
print("UPDATED FINAL COUNTS")
print("=" * 60)

companies = sr('res.company', [], ['name'], limit=10)
for c in companies:
    cid = c['id']
    inv_total = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice']]])
    inv_posted = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice'], ['state', '=', 'posted']]])
    bill_total = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice']]])
    bill_posted = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice'], ['state', '=', 'posted']]])
    pay_total = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['company_id', '=', cid]]])
    so_total = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid]]])
    so_draft = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    po_total = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid]]])
    po_draft = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    
    print(f"\n{c['name']}:")
    print(f"  SO: {so_total} ({so_total - so_draft} confirmed, {so_draft} draft)")
    print(f"  PO: {po_total} ({po_total - po_draft} confirmed, {po_draft} draft)")
    print(f"  Invoices: {inv_total} ({inv_posted} posted)")
    print(f"  Bills: {bill_total} ({bill_posted} posted)")
    print(f"  Payments: {pay_total}")

print("\n=== DONE ===")
