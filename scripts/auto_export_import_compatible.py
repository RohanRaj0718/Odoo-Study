import xmlrpc.client
import csv

url = "https://psquare-interior.odoo.com"
db = "psquare-interior"
username = "georgey@psquareinterior.com"
password = "Psquare@1"

def export_import_compatible_products():
    print("Connecting to Odoo...")
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # 1. Get all fields dynamically
    print("Fetching product fields...")
    fields_info = models.execute_kw(db, uid, password, 'product.template', 'fields_get', [], {'attributes': ['type', 'store', 'readonly']})
    
    export_fields = ['id'] # Always include External ID first
    
    for field_name, attributes in fields_info.items():
        # Skip pure readonly or non-stored fields (they can't be imported anyway)
        if attributes.get('readonly') or not attributes.get('store'):
            continue
            
        field_type = attributes.get('type')
        if field_type in ['many2one', 'many2many']:
            # For relationships, export the External ID, which is import-compatible
            export_fields.append(f"{field_name}/id")
        elif field_type not in ['one2many', 'binary']: 
            export_fields.append(field_name)

    print(f"Prepared {len(export_fields)} import-compatible fields for export.")

    # 2. Get all product IDs
    print("Searching for products...")
    product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
    print(f"Found {len(product_ids)} products.")

    # 3. Use Odoo's native export_data endpoint
    print("Downloading data via export_data...")
    batch_size = 500
    all_rows = []
    
    for i in range(0, len(product_ids), batch_size):
        batch_ids = product_ids[i:i+batch_size]
        print(f"  Downloading batch {i} to {i+len(batch_ids)}...")
        result = models.execute_kw(db, uid, password, 'product.template', 'export_data', [batch_ids, export_fields])
        all_rows.extend(result.get('datas', []))

    # 4. Write to CSV
    filename = 'C:\\Odoo Study\\psquare_products_import_compatible.csv'
    print(f"Writing to {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(export_fields)
        # Write data
        writer.writerows(all_rows)
            
    print("Export complete!")

if __name__ == "__main__":
    export_import_compatible_products()
