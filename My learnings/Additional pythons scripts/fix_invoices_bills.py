"""
Fix Script: Create Invoices & Bills directly via account.move
Since _create_invoices is a private method, we create invoices/bills directly.
"""
import xmlrpc.client
import datetime
import sys

URL = "https://demo-company15.odoo.com"
DB = "demo-company15"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def execute(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

def search_read(model, domain, fields):
    return execute(model, 'search_read', [domain], {'fields': fields})

def create(model, vals):
    return execute(model, 'create', [vals])

TODAY = datetime.date.today().isoformat()
print("=" * 60)
print("CREATING INVOICES & BILLS (Direct Method)")
print("=" * 60)

# ── Lookup existing partners ──
def get_partner_id(name):
    r = search_read('res.partner', [['name', '=', name]], ['id'])
    return r[0]['id'] if r else None

def get_product_id(name):
    r = search_read('product.product', [['name', '=', name]], ['id'])
    return r[0]['id'] if r else None

# ── CUSTOMER INVOICES ──
print("\n── Creating Customer Invoices ──")

invoices_data = [
    {
        "desc": "INV1: Tech Solutions - 10x Consulting @ $150",
        "partner_id": get_partner_id("Tech Solutions Inc."),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Professional Consulting Services"),
                    "quantity": 10, "price_unit": 150.00,
                    "name": "Professional Consulting Services"}]
    },
    {
        "desc": "INV2: Global Manufacturing - 1x Software License @ $500",
        "partner_id": get_partner_id("Global Manufacturing Co."),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Software License (Annual)"),
                    "quantity": 1, "price_unit": 500.00,
                    "name": "Software License (Annual)"}]
    },
    {
        "desc": "INV3: Retail Stores - 1x Equipment @ $1,200",
        "partner_id": get_partner_id("Retail Stores Group"),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Office Equipment Package"),
                    "quantity": 1, "price_unit": 1200.00,
                    "name": "Office Equipment Package"}]
    },
    {
        "desc": "INV4: ABC Enterprises - 3x Training @ $300",
        "partner_id": get_partner_id("ABC Enterprises"),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Training Workshop"),
                    "quantity": 3, "price_unit": 300.00,
                    "name": "Training Workshop"}]
    },
    {
        "desc": "INV5: Quick Buy - 1x Maintenance @ $2,400",
        "partner_id": get_partner_id("Quick Buy Ltd"),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Annual Maintenance Contract"),
                    "quantity": 1, "price_unit": 2400.00,
                    "name": "Annual Maintenance Contract"}]
    },
    {
        "desc": "INV6: Tech Solutions - 2x Software License @ $500 (partial pay scenario)",
        "partner_id": get_partner_id("Tech Solutions Inc."),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Software License (Annual)"),
                    "quantity": 2, "price_unit": 500.00,
                    "name": "Software License (Annual)"}]
    },
    {
        "desc": "INV7: Tech Solutions - 2x Consulting @ $150 (multi-invoice scenario)",
        "partner_id": get_partner_id("Tech Solutions Inc."),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Professional Consulting Services"),
                    "quantity": 2, "price_unit": 150.00,
                    "name": "Professional Consulting Services"}]
    },
    {
        "desc": "INV8: Tech Solutions - 1x Training @ $300 (multi-invoice scenario)",
        "partner_id": get_partner_id("Tech Solutions Inc."),
        "move_type": "out_invoice",
        "lines": [{"product_id": get_product_id("Training Workshop"),
                    "quantity": 1, "price_unit": 300.00,
                    "name": "Training Workshop"}]
    },
]

invoice_count = 0
for inv in invoices_data:
    try:
        lines = []
        for line in inv["lines"]:
            line_vals = {
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'name': line['name'],
            }
            if line.get('product_id'):
                line_vals['product_id'] = line['product_id']
            lines.append((0, 0, line_vals))
        
        inv_id = create('account.move', {
            'move_type': inv['move_type'],
            'partner_id': inv['partner_id'],
            'invoice_date': TODAY,
            'date': TODAY,
            'invoice_line_ids': lines,
        })
        
        # Post the invoice
        execute('account.move', 'action_post', [[inv_id]])
        
        # Read back the invoice number
        inv_data = search_read('account.move', [['id', '=', inv_id]], ['name', 'amount_total'])
        inv_name = inv_data[0]['name'] if inv_data else f"ID:{inv_id}"
        inv_amount = inv_data[0]['amount_total'] if inv_data else '?'
        print(f"  ✅ {inv['desc']}")
        print(f"     ↳ {inv_name} posted | Total: ${inv_amount}")
        invoice_count += 1
        
    except Exception as e:
        print(f"  ❌ {inv['desc']}: {e}")

