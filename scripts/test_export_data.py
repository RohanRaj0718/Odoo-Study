import xmlrpc.client

url = "https://psquare-interior.odoo.com"
db = "psquare-interior"
username = "georgey@psquareinterior.com"
password = "Psquare@1"

def test_export():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Fetch 5 product IDs
    product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]], {'limit': 5})
    
    # Try exporting native UI style
    fields_to_export = [
        'id',               # External ID
        'name',
        'default_code',
        'categ_id/id',      # Category External ID
        'taxes_id/id',      # Taxes External IDs
        'supplier_taxes_id/id'
    ]
    
    result = models.execute_kw(db, uid, password, 'product.template', 'export_data', [product_ids, fields_to_export])
    print(result)

if __name__ == "__main__":
    test_export()
