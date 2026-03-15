"""
Create complete demo data across all branches:
- Sales Orders (some confirmed, some draft)
- Purchase Orders (some confirmed, some draft)  
- Invoices from confirmed SOs (some paid, some unpaid)
- Bills from confirmed POs (some paid, some unpaid)
- Leave clean partners for live demo

CLEAN CUSTOMERS (keep clean for live demo):
  - Mohammed Ashraf Interiors (ID=56)
  - Priya Thomas (ID=52)

CLEAN VENDORS (keep clean for live demo):  
  - Decor World Imports (ID=66)
  - Godrej Interio Distributor Kerala (ID=67)
  - Nizar Hardware & Tools (ID=65)
"""
import xmlrpc.client
import time

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

def action(model, method, ids):
    try:
        result = models.execute_kw(DB, uid, PASSWORD, model, method, [ids])
        return result
    except Exception as e:
        if "cannot marshal None" in str(e):
            return True  # Action succeeded but returned None
        raise

def sr(model, domain, fields, limit=10):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# ── Partner IDs ──
RAJAN_PILLAI = 57
MOHAMMED_ASHRAF = 56  # KEEP CLEAN
PRIYA_THOMAS = 52     # KEEP CLEAN
GREEN_VALLEY = 54
LAKSHMI_DEVI = 55
SKYLINE = 58
ANOOP = 50
DEEPA = 59
SURESH = 51
VARGHESE = 53

# Vendors
COCHIN_LAMINATE = 64
KERALA_BLINDS = 60
MALABAR = 62
SOUTHERN_MATTRESS = 63
TRAVANCORE_WOOD = 61
DECOR_WORLD = 66       # KEEP CLEAN
GODREJ = 67            # KEEP CLEAN
NIZAR = 65             # KEEP CLEAN

# ── Company/Journal IDs ──
KG = 1      # Krishnadas Group (parent)
DEVIKA = 2  # Devika Furniture (branch)
KDESIGN = 3 # KDESIGN INTERIOR (branch)
KFURN = 4   # KDESIGN INTERIOR FURNISHING (standalone)

BANK_KG = 12      # Bank Yes 0024
BANK_DEVIKA = 30   # Bank Devika 4501
BANK_KDESIGN = 36  # Bank KDESIGN 7802
BANK_KFURN = 21    # Bank

# ── Products (real products from the DB) ──
# ID=18: Carolina Lithgow Black Recliner @ 24000 (sale) / 15000 (cost)
# ID=17: Las Vegas Recliner Ivory @ 39000 / 24000
# ID=27: Built-in Chimney 60cm @ 18500 / 12000
# ID=28: Built-in Hob 4 Burner @ 14500 / 9500
# ID=49: BLDC Designer Ceiling Fan @ 8500 / 5200
# ID=53: Canvas Abstract Wall Art @ 2500 / 1200
# ID=50: Ceramic Indoor Pot Large @ 650 / 320
# ID=43: Blackout Lining Fabric @ 280 / 140
# ID=29: 3D Wallpaper Premium Floral @ 450 / 220
# ID=7:  Roller Blind Clutch With Chain @ 350 / 180
# ID=2:  Atlantic Classic Bedsheet @ 2499 / 1500
# ID=13: Somfy Track @ 4500 / 2800
# ID=1:  Booking Fees @ 50 (service)

print("=" * 70)
print("CREATING DEMO DATA ACROSS ALL BRANCHES")
print("=" * 70)

# ════════════════════════════════════════════════════════════════
# SALE ORDERS
# ════════════════════════════════════════════════════════════════
print("\n--- SALE ORDERS ---")