# ── VENDOR BILLS ──
print("\n── Creating Vendor Bills ──")

bills_data = [
    {
        "desc": "BILL1: Office Supplies Co. - $450",
        "partner_id": get_partner_id("Office Supplies Co."),
        "move_type": "in_invoice",
        "lines": [{"product_id": get_product_id("Office Supplies"),
                    "quantity": 1, "price_unit": 450.00,
                    "name": "Office Supplies"}]
    },
    {
        "desc": "BILL2: Tech Hardware - 3x Computers @ $800",
        "partner_id": get_partner_id("Tech Hardware Supplier"),
        "move_type": "in_invoice",
        "lines": [{"product_id": get_product_id("Computer Equipment"),
                    "quantity": 3, "price_unit": 800.00,
                    "name": "Computer Equipment"}]
    },
    {
        "desc": "BILL3: Cloud Services - Monthly @ $49.99",
        "partner_id": get_partner_id("Cloud Services LLC"),
        "move_type": "in_invoice",
        "lines": [{"product_id": get_product_id("Cloud Hosting Subscription"),
                    "quantity": 1, "price_unit": 49.99,
                    "name": "Cloud Hosting Subscription"}]
    },
    {
        "desc": "BILL4: Equipment Rental - $300",
        "partner_id": get_partner_id("Equipment Rentals Inc."),
        "move_type": "in_invoice",
        "lines": [{"product_id": get_product_id("Equipment Rental - Monthly"),
                    "quantity": 1, "price_unit": 300.00,
                    "name": "Equipment Rental - Monthly"}]
    },
    {
        "desc": "BILL5: Raw Materials - $1,800",
        "partner_id": get_partner_id("Raw Materials Supplier"),
        "move_type": "in_invoice",
        "lines": [{"product_id": get_product_id("Raw Materials Batch"),
                    "quantity": 1, "price_unit": 1800.00,
                    "name": "Raw Materials Batch"}]
    },
]

bill_count = 0
for bill in bills_data:
    try:
        lines = []
        for line in bill["lines"]:
            line_vals = {
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'name': line['name'],
            }
            if line.get('product_id'):
                line_vals['product_id'] = line['product_id']
            lines.append((0, 0, line_vals))
        
        bill_id = create('account.move', {
            'move_type': bill['move_type'],
            'partner_id': bill['partner_id'],
            'invoice_date': TODAY,
            'date': TODAY,
            'invoice_line_ids': lines,
        })
        
        # Post the bill
        execute('account.move', 'action_post', [[bill_id]])
        
        # Read back
        bill_data = search_read('account.move', [['id', '=', bill_id]], ['name', 'amount_total'])
        bill_name = bill_data[0]['name'] if bill_data else f"ID:{bill_id}"
        bill_amount = bill_data[0]['amount_total'] if bill_data else '?'
        print(f"  ✅ {bill['desc']}")
        print(f"     ↳ {bill_name} posted | Total: ${bill_amount}")
        bill_count += 1
        
    except Exception as e:
        print(f"  ❌ {bill['desc']}: {e}")

# ── FINAL SUMMARY ──
print("\n" + "=" * 60)
print("INVOICES & BILLS CREATION COMPLETE!")
print("=" * 60)
print(f"  Customer Invoices created & posted: {invoice_count}/8")
print(f"  Vendor Bills created & posted:      {bill_count}/5")
print(f"""
Your Odoo database now has:
  ✅ 5 Customers + 5 Vendors
  ✅ 10 Products
  ✅ 8 Confirmed Sales Orders
  ✅ {invoice_count} Posted Customer Invoices
  ✅ 5 Confirmed Purchase Orders
  ✅ {bill_count} Posted Vendor Bills
  ✅ 20 Bank Transactions ready to reconcile

🎯 Go to Accounting > Bank to start reconciling!
""")
