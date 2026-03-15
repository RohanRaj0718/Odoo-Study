"""
Audit: Which customers/vendors are clean (no transactions) vs already used.
Also check products, sale.order and purchase.order modules availability.
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=200, order=None):
    kw = {'fields': fields, 'limit': limit}
    if order:
        kw['order'] = order
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

def cnt(model, domain=[]):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])

# ============================================================
# 1. All customers with transaction counts
# ============================================================
print("=" * 70)
print("CUSTOMERS — Transaction Status")
print("=" * 70)
customers = sr('res.partner', [['customer_rank', '>', 0]], ['name', 'id', 'company_id', 'vat'])
for c in customers:
    inv_count = cnt('account.move', [['partner_id', '=', c['id']], ['move_type', '=', 'out_invoice']])
    pay_count = cnt('account.payment', [['partner_id', '=', c['id']], ['payment_type', '=', 'inbound']])
    so_count = cnt('sale.order', [['partner_id', '=', c['id']]])
    status = "CLEAN" if (inv_count == 0 and pay_count == 0 and so_count == 0) else "HAS DATA"
    cname = c.get('company_id', [False, 'All'])
    cname = cname[1] if isinstance(cname, list) else 'All'
    print(f"  [{status:8}] ID={c['id']:3} | {c['name']:<35} | INV={inv_count} PAY={pay_count} SO={so_count} | Company: {cname}")

# ============================================================
# 2. All vendors with transaction counts
# ============================================================
print("\n" + "=" * 70)
print("VENDORS — Transaction Status")
print("=" * 70)
vendors = sr('res.partner', [['supplier_rank', '>', 0]], ['name', 'id', 'company_id', 'vat'])
for v in vendors:
    bill_count = cnt('account.move', [['partner_id', '=', v['id']], ['move_type', '=', 'in_invoice']])
    pay_count = cnt('account.payment', [['partner_id', '=', v['id']], ['payment_type', '=', 'outbound']])
    po_count = cnt('purchase.order', [['partner_id', '=', v['id']]])
    status = "CLEAN" if (bill_count == 0 and pay_count == 0 and po_count == 0) else "HAS DATA"
    cname = v.get('company_id', [False, 'All'])
    cname = cname[1] if isinstance(cname, list) else 'All'
    print(f"  [{status:8}] ID={v['id']:3} | {v['name']:<40} | BILL={bill_count} PAY={pay_count} PO={po_count} | Company: {cname}")

# ============================================================
# 3. Products available
# ============================================================
print("\n" + "=" * 70)
print("PRODUCTS")
print("=" * 70)
products = sr('product.product', [['sale_ok', '=', True]], ['name', 'list_price', 'standard_price', 'taxes_id', 'type', 'company_id'], limit=30)
for p in products:
    cid = p.get('company_id')
    cname = cid[1] if cid and isinstance(cid, list) else 'All'
    ptype = p.get('type', '')
    print(f"  ID={p['id']:3} | {p['name']:<40} | Sale: {p.get('list_price',0):>10} | Cost: {p.get('standard_price',0):>10} | Tax IDs: {p.get('taxes_id',[])} | Type: {ptype} | Co: {cname}")

# Also check purchasable products
print("\n--- Purchasable Products ---")
purch = sr('product.product', [['purchase_ok', '=', True]], ['name', 'list_price', 'standard_price', 'supplier_taxes_id', 'type'], limit=30)
for p in purch:
    print(f"  ID={p['id']:3} | {p['name']:<40} | Cost: {p.get('standard_price',0):>10} | Vendor Tax IDs: {p.get('supplier_taxes_id',[])} | Type: {p.get('type','')}")

# ============================================================
# 4. Check existing SOs and POs
# ============================================================
print("\n" + "=" * 70)
print("EXISTING SALE ORDERS")
print("=" * 70)
sos = sr('sale.order', [], ['name', 'partner_id', 'company_id', 'state', 'amount_total'], limit=30, order='company_id, name')
if sos:
    for s in sos:
        cname = s['company_id'][1] if s.get('company_id') else '?'
        pname = s['partner_id'][1] if s.get('partner_id') else '?'
        print(f"  {s['name']} | {pname} | {cname} | State: {s['state']} | Total: {s['amount_total']}")
else:
    print("  No sale orders found")

print("\n" + "=" * 70)
print("EXISTING PURCHASE ORDERS")
print("=" * 70)
pos = sr('purchase.order', [], ['name', 'partner_id', 'company_id', 'state', 'amount_total'], limit=30, order='company_id, name')
if pos:
    for p in pos:
        cname = p['company_id'][1] if p.get('company_id') else '?'
        pname = p['partner_id'][1] if p.get('partner_id') else '?'
        print(f"  {p['name']} | {pname} | {cname} | State: {p['state']} | Total: {p['amount_total']}")
else:
    print("  No purchase orders found")

# ============================================================
# 5. Check sale.order.line and purchase.order.line fields
# ============================================================
print("\n" + "=" * 70)
print("SALE ORDER LINE FIELDS")
print("=" * 70)
try:
    so_fields = models.execute_kw(DB, uid, PASSWORD, 'sale.order.line', 'fields_get', [], {'attributes': ['string', 'type', 'required']})
    important = ['product_id', 'product_uom_qty', 'price_unit', 'tax_id', 'name', 'order_id', 'product_uom']
    for f in important:
        if f in so_fields:
            print(f"  {f}: {so_fields[f]['string']} | type={so_fields[f]['type']} | required={so_fields[f].get('required', False)}")
except Exception as e:
    print(f"  Error: {e}")

print("\n--- Purchase Order Line Fields ---")
try:
    po_fields = models.execute_kw(DB, uid, PASSWORD, 'purchase.order.line', 'fields_get', [], {'attributes': ['string', 'type', 'required']})
    important = ['product_id', 'product_qty', 'price_unit', 'taxes_id', 'name', 'order_id', 'product_uom', 'date_planned']
    for f in important:
        if f in po_fields:
            print(f"  {f}: {po_fields[f]['string']} | type={po_fields[f]['type']} | required={po_fields[f].get('required', False)}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
# 6. Check UoM
# ============================================================
print("\n--- Units of Measure ---")
uoms = sr('uom.uom', [['name', 'in', ['Units', 'Unit(s)', 'pcs', 'Nos']]], ['name', 'id'])
if not uoms:
    uoms = sr('uom.uom', [], ['name', 'id'], limit=5)
for u in uoms:
    print(f"  ID={u['id']} | {u['name']}")

print("\n=== DONE ===")