sale_orders = [
    # ── Krishnadas Group SOs ──
    {
        'partner_id': RAJAN_PILLAI,
        'company_id': KG,
        'lines': [
            {'product_id': 18, 'product_uom_qty': 1, 'price_unit': 24000, 'name': '1/9097 Carolina Lithgow Black Recliner'},
            {'product_id': 49, 'product_uom_qty': 2, 'price_unit': 8500, 'name': 'BLDC Designer Ceiling Fan 48inch'},
        ],
        'confirm': True,
        'invoice': True,
        'pay': True,
        'pay_amount': 41000,
        'journal_id': BANK_KG,
        'label': 'KG: Rajan Pillai - Recliner+Fan [CONFIRM+INVOICE+PAY]'
    },
    {
        'partner_id': GREEN_VALLEY,
        'company_id': KG,
        'lines': [
            {'product_id': 27, 'product_uom_qty': 3, 'price_unit': 18500, 'name': 'Built-in Chimney 60cm Auto Clean'},
            {'product_id': 28, 'product_uom_qty': 3, 'price_unit': 14500, 'name': 'Built-in Hob 4 Burner SS'},
        ],
        'confirm': True,
        'invoice': False,
        'pay': False,
        'label': 'KG: Green Valley - Chimney+Hob [CONFIRM ONLY - no invoice]'
    },

    # ── Devika Furniture SOs ──
    {
        'partner_id': RAJAN_PILLAI,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 2, 'product_uom_qty': 10, 'price_unit': 2499, 'name': 'Atlantic Classic Bedsheet'},
            {'product_id': 43, 'product_uom_qty': 20, 'price_unit': 280, 'name': 'Blackout Lining Fabric 48inch'},
        ],
        'confirm': True,
        'invoice': True,
        'pay': False,
        'label': 'Devika: Rajan Pillai - Bedsheets+Fabric [CONFIRM+INVOICE, NO PAY]'
    },
    {
        'partner_id': VARGHESE,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 17, 'product_uom_qty': 2, 'price_unit': 39000, 'name': 'Las Vegas Recliner Ivory'},
            {'product_id': 53, 'product_uom_qty': 5, 'price_unit': 2500, 'name': 'Canvas Abstract Wall Art 24x36'},
        ],
        'confirm': True,
        'invoice': True,
        'pay': True,
        'pay_amount': 50000,
        'journal_id': BANK_DEVIKA,
        'label': 'Devika: Varghese - Recliner+Art [CONFIRM+INVOICE+PARTIAL PAY]'
    },
    {
        'partner_id': ANOOP,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 29, 'product_uom_qty': 50, 'price_unit': 450, 'name': '3D Wallpaper Premium Floral'},
        ],
        'confirm': False,
        'invoice': False,
        'pay': False,
        'label': 'Devika: Anoop - Wallpaper [DRAFT only]'
    },

    # ── KDESIGN INTERIOR SOs ──
    {
        'partner_id': RAJAN_PILLAI,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 13, 'product_uom_qty': 4, 'price_unit': 4500, 'name': 'Somfy Track'},
            {'product_id': 7, 'product_uom_qty': 10, 'price_unit': 350, 'name': 'Roller Blind Clutch With Chain'},
        ],
        'confirm': True,
        'invoice': True,
        'pay': True,
        'pay_amount': 21500,
        'journal_id': BANK_KDESIGN,
        'label': 'KDESIGN: Rajan Pillai - Track+Blind [CONFIRM+INVOICE+FULL PAY]'
    },
    {
        'partner_id': LAKSHMI_DEVI,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 50, 'product_uom_qty': 15, 'price_unit': 650, 'name': 'Ceramic Indoor Pot Large'},
            {'product_id': 29, 'product_uom_qty': 30, 'price_unit': 450, 'name': '3D Wallpaper Premium Floral'},
        ],
        'confirm': True,
        'invoice': False,
        'pay': False,
        'label': 'KDESIGN: Lakshmi Devi - Pots+Wallpaper [CONFIRM ONLY]'
    },

    # ── KDESIGN INTERIOR FURNISHING SOs ──
    {
        'partner_id': VARGHESE,
        'company_id': KFURN,
        'lines': [
            {'product_id': 27, 'product_uom_qty': 2, 'price_unit': 18500, 'name': 'Built-in Chimney 60cm Auto Clean'},
            {'product_id': 28, 'product_uom_qty': 2, 'price_unit': 14500, 'name': 'Built-in Hob 4 Burner SS'},
        ],
        'confirm': True,
        'invoice': True,
        'pay': False,
        'label': 'KFURN: Varghese - Chimney+Hob [CONFIRM+INVOICE, NO PAY]'  
    },
    {
        'partner_id': DEEPA,
        'company_id': KFURN,
        'lines': [
            {'product_id': 49, 'product_uom_qty': 3, 'price_unit': 8500, 'name': 'BLDC Designer Ceiling Fan 48inch'},
        ],
        'confirm': False,
        'invoice': False,
        'pay': False,
        'label': 'KFURN: Deepa - Fan [DRAFT only]'
    },
]

