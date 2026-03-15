import xmlrpc.client

URL = "https://psi-122test.odoo.com"
DB = "psi-122test"
USER = "georgey@psquareinterior.com"
PWD = "Psquare@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def x(model, domain, fields):
    return models.execute_kw(DB, uid, PWD, model, 'search_read', [domain], {'fields': fields})

# 1. Check if branch companies have warehouses
print("=" * 80)
print("WAREHOUSES PER COMPANY")
print("=" * 80)
companies = x('res.company', [], ['name', 'parent_id', 'child_ids'])
for c in companies:
    whs = x('stock.warehouse', [('company_id', '=', c['id'])], ['name', 'code'])
    print(f"\n  Company: {c['name']} (ID: {c['id']})")
    if whs:
        for w in whs:
            print(f"    Warehouse: {w['name']} ({w['code']})")
    else:
        print(f"    *** NO WAREHOUSES ***")

# 2. Check internal transit location
print("\n" + "=" * 80)
print("INTERNAL TRANSIT LOCATION PER COMPANY")
print("=" * 80)
companies_transit = x('res.company', [], ['name', 'internal_transit_location_id'])
for c in companies_transit:
    transit = c['internal_transit_location_id']
    print(f"  {c['name']}: {transit[1] if transit else 'NONE'}")

# 3. Check what stock locations exist for each company
print("\n" + "=" * 80)
print("KEY STOCK LOCATIONS PER COMPANY")
print("=" * 80)
for c in companies:
    locs = x('stock.location', [
        ('company_id', '=', c['id']),
        ('usage', 'in', ['internal', 'transit']),
    ], ['name', 'complete_name', 'usage', 'company_id'])
    print(f"\n  Company: {c['name']} (ID: {c['id']})")
    for loc in locs:
        print(f"    {loc['complete_name']} [{loc['usage']}]")

# 4. Check sale orders - can we see which company's warehouse is used
print("\n" + "=" * 80)
print("RECENT SALE ORDERS - Company vs Warehouse")
print("=" * 80)
sales = x('sale.order', [], ['name', 'company_id', 'warehouse_id', 'state'])
for s in sales[:10]:
    wh = s.get('warehouse_id')
    print(f"  {s['name']}: Company={s['company_id'][1]}, Warehouse={wh[1] if wh else 'N/A'}, State={s['state']}")

# 5. Check if Georgeon Furniture or PSQUARE INTERIOR have any transactions
print("\n" + "=" * 80)
print("TRANSACTIONS IN BRANCH COMPANIES")
print("=" * 80)
for cid, cname in [(11, 'Georgeon Furniture'), (12, 'PSQUARE INTERIOR')]:
    so_count = models.execute_kw(DB, uid, PWD, 'sale.order', 'search_count', [[('company_id', '=', cid)]])
    po_count = models.execute_kw(DB, uid, PWD, 'purchase.order', 'search_count', [[('company_id', '=', cid)]])
    inv_count = models.execute_kw(DB, uid, PWD, 'account.move', 'search_count', [[('company_id', '=', cid), ('move_type', '!=', 'entry')]])
    pick_count = models.execute_kw(DB, uid, PWD, 'stock.picking', 'search_count', [[('company_id', '=', cid)]])
    print(f"\n  {cname} (ID: {cid}):")
    print(f"    Sale Orders: {so_count}")
    print(f"    Purchase Orders: {po_count}")
    print(f"    Invoices/Bills: {inv_count}")
    print(f"    Stock Pickings: {pick_count}")

# 6. Check the 'child_ids' field label carefully
print("\n" + "=" * 80)
print("FIELD DEFINITION: child_ids on res.company")
print("=" * 80)
field_info = models.execute_kw(DB, uid, PWD, 'res.company', 'fields_get', [['child_ids']], {'attributes': ['string', 'type', 'help', 'relation']})
for fname, finfo in field_info.items():
    print(f"  Field Name: {fname}")
    print(f"  Label: {finfo['string']}")
    print(f"  Type: {finfo['type']}")
    print(f"  Relation: {finfo.get('relation', 'N/A')}")
    print(f"  Help: {finfo.get('help', 'N/A')}")

# 7. Check if branches share the same Chart of Accounts / GSTIN
print("\n" + "=" * 80)  
print("GSTIN / VAT COMPARISON")
print("=" * 80)
companies_vat = x('res.company', [], ['name', 'vat', 'parent_id', 'currency_id', 'chart_template'])
for c in companies_vat:
    parent = c['parent_id'][1] if c['parent_id'] else "ROOT"
    print(f"  {c['name']}: VAT={c.get('vat','N/A')}, Parent={parent}, Currency={c['currency_id'][1] if c['currency_id'] else 'N/A'}")
