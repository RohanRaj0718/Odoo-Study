"""Read back the S00055 sales order to verify discount visibility."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

def sr(model, domain=[], fields=[], limit=10):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read',
                             [domain], {'fields': fields, 'limit': limit})

# Read back the order line for SO ID=55
print("=== ORDER LINE for S00055 (ID=55) ===")
lines = sr('sale.order.line', [('order_id', '=', 55)], [
    'product_id', 'name', 'product_uom_qty', 'price_unit',
    'discount', 'price_subtotal', 'price_total'
], 5)

for l in lines:
    pid = l['product_id']
    print(f"  Product: {pid}")
    print(f"  Quantity: {l['product_uom_qty']}")
    print(f"  Unit Price: {l['price_unit']}")
    print(f"  Discount: {l['discount']}%")
    print(f"  Subtotal: {l['price_subtotal']}")
    print(f"  Total (with tax): {l['price_total']}")

print()
print("=== ANALYSIS ===")
print("  Original Bedroom Mat price: 500.0")
if lines:
    l = lines[0]
    if l['discount'] > 0:
        print(f"  RESULT: Discount IS visible at {l['discount']}%")
        print(f"  Unit price kept at {l['price_unit']}, discount shown separately")
    elif l['price_unit'] < 500:
        print(f"  RESULT: Discount is HIDDEN. Price silently reduced to {l['price_unit']}")
    else:
        print(f"  RESULT: No discount applied")

# Also read the SO summary
so = sr('sale.order', [('id', '=', 55)], ['name', 'amount_untaxed', 'amount_tax', 'amount_total'], 1)[0]
print(f"  SO {so['name']}: untaxed={so['amount_untaxed']}, tax={so['amount_tax']}, total={so['amount_total']}")
print(f"  Expected: 500 x 3 = 1500, minus 15% = 1275")
print(f"  URL: {URL}/odoo/sales/55")