# ════════════════════════════════════════════════════════════════
# PURCHASE ORDERS  
# ════════════════════════════════════════════════════════════════
print("\n--- PURCHASE ORDERS ---")

purchase_orders = [
    # ── Krishnadas Group POs ──
    {
        'partner_id': SOUTHERN_MATTRESS,
        'company_id': KG,
        'lines': [
            {'product_id': 18, 'product_uom_qty': 5, 'price_unit': 15000, 'name': '1/9097 Carolina Lithgow Black Recliner'},
        ],
        'confirm': True,
        'bill': True,
        'pay': True,
        'pay_amount': 75000,
        'journal_id': BANK_KG,
        'label': 'KG: Southern Mattress - Recliners [CONFIRM+BILL+FULL PAY]'
    },
    {
        'partner_id': TRAVANCORE_WOOD,
        'company_id': KG,
        'lines': [
            {'product_id': 27, 'product_uom_qty': 10, 'price_unit': 12000, 'name': 'Built-in Chimney 60cm'},
        ],
        'confirm': True,
        'bill': False,
        'pay': False,
        'label': 'KG: Travancore Wood - Chimney [CONFIRM ONLY - no bill]'
    },

    # ── Devika Furniture POs ──
    {
        'partner_id': COCHIN_LAMINATE,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 2, 'product_uom_qty': 50, 'price_unit': 1500, 'name': 'Atlantic Classic Bedsheet'},
            {'product_id': 43, 'product_uom_qty': 100, 'price_unit': 140, 'name': 'Blackout Lining Fabric 48inch'},
        ],
        'confirm': True,
        'bill': True,
        'pay': False,
        'label': 'Devika: Cochin Laminate - Bedsheets+Fabric [CONFIRM+BILL, NO PAY]'
    },
    {
        'partner_id': SOUTHERN_MATTRESS,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 17, 'product_uom_qty': 3, 'price_unit': 24000, 'name': 'Las Vegas Recliner Ivory'},
        ],
        'confirm': True,
        'bill': True,
        'pay': True,
        'pay_amount': 72000,
        'journal_id': BANK_DEVIKA,
        'label': 'Devika: Southern Mattress - Recliners [CONFIRM+BILL+FULL PAY]'
    },
    {
        'partner_id': TRAVANCORE_WOOD,
        'company_id': DEVIKA,
        'lines': [
            {'product_id': 53, 'product_uom_qty': 20, 'price_unit': 1200, 'name': 'Canvas Abstract Wall Art'},
        ],
        'confirm': False,
        'bill': False,
        'pay': False,
        'label': 'Devika: Travancore Wood - Wall Art [DRAFT only]'
    },

    # ── KDESIGN INTERIOR POs ──
    {
        'partner_id': MALABAR,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 13, 'product_uom_qty': 10, 'price_unit': 2800, 'name': 'Somfy Track'},
            {'product_id': 7, 'product_uom_qty': 50, 'price_unit': 180, 'name': 'Roller Blind Clutch'},
        ],
        'confirm': True,
        'bill': True,
        'pay': True,
        'pay_amount': 37000,
        'journal_id': BANK_KDESIGN,
        'label': 'KDESIGN: Malabar - Track+Clutch [CONFIRM+BILL+FULL PAY]'
    },
    {
        'partner_id': SOUTHERN_MATTRESS,
        'company_id': KDESIGN,
        'lines': [
            {'product_id': 50, 'product_uom_qty': 100, 'price_unit': 320, 'name': 'Ceramic Indoor Pot Large'},
        ],
        'confirm': True,
        'bill': False,
        'pay': False,
        'label': 'KDESIGN: Southern Mattress - Pots [CONFIRM ONLY]'
    },

    # ── KDESIGN INTERIOR FURNISHING POs ──
    {
        'partner_id': COCHIN_LAMINATE,
        'company_id': KFURN,
        'lines': [
            {'product_id': 28, 'product_uom_qty': 5, 'price_unit': 9500, 'name': 'Built-in Hob 4 Burner SS'},
        ],
        'confirm': True,
        'bill': True,
        'pay': False,
        'label': 'KFURN: Cochin Laminate - Hobs [CONFIRM+BILL, NO PAY]'
    },
    {
        'partner_id': MALABAR,
        'company_id': KFURN,
        'lines': [
            {'product_id': 49, 'product_uom_qty': 10, 'price_unit': 5200, 'name': 'BLDC Designer Ceiling Fan'},
        ],
        'confirm': False,
        'bill': False,
        'pay': False,
        'label': 'KFURN: Malabar - Fans [DRAFT only]'
    },
]


