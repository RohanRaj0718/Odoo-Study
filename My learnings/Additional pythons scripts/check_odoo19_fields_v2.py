"""Find the correct field names for stock.picking and product type in Odoo 19."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def fg(model, fields=None):
    kw = {'attributes': ['string', 'type', 'relation']}
    if fields:
        return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', fields, kw)
    return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], kw)

# 1. Find the correct move_ids field on stock.picking
print("=== stock.picking fields containing 'move' ===")
pick_fields = fg('stock.picking')
for k, v in sorted(pick_fields.items()):
    if 'move' in k.lower():
        print(f"  {k:40s} | {v['string']:30s} | {v['type']:12s} | rel: {v.get('relation', '')}")

# 2. Find product tracking fields
print("\n=== product.product fields for type/tracking ===")
prod_fields = fg('product.product')
for k, v in sorted(prod_fields.items()):
    if any(x in k.lower() for x in ['type', 'storable', 'track', 'is_']):
        print(f"  {k:40s} | {v['string']:30s} | {v['type']:12s}")

# 3. Check an existing product that HAS stock (001GREY@1560)
from xmlrpc.client import MAXINT
print("\n=== Existing product with stock ===")
existing = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'search_read',
    [[['name', 'ilike', '001GREY']]],
    {'fields': ['name', 'type', 'categ_id'], 'limit': 1})
if existing:
    print(f"  Name: {existing[0]['name']}")
    print(f"  Type: {existing[0]['type']}")
    print(f"  Category: {existing[0]['categ_id']}")
    
    # check its quants
    quants = models.execute_kw(DB, uid, PASSWORD, 'stock.quant', 'search_read',
        [[['product_id', '=', existing[0]['id']]]],
        {'fields': ['product_id', 'location_id', 'quantity'], 'limit': 5})
    print(f"  Quants: {len(quants)}")
    for q in quants:
        print(f"    Loc: {q['location_id'][1]} | Qty: {q['quantity']}")

# 4. What type does this product use?
print(f"\n  Product type = '{existing[0]['type']}' — This is a product WITH stock/quants")

# 5. Check our test products
print("\n=== Test products ===")
test_prods = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'search_read',
    [[['name', 'ilike', 'ZZ-TEST']]],
    {'fields': ['name', 'type', 'categ_id'], 'limit': 10})
for p in test_prods:
    print(f"  {p['name']:35s} | type: {p['type']:8s} | cat: {p['categ_id']}")

# 6. Check stock.move fields for the correct one
print("\n=== stock.move fields ===")
move_fields = fg('stock.move')
for k, v in sorted(move_fields.items()):
    if any(x in k.lower() for x in ['picking', 'product_uom_qty', 'quantity', 'location']):
        print(f"  {k:40s} | {v['string']:30s} | {v['type']:12s}")
