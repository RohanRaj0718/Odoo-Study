import xmlrpc.client
import csv
import sys

url = "https://psquare-interior.odoo.com"
db = "psquare-interior"
username = "georgey@psquareinterior.com"
password = "Psquare@1"

def export_products():
    print("Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed.")
        return

    print(f"Authenticated successfully. User ID: {uid}")
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # 1. Get all fields for product.product (or product.template)
    print("Fetching all fields for product.template...")
    fields_info = models.execute_kw(db, uid, password, 'product.template', 'fields_get', [], {'attributes': ['string', 'help', 'type']})
    field_names = list(fields_info.keys())
    print(f"Found {len(field_names)} fields.")

    # 2. Search all products
    print("Searching for products...")
    product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
    print(f"Found {len(product_ids)} products.")

    # 3. Read all data
    print("Reading data...")
    # Read in batches of 1000 to avoid memory/timeout issues
    batch_size = 1000
    all_products = []
    for i in range(0, len(product_ids), batch_size):
        batch_ids = product_ids[i:i+batch_size]
        print(f"  Reading batch {i} to {i+len(batch_ids)}...")
        records = models.execute_kw(db, uid, password, 'product.template', 'read', [batch_ids], {'fields': field_names})
        all_products.extend(records)

    # 4. Write to CSV
    filename = 'C:\\Odoo Study\\psquare_products_full_export.csv'
    print(f"Writing to {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for p in all_products:
            row = {}
            for f in field_names:
                val = p.get(f)
                if isinstance(val, list):
                    val = str(val)
                row[f] = val
            writer.writerow(row)
            
    print("Export complete!")

if __name__ == "__main__":
    try:
        export_products()
    except Exception as e:
        print(f"Error: {e}")