# ════════════════════════════════════════════════════════════════
# EXECUTE: Create Sale Orders
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CREATING SALE ORDERS")
print("=" * 70)

for i, so in enumerate(sale_orders):
    print(f"\n[SO {i+1}] {so['label']}")
    try:
        # Create SO
        so_id = create('sale.order', {
            'partner_id': so['partner_id'],
            'company_id': so['company_id'],
        })
        print(f"  Created SO ID: {so_id}")

        # Add lines
        for line in so['lines']:
            line_id = create('sale.order.line', {
                'order_id': so_id,
                'product_id': line['product_id'],
                'product_uom_qty': line['product_uom_qty'],
                'price_unit': line['price_unit'],
                'name': line['name'],
            })
            print(f"  Added line: {line['name']} x{line['product_uom_qty']} @ {line['price_unit']}")

        # Confirm
        if so['confirm']:
            action('sale.order', 'action_confirm', [so_id])
            print(f"  CONFIRMED")

            # Create invoice
            if so['invoice']:
                try:
                    inv_result = action('sale.order', '_create_invoices', [so_id])
                    print(f"  Invoice created (result type: {type(inv_result).__name__})")
                    
                    # Find the invoice
                    time.sleep(0.5)
                    invoices = sr('account.move', [
                        ['partner_id', '=', so['partner_id']],
                        ['company_id', '=', so['company_id']],
                        ['move_type', '=', 'out_invoice'],
                        ['state', '=', 'draft']
                    ], ['name', 'amount_total', 'state'], limit=1)
                    
                    if invoices:
                        inv_id = invoices[0]['id']
                        inv_total = invoices[0]['amount_total']
                        # Post the invoice
                        action('account.move', 'action_post', [inv_id])
                        print(f"  Invoice POSTED: {invoices[0]['name']} | Total: {inv_total}")
                        
                        # Pay if needed
                        if so['pay']:
                            pay_id = create('account.payment', {
                                'payment_type': 'inbound',
                                'partner_type': 'customer',
                                'partner_id': so['partner_id'],
                                'amount': so['pay_amount'],
                                'journal_id': so['journal_id'],
                                'company_id': so['company_id'],
                                'date': '2026-03-03',
                            })
                            action('account.payment', 'action_post', [pay_id])
                            print(f"  Payment POSTED: {so['pay_amount']}")
                    else:
                        print(f"  WARNING: Could not find draft invoice to post")
                        
                except Exception as e:
                    print(f"  Invoice creation error: {e}")
        else:
            print(f"  Left as DRAFT")

    except Exception as e:
        print(f"  ERROR: {e}")


# ════════════════════════════════════════════════════════════════
# EXECUTE: Create Purchase Orders
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("CREATING PURCHASE ORDERS")
print("=" * 70)

