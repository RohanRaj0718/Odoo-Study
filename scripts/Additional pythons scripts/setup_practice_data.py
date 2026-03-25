"""
Odoo Bank Reconciliation Practice - Complete Setup Script
=========================================================
Creates all practice data in the Odoo database:
- Customers, Vendors, Products
- Sales Orders, Invoices
- Purchase Orders, Bills
- Bank Transactions for reconciliation practice

Uses Odoo XML-RPC API (official external API)
"""
import xmlrpc.client
import datetime
import sys
import time

# ──────────────────────────────────────────────────────────
# CONNECTION SETTINGS
# ──────────────────────────────────────────────────────────
URL = "https://demo-company15.odoo.com"
DB = "demo-company15"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

# ──────────────────────────────────────────────────────────
# CONNECT & AUTHENTICATE
# ──────────────────────────────────────────────────────────
print("=" * 60)
print("ODOO BANK RECONCILIATION - PRACTICE DATA SETUP")
print("=" * 60)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("❌ Authentication failed!")
    sys.exit(1)
print(f"✅ Connected as UID {uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def execute(model, method, *args, **kwargs):
    """Helper to call Odoo API."""
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

def search_read(model, domain, fields):
    """Search and read helper."""
    return execute(model, 'search_read', [domain], {'fields': fields})

def search(model, domain):
    """Search helper."""
    return execute(model, 'search', [domain])

def create(model, vals):
    """Create helper."""
    return execute(model, 'create', [vals])

def write(model, ids, vals):
    """Write helper."""
    return execute(model, 'write', [ids, vals])

TODAY = datetime.date.today().isoformat()

# ──────────────────────────────────────────────────────────
# PHASE 1: CREATE CUSTOMERS
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 1: Creating Customers...")
print("─" * 60)

customers_data = [
    {"name": "Tech Solutions Inc.", "email": "contact@techsolutions.com",
     "phone": "+1-555-0101", "is_company": True, "customer_rank": 1},
    {"name": "Global Manufacturing Co.", "email": "billing@globalmanuf.com",
     "phone": "+1-555-0102", "is_company": True, "customer_rank": 1},
    {"name": "Retail Stores Group", "email": "accounts@retailgroup.com",
     "phone": "+1-555-0103", "is_company": True, "customer_rank": 1},
    {"name": "ABC Enterprises", "email": "finance@abcent.com",
     "phone": "+1-555-0104", "is_company": True, "customer_rank": 1},
    {"name": "Quick Buy Ltd", "email": "payments@quickbuy.com",
     "phone": "+1-555-0105", "is_company": True, "customer_rank": 1},
]

customer_ids = {}
for cust in customers_data:
    # Check if customer already exists
    existing = search_read('res.partner', [['name', '=', cust['name']]], ['id', 'name'])
    if existing:
        cid = existing[0]['id']
        print(f"  ℹ️  Customer '{cust['name']}' already exists (ID: {cid})")
    else:
        cid = create('res.partner', cust)
        print(f"  ✅ Created customer '{cust['name']}' (ID: {cid})")
    customer_ids[cust['name']] = cid

# ──────────────────────────────────────────────────────────
# PHASE 2: CREATE VENDORS
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 2: Creating Vendors...")
print("─" * 60)

vendors_data = [
    {"name": "Office Supplies Co.", "email": "sales@officesupplies.com",
     "phone": "+1-555-0201", "is_company": True, "supplier_rank": 1},
    {"name": "Tech Hardware Supplier", "email": "orders@techhardware.com",
     "phone": "+1-555-0202", "is_company": True, "supplier_rank": 1},
    {"name": "Cloud Services LLC", "email": "billing@cloudservices.com",
     "phone": "+1-555-0203", "is_company": True, "supplier_rank": 1},
    {"name": "Equipment Rentals Inc.", "email": "accounts@equiprent.com",
     "phone": "+1-555-0204", "is_company": True, "supplier_rank": 1},
    {"name": "Raw Materials Supplier", "email": "sales@rawmaterials.com",
     "phone": "+1-555-0205", "is_company": True, "supplier_rank": 1},
]

vendor_ids = {}
for vend in vendors_data:
    existing = search_read('res.partner', [['name', '=', vend['name']]], ['id', 'name'])
    if existing:
        vid = existing[0]['id']
        print(f"  ℹ️  Vendor '{vend['name']}' already exists (ID: {vid})")
    else:
        vid = create('res.partner', vend)
        print(f"  ✅ Created vendor '{vend['name']}' (ID: {vid})")
    vendor_ids[vend['name']] = vid

# ──────────────────────────────────────────────────────────
# PHASE 3: CREATE PRODUCTS
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 3: Creating Products...")
print("─" * 60)

products_data = [
    {"name": "Professional Consulting Services", "type": "service",
     "list_price": 150.00, "sale_ok": True, "purchase_ok": False},
    {"name": "Software License (Annual)", "type": "service",
     "list_price": 500.00, "sale_ok": True, "purchase_ok": False},
    {"name": "Office Equipment Package", "type": "consu",
     "list_price": 1200.00, "standard_price": 800.00,
     "sale_ok": True, "purchase_ok": True},
    {"name": "Training Workshop", "type": "service",
     "list_price": 300.00, "sale_ok": True, "purchase_ok": False},
    {"name": "Annual Maintenance Contract", "type": "service",
     "list_price": 2400.00, "sale_ok": True, "purchase_ok": False},
]

product_ids = {}
for prod in products_data:
    existing = search_read('product.template', [['name', '=', prod['name']]], ['id', 'name'])
    if existing:
        pid = existing[0]['id']
        print(f"  ℹ️  Product '{prod['name']}' already exists (ID: {pid})")
        # Get the product.product id
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        product_ids[prod['name']] = pp[0]['id'] if pp else pid
    else:
        pid = create('product.template', prod)
        print(f"  ✅ Created product '{prod['name']}' (ID: {pid})")
        # Get the product.product id
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        product_ids[prod['name']] = pp[0]['id'] if pp else pid

# Also create purchase-only products
purchase_products_data = [
    {"name": "Office Supplies", "type": "consu",
     "list_price": 0, "standard_price": 450.00,
     "sale_ok": False, "purchase_ok": True},
    {"name": "Computer Equipment", "type": "consu",
     "list_price": 0, "standard_price": 800.00,
     "sale_ok": False, "purchase_ok": True},
    {"name": "Cloud Hosting Subscription", "type": "service",
     "list_price": 0, "standard_price": 49.99,
     "sale_ok": False, "purchase_ok": True},
    {"name": "Equipment Rental - Monthly", "type": "service",
     "list_price": 0, "standard_price": 300.00,
     "sale_ok": False, "purchase_ok": True},
    {"name": "Raw Materials Batch", "type": "consu",
     "list_price": 0, "standard_price": 1800.00,
     "sale_ok": False, "purchase_ok": True},
]

purchase_product_ids = {}
for prod in purchase_products_data:
    existing = search_read('product.template', [['name', '=', prod['name']]], ['id', 'name'])
    if existing:
        pid = existing[0]['id']
        print(f"  ℹ️  Product '{prod['name']}' already exists (ID: {pid})")
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        purchase_product_ids[prod['name']] = pp[0]['id'] if pp else pid
    else:
        pid = create('product.template', prod)
        print(f"  ✅ Created product '{prod['name']}' (ID: {pid})")
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        purchase_product_ids[prod['name']] = pp[0]['id'] if pp else pid

# ──────────────────────────────────────────────────────────
# PHASE 4: CREATE SALES ORDERS & INVOICES
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 4: Creating Sales Orders & Invoices...")
print("─" * 60)

sales_orders = [
    {
        "desc": "SO1: Tech Solutions - Consulting ($1,500)",
        "partner_id": customer_ids["Tech Solutions Inc."],
        "lines": [{"product_id": product_ids["Professional Consulting Services"],
                    "product_uom_qty": 10, "price_unit": 150.00}]
    },
    {
        "desc": "SO2: Global Manufacturing - Software ($500)",
        "partner_id": customer_ids["Global Manufacturing Co."],
        "lines": [{"product_id": product_ids["Software License (Annual)"],
                    "product_uom_qty": 1, "price_unit": 500.00}]
    },
    {
        "desc": "SO3: Retail Stores - Equipment ($1,200)",
        "partner_id": customer_ids["Retail Stores Group"],
        "lines": [{"product_id": product_ids["Office Equipment Package"],
                    "product_uom_qty": 1, "price_unit": 1200.00}]
    },
    {
        "desc": "SO4: ABC Enterprises - Training ($900)",
        "partner_id": customer_ids["ABC Enterprises"],
        "lines": [{"product_id": product_ids["Training Workshop"],
                    "product_uom_qty": 3, "price_unit": 300.00}]
    },
    {
        "desc": "SO5: Quick Buy - Maintenance ($2,400)",
        "partner_id": customer_ids["Quick Buy Ltd"],
        "lines": [{"product_id": product_ids["Annual Maintenance Contract"],
                    "product_uom_qty": 1, "price_unit": 2400.00}]
    },
    {
        "desc": "SO6: Tech Solutions - Software x2 ($1,000 - partial payment scenario)",
        "partner_id": customer_ids["Tech Solutions Inc."],
        "lines": [{"product_id": product_ids["Software License (Annual)"],
                    "product_uom_qty": 2, "price_unit": 500.00}]
    },
    {
        "desc": "SO7: Tech Solutions - Consulting x2 ($300 - multi-invoice scenario)",
        "partner_id": customer_ids["Tech Solutions Inc."],
        "lines": [{"product_id": product_ids["Professional Consulting Services"],
                    "product_uom_qty": 2, "price_unit": 150.00}]
    },
    {
        "desc": "SO8: Tech Solutions - Training ($300 - multi-invoice scenario)",
        "partner_id": customer_ids["Tech Solutions Inc."],
        "lines": [{"product_id": product_ids["Training Workshop"],
                    "product_uom_qty": 1, "price_unit": 300.00}]
    },
]

invoice_ids = []
for so in sales_orders:
    try:
        # Create SO
        order_lines = []
        for line in so["lines"]:
            order_lines.append((0, 0, {
                'product_id': line['product_id'],
                'product_uom_qty': line['product_uom_qty'],
                'price_unit': line['price_unit'],
            }))
        
        so_id = create('sale.order', {
            'partner_id': so['partner_id'],
            'date_order': TODAY,
            'order_line': order_lines,
        })
        print(f"  ✅ Created {so['desc']} (SO ID: {so_id})")
        
        # Confirm the SO
        execute('sale.order', 'action_confirm', [[so_id]])
        print(f"     ↳ Confirmed")
        
        # Create invoice
        inv_action = execute('sale.order', '_create_invoices', [[so_id]])
        
        # Find the invoice
        so_data = search_read('sale.order', [['id', '=', so_id]], ['invoice_ids'])
        if so_data and so_data[0].get('invoice_ids'):
            inv_id = so_data[0]['invoice_ids'][0]
            # Confirm the invoice
            execute('account.move', 'action_post', [[inv_id]])
            inv_data = search_read('account.move', [['id', '=', inv_id]], ['name', 'amount_total'])
            inv_name = inv_data[0]['name'] if inv_data else f"INV-{inv_id}"
            inv_amount = inv_data[0]['amount_total'] if inv_data else '?'
            print(f"     ↳ Invoice {inv_name} created & posted (${inv_amount})")
            invoice_ids.append(inv_id)
        else:
            print(f"     ⚠️  Could not find invoice for SO {so_id}")
            
    except Exception as e:
        print(f"  ❌ Error creating {so['desc']}: {e}")

print(f"\n  📊 Total invoices created: {len(invoice_ids)}")

# ──────────────────────────────────────────────────────────
# PHASE 5: CREATE PURCHASE ORDERS & BILLS
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 5: Creating Purchase Orders & Bills...")
print("─" * 60)

purchase_orders = [
    {
        "desc": "PO1: Office Supplies ($450)",
        "partner_id": vendor_ids["Office Supplies Co."],
        "lines": [{"product_id": purchase_product_ids["Office Supplies"],
                    "product_qty": 1, "price_unit": 450.00}]
    },
    {
        "desc": "PO2: Tech Hardware - 3 Computers ($2,400)",
        "partner_id": vendor_ids["Tech Hardware Supplier"],
        "lines": [{"product_id": purchase_product_ids["Computer Equipment"],
                    "product_qty": 3, "price_unit": 800.00}]
    },
    {
        "desc": "PO3: Cloud Services - Monthly ($49.99)",
        "partner_id": vendor_ids["Cloud Services LLC"],
        "lines": [{"product_id": purchase_product_ids["Cloud Hosting Subscription"],
                    "product_qty": 1, "price_unit": 49.99}]
    },
    {
        "desc": "PO4: Equipment Rental ($300)",
        "partner_id": vendor_ids["Equipment Rentals Inc."],
        "lines": [{"product_id": purchase_product_ids["Equipment Rental - Monthly"],
                    "product_qty": 1, "price_unit": 300.00}]
    },
    {
        "desc": "PO5: Raw Materials ($1,800)",
        "partner_id": vendor_ids["Raw Materials Supplier"],
        "lines": [{"product_id": purchase_product_ids["Raw Materials Batch"],
                    "product_qty": 1, "price_unit": 1800.00}]
    },
]

bill_ids = []
for po in purchase_orders:
    try:
        order_lines = []
        for line in po["lines"]:
            order_lines.append((0, 0, {
                'product_id': line['product_id'],
                'product_qty': line['product_qty'],
                'price_unit': line['price_unit'],
            }))
        
        po_id = create('purchase.order', {
            'partner_id': po['partner_id'],
            'date_order': TODAY,
            'order_line': order_lines,
        })
        print(f"  ✅ Created {po['desc']} (PO ID: {po_id})")
        
        # Confirm PO
        execute('purchase.order', 'button_confirm', [[po_id]])
        print(f"     ↳ Confirmed")
        
        # Create Bill from PO
        # In Odoo, we create vendor bill as account.move directly
        po_data = search_read('purchase.order', [['id', '=', po_id]],
                              ['name', 'partner_id', 'order_line', 'invoice_ids'])
        
        # Use action_create_invoice if available
        try:
            execute('purchase.order', 'action_create_invoice', [[po_id]])
            # Re-read to get invoice
            po_data = search_read('purchase.order', [['id', '=', po_id]], ['invoice_ids'])
            if po_data and po_data[0].get('invoice_ids'):
                bill_id = po_data[0]['invoice_ids'][0]
                execute('account.move', 'action_post', [[bill_id]])
                bill_data = search_read('account.move', [['id', '=', bill_id]], ['name', 'amount_total'])
                bill_name = bill_data[0]['name'] if bill_data else f"BILL-{bill_id}"
                bill_amount = bill_data[0]['amount_total'] if bill_data else '?'
                print(f"     ↳ Bill {bill_name} created & posted (${bill_amount})")
                bill_ids.append(bill_id)
        except Exception as e:
            print(f"     ⚠️  Could not auto-create bill: {e}")
            print(f"     ℹ️  You can create the bill manually from PO in Odoo")
    except Exception as e:
        print(f"  ❌ Error creating {po['desc']}: {e}")

print(f"\n  📊 Total bills created: {len(bill_ids)}")

# ──────────────────────────────────────────────────────────
# PHASE 6: CREATE BANK TRANSACTIONS
# ──────────────────────────────────────────────────────────
print("\n" + "─" * 60)
print("PHASE 6: Creating Bank Transactions for Reconciliation...")
print("─" * 60)

# Find the bank journal
bank_journals = search_read('account.journal', [['type', '=', 'bank']], ['id', 'name'])
if not bank_journals:
    print("  ❌ No bank journal found!")
    sys.exit(1)

bank_journal_id = bank_journals[0]['id']
print(f"  Using bank journal: {bank_journals[0]['name']} (ID: {bank_journal_id})")

# In Odoo 17+, bank transactions are created as account.bank.statement.line
# They are also accessible from the bank matching view
transactions = [
    # ── INCOMING (Customer Payments) ──
    {"date": TODAY, "payment_ref": "Payment for Professional Services - Tech Solutions",
     "partner_id": customer_ids["Tech Solutions Inc."], "amount": 1500.00,
     "note": "Matches $1,500 invoice - AUTO MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Software License Payment - Global Manufacturing",
     "partner_id": customer_ids["Global Manufacturing Co."], "amount": 500.00,
     "note": "Matches $500 invoice - AUTO MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Office Equipment Payment - Retail Stores",
     "partner_id": customer_ids["Retail Stores Group"], "amount": 1200.00,
     "note": "Matches $1,200 invoice - AUTO MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Training Services Payment - ABC Enterprises",
     "partner_id": customer_ids["ABC Enterprises"], "amount": 900.00,
     "note": "Matches $900 invoice - MANUAL MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Partial payment for Software License",
     "partner_id": customer_ids["Tech Solutions Inc."], "amount": 950.00,
     "note": "PARTIAL PAYMENT: $950 against $1,000 invoice ($50 short)"},
    
    {"date": TODAY, "payment_ref": "Maintenance Contract - bank fee deducted",
     "partner_id": customer_ids["Quick Buy Ltd"], "amount": 2350.00,
     "note": "BANK FEE DEDUCTED: $2,400 invoice minus $50 fee"},
    
    {"date": TODAY, "payment_ref": "Payment for multiple invoices - Tech Solutions",
     "partner_id": customer_ids["Tech Solutions Inc."], "amount": 600.00,
     "note": "MULTI-INVOICE: Should match two $300 invoices"},
    
    # ── OUTGOING (Vendor Payments) ──
    {"date": TODAY, "payment_ref": "Payment for office supplies",
     "partner_id": vendor_ids["Office Supplies Co."], "amount": -450.00,
     "note": "Matches $450 bill - AUTO MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Computer equipment purchase - Tech Hardware",
     "partner_id": vendor_ids["Tech Hardware Supplier"], "amount": -2400.00,
     "note": "Matches $2,400 bill - AUTO MATCH scenario"},
    
    {"date": TODAY, "payment_ref": "Cloud Services LLC - Monthly subscription",
     "partner_id": vendor_ids["Cloud Services LLC"], "amount": -49.99,
     "note": "RECURRING: Great for reconciliation model practice"},
    
    {"date": TODAY, "payment_ref": "Equipment rental plus convenience fee",
     "partner_id": vendor_ids["Equipment Rentals Inc."], "amount": -303.00,
     "note": "FEE SCENARIO: $300 bill + $3 convenience fee"},
    
    {"date": TODAY, "payment_ref": "Check #1001 - Raw Materials Supplier",
     "partner_id": vendor_ids["Raw Materials Supplier"], "amount": -1800.00,
     "note": "CHECK PAYMENT: Matches $1,800 bill"},
    
    # ── MISCELLANEOUS (Write-offs) ──
    {"date": TODAY, "payment_ref": "Monthly bank service fee",
     "partner_id": False, "amount": -15.00,
     "note": "WRITE-OFF: Practice Set Account to Bank Fees"},
    
    {"date": TODAY, "payment_ref": "Interest earned on account",
     "partner_id": False, "amount": 12.50,
     "note": "WRITE-OFF: Practice Set Account to Interest Income"},
    
    {"date": TODAY, "payment_ref": "Wire transfer fee - international",
     "partner_id": False, "amount": -35.00,
     "note": "WRITE-OFF: Practice Set Account to Bank Charges"},
    
    {"date": TODAY, "payment_ref": "Credit card processing fees",
     "partner_id": False, "amount": -8.75,
     "note": "WRITE-OFF: Practice Set Account to Processing Fees"},
    
    # ── SPECIAL SCENARIOS ──
    {"date": TODAY, "payment_ref": "Customer deposit for future order",
     "partner_id": customer_ids["Retail Stores Group"], "amount": 1500.00,
     "note": "OVERPAYMENT: No matching invoice - customer advance"},
    
    {"date": TODAY, "payment_ref": "Unknown deposit - needs investigation",
     "partner_id": False, "amount": 250.00,
     "note": "UNKNOWN: Practice Set Partner then reconcile"},
    
    {"date": TODAY, "payment_ref": "Refund from vendor for returned items",
     "partner_id": vendor_ids["Raw Materials Supplier"], "amount": 200.00,
     "note": "VENDOR REFUND: Credit from vendor"},
    
    {"date": TODAY, "payment_ref": "ATM cash withdrawal for petty cash",
     "partner_id": False, "amount": -500.00,
     "note": "CASH WITHDRAWAL: Practice Set Account to Petty Cash"},
]

txn_count = 0
for txn in transactions:
    try:
        vals = {
            'journal_id': bank_journal_id,
            'date': txn['date'],
            'payment_ref': txn['payment_ref'],
            'amount': txn['amount'],
        }
        if txn.get('partner_id'):
            vals['partner_id'] = txn['partner_id']
        
        txn_id = create('account.bank.statement.line', vals)
        txn_count += 1
        direction = "IN" if txn['amount'] > 0 else "OUT"
        print(f"  ✅ [{direction}] ${abs(txn['amount']):>10,.2f} | {txn['payment_ref'][:50]}")
        
    except Exception as e:
        print(f"  ❌ Error: {txn['payment_ref'][:40]} - {e}")

print(f"\n  📊 Total bank transactions created: {txn_count}")

# ──────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("🎉 SETUP COMPLETE!")
print("=" * 60)
print(f"""
Summary of created data:
─────────────────────────
  Customers:          5
  Vendors:            5
  Products:           10
  Sales Orders:       {len(invoice_ids)}
  Sales Invoices:     {len(invoice_ids)} (posted)
  Purchase Orders:    {len(bill_ids)}
  Vendor Bills:       {len(bill_ids)} (posted)
  Bank Transactions:  {txn_count}
  
─────────────────────────
PRACTICE SCENARIOS AVAILABLE:
─────────────────────────
  🟢 Easy (Auto-Match):     ~5 transactions
  🟡 Medium (Manual Match): ~5 transactions
  🔴 Advanced (Write-off):  ~4 transactions
  ⭐ Complex (Special):      ~6 transactions
  
─────────────────────────
NEXT STEPS:
─────────────────────────
  1. Go to: Accounting Dashboard
  2. Look for: "{txn_count} to reconcile" on Bank journal
  3. Click: Bank journal name to open Bank Matching view
  4. Start reconciling using the guide!
  
  Use: BANK_RECONCILIATION_COMPLETE_GUIDE.md for instructions
  Use: BANK_RECONCILIATION_QUICK_REFERENCE.md for quick lookup
""")