for i, po in enumerate(purchase_orders):
    print(f"\n[PO {i+1}] {po['label']}")
    try:
        # Create PO
        po_id = create('purchase.order', {
            'partner_id': po['partner_id'],
            'company_id': po['company_id'],
        })
        print(f"  Created PO ID: {po_id}")

        # Add lines
        for line in po['lines']:
            line_id = create('purchase.order.line', {
                'order_id': po_id,
                'product_id': line['product_id'],
                'product_qty': line['product_uom_qty'],
                'price_unit': line['price_unit'],
                'name': line['name'],
            })
            print(f"  Added line: {line['name']} x{line['product_uom_qty']} @ {line['price_unit']}")

        # Confirm
        if po['confirm']:
            action('purchase.order', 'button_confirm', [po_id])
            print(f"  CONFIRMED")

            # Create bill
            if po['bill']:
                try:
                    # For POs, we create vendor bill manually
                    bill_vals = {
                        'partner_id': po['partner_id'],
                        'company_id': po['company_id'],
                        'move_type': 'in_invoice',
                        'invoice_date': '2026-03-03',
                    }
                    bill_id = create('account.move', bill_vals)
                    
                    # Add lines from PO lines
                    for line in po['lines']:
                        create('account.move.line', {
                            'move_id': bill_id,
                            'product_id': line['product_id'],
                            'quantity': line['product_uom_qty'],
                            'price_unit': line['price_unit'],
                            'name': line['name'],
                        })
                    
                    # Post bill
                    action('account.move', 'action_post', [bill_id])
                    
                    bills = sr('account.move', [['id', '=', bill_id]], ['name', 'amount_total'])
                    bill_name = bills[0]['name'] if bills else '?'
                    bill_total = bills[0]['amount_total'] if bills else 0
                    print(f"  Bill POSTED: {bill_name} | Total: {bill_total}")
                    
                    # Pay if needed
                    if po['pay']:
                        pay_id = create('account.payment', {
                            'payment_type': 'outbound',
                            'partner_type': 'supplier',
                            'partner_id': po['partner_id'],
                            'amount': po['pay_amount'],
                            'journal_id': po['journal_id'],
                            'company_id': po['company_id'],
                            'date': '2026-03-03',
                        })
                        action('account.payment', 'action_post', [pay_id])
                        print(f"  Payment POSTED: {po['pay_amount']}")
                        
                except Exception as e:
                    print(f"  Bill creation error: {e}")
        else:
            print(f"  Left as DRAFT")

    except Exception as e:
        print(f"  ERROR: {e}")


# ════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

companies = sr('res.company', [], ['name'], limit=10)
for c in companies:
    cid = c['id']
    so_count = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid]]])
    so_confirmed = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'sale']]])
    so_draft = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    po_count = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid]]])
    po_confirmed = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'purchase']]])
    po_draft = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['company_id', '=', cid], ['state', '=', 'draft']]])
    inv_count = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'out_invoice']]])
    bill_count = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['company_id', '=', cid], ['move_type', '=', 'in_invoice']]])
    pay_count = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['company_id', '=', cid]]])
    
    print(f"\n{c['name']}:")
    print(f"  Sale Orders: {so_count} total ({so_confirmed} confirmed, {so_draft} draft)")
    print(f"  Purchase Orders: {po_count} total ({po_confirmed} confirmed, {po_draft} draft)")
    print(f"  Invoices: {inv_count}")
    print(f"  Bills: {bill_count}")
    print(f"  Payments: {pay_count}")

print("\n--- CLEAN PARTNERS (kept untouched for live demo) ---")
clean_custs = [('Mohammed Ashraf Interiors', 56), ('Priya Thomas', 52)]
clean_vends = [('Decor World Imports', 66), ('Godrej Interio Distributor Kerala', 67), ('Nizar Hardware & Tools', 65)]

for name, pid in clean_custs:
    inv = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['partner_id', '=', pid], ['move_type', '=', 'out_invoice']]])
    so = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[['partner_id', '=', pid]]])
    pay = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['partner_id', '=', pid]]])
    print(f"  CUSTOMER: {name} — SO={so}, INV={inv}, PAY={pay}")

for name, pid in clean_vends:
    bill = models.execute_kw(DB, uid, PASSWORD, 'account.move', 'search_count', [[['partner_id', '=', pid], ['move_type', '=', 'in_invoice']]])
    po = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[['partner_id', '=', pid]]])
    pay = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', [[['partner_id', '=', pid]]])
    print(f"  VENDOR: {name} — PO={po}, BILL={bill}, PAY={pay}")

print("\n=== ALL DONE ===")
