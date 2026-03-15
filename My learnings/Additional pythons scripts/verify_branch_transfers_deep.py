"""
Deep verification:
1. Can we do an internal transfer between parent WH and branch WH?
2. Do branches truly need separate journals or can they use parent's?
3. What EXACTLY does Odoo share between parent and child (branch)?
"""
import xmlrpc.client

URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def x(model, method, *a, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *a, **kw)

# ═══════════════════════════════════════════════════════════
print("=" * 70)
print("1. COMPANY STRUCTURE REMINDER")
print("=" * 70)
companies = x('res.company', 'search_read', [[]], {'fields': ['name', 'parent_id', 'child_ids']})
for c in sorted(companies, key=lambda x: x['id']):
    role = "BRANCH (child)" if c['parent_id'] else "ROOT"
    parent = f" → parent: {c['parent_id'][1]}" if c['parent_id'] else ""
    print(f"  ID {c['id']:>2}: {c['name']} [{role}]{parent}")

warehouses = x('stock.warehouse', 'search_read', [[]], {'fields': ['name', 'code', 'company_id', 'lot_stock_id']})
print("\nWarehouses:")
for w in warehouses:
    print(f"  WH {w['id']}: {w['name']} ({w['code']}) → company: {w['company_id'][1]} (ID {w['company_id'][0]}), stock_loc: {w['lot_stock_id']}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. INTERNAL TRANSFER: Parent WH → Branch WH (stock.picking)")
print("=" * 70)

# Get locations
parent_stock_loc = None
branch_stock_loc = None
for w in warehouses:
    if w['code'] == 'WH':  # Krishnadas Group main warehouse
        parent_stock_loc = w['lot_stock_id']
    if w['code'] == 'DF':  # Devika Furniture Showroom
        branch_stock_loc = w['lot_stock_id']

print(f"  Source: {parent_stock_loc}")
print(f"  Dest:   {branch_stock_loc}")

# Find the internal picking type for parent company
picking_types = x('stock.picking.type', 'search_read', 
    [[('code', '=', 'internal'), ('company_id', '=', 1)]],
    {'fields': ['name', 'code', 'warehouse_id', 'company_id', 'default_location_src_id', 'default_location_dest_id']})
print(f"\n  Internal picking types (Krishnadas Group):")
for pt in picking_types:
    print(f"    ID {pt['id']}: {pt['name']} (WH: {pt['warehouse_id']}, src: {pt['default_location_src_id']}, dest: {pt['default_location_dest_id']})")

# Also check branch picking types
branch_picking_types = x('stock.picking.type', 'search_read', 
    [[('code', '=', 'internal'), ('company_id', '=', 2)]],
    {'fields': ['name', 'code', 'warehouse_id', 'company_id']})
print(f"\n  Internal picking types (Devika Furniture):")
for pt in branch_picking_types:
    print(f"    ID {pt['id']}: {pt['name']} (WH: {pt['warehouse_id']})")

# Find a product to transfer
products = x('product.product', 'search_read', [[('type', '=', 'product')]], 
             {'fields': ['name', 'qty_available'], 'limit': 3})
if not products:
    products = x('product.product', 'search_read', [[('type', '=', 'consu')]], 
                 {'fields': ['name'], 'limit': 3})
print(f"\n  Test product: {products[0]['name'] if products else 'NONE FOUND'}")

# Now try creating an internal transfer from Parent WH → Branch WH
print(f"\n  ATTEMPT: Internal transfer from {parent_stock_loc[1]} → {branch_stock_loc[1]}")
print(f"  Using parent company's internal picking type...")

if picking_types and parent_stock_loc and branch_stock_loc and products:
    pt_id = picking_types[0]['id']
    prod_id = products[0]['id']
    
    try:
        picking_id = x('stock.picking', 'create', [{
            'picking_type_id': pt_id,
            'location_id': parent_stock_loc[0],
            'location_dest_id': branch_stock_loc[0],
            'company_id': 1,  # Parent company
            'move_ids': [(0, 0, {
                'name': 'Test Transfer',
                'product_id': prod_id,
                'product_uom_qty': 1.0,
                'location_id': parent_stock_loc[0],
                'location_dest_id': branch_stock_loc[0],
            })]
        }])
        print(f"  ✅ Internal transfer CREATED! Picking ID: {picking_id}")
        
        # Read back
        pick_data = x('stock.picking', 'read', [picking_id], 
                      {'fields': ['name', 'company_id', 'location_id', 'location_dest_id', 'state', 'picking_type_id']})
        print(f"  Details: {pick_data}")
        
        # Check the destination location's company
        dest_loc = x('stock.location', 'read', [branch_stock_loc[0]], 
                     {'fields': ['name', 'company_id', 'complete_name']})
        print(f"\n  Destination location details: {dest_loc}")
        print(f"  Destination location company: {dest_loc[0]['company_id']}")
        
        src_loc = x('stock.location', 'read', [parent_stock_loc[0]], 
                    {'fields': ['name', 'company_id', 'complete_name']})
        print(f"  Source location company: {src_loc[0]['company_id']}")
        
        # Clean up
        x('stock.picking', 'unlink', [picking_id])
        print(f"  (Test picking deleted)")
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")

# Also try with branch company's picking type
print(f"\n  ATTEMPT 2: Using branch picking type (if exists)...")
if branch_picking_types and parent_stock_loc and branch_stock_loc and products:
    pt_id2 = branch_picking_types[0]['id']
    try:
        picking_id2 = x('stock.picking', 'create', [{
            'picking_type_id': pt_id2,
            'location_id': parent_stock_loc[0],
            'location_dest_id': branch_stock_loc[0],
            'company_id': 2,  # Branch company
            'move_ids': [(0, 0, {
                'name': 'Test Transfer 2',
                'product_id': prod_id,
                'product_uom_qty': 1.0,
                'location_id': parent_stock_loc[0],
                'location_dest_id': branch_stock_loc[0],
            })]
        }])
        print(f"  ✅ Transfer CREATED with branch picking type! ID: {picking_id2}")
        pick_data2 = x('stock.picking', 'read', [picking_id2], 
                      {'fields': ['name', 'company_id', 'location_id', 'location_dest_id', 'state']})
        print(f"  Details: {pick_data2}")
        x('stock.picking', 'unlink', [picking_id2])
        print(f"  (Test picking deleted)")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. CHECK LOCATION COMPANIES")
print("=" * 70)

# Check ALL stock locations and their companies
locations = x('stock.location', 'search_read', 
    [[('usage', '=', 'internal')]],
    {'fields': ['name', 'complete_name', 'company_id', 'warehouse_id']})
print(f"  All internal stock locations:")
for loc in locations:
    print(f"    ID {loc['id']}: {loc['complete_name']} → company: {loc['company_id']}, warehouse: {loc.get('warehouse_id', 'N/A')}")

# Check transit locations
transit_locs = x('stock.location', 'search_read', 
    [[('usage', '=', 'transit')]],
    {'fields': ['name', 'complete_name', 'company_id']})
print(f"\n  Transit locations:")
for loc in transit_locs:
    print(f"    ID {loc['id']}: {loc['complete_name']} → company: {loc['company_id']}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. JOURNAL SHARING — Can branch use parent's journals?")
print("=" * 70)

# Check journal company_id field definition
journal_fields = x('account.journal', 'fields_get', [['company_id']], 
                   {'attributes': ['string', 'type', 'required', 'readonly', 'domain']})
print(f"  account.journal company_id field:")
for k, v in journal_fields['company_id'].items():
    if v:
        print(f"    {k}: {v}")

# Try creating an invoice under branch using parent's journal
parent_journals = x('account.journal', 'search_read', 
    [[('company_id', '=', 1), ('type', '=', 'sale')]],
    {'fields': ['name', 'code', 'company_id']})
branch_journals = x('account.journal', 'search_read', 
    [[('company_id', '=', 2), ('type', '=', 'sale')]],
    {'fields': ['name', 'code', 'company_id']})

print(f"\n  Parent sale journals: {parent_journals}")
print(f"  Branch sale journals: {branch_journals}")

print(f"\n  ATTEMPT: Create invoice under branch with PARENT's journal...")
if parent_journals:
    try:
        inv_id = x('account.move', 'create', [{
            'move_type': 'out_invoice',
            'company_id': 2,  # Branch
            'journal_id': parent_journals[0]['id'],  # Parent's journal
            'partner_id': 50,
        }])
        print(f"  ✅ Invoice created! ID: {inv_id}")
        inv_data = x('account.move', 'read', [inv_id], {'fields': ['name', 'company_id', 'journal_id']})
        print(f"  Details: {inv_data}")
        x('account.move', 'button_cancel', [inv_id])
        x('account.move', 'unlink', [inv_id])
        print(f"  (Test invoice deleted)")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")

print(f"\n  ATTEMPT: Create invoice under branch with BRANCH's own journal...")
if branch_journals:
    try:
        inv_id2 = x('account.move', 'create', [{
            'move_type': 'out_invoice',
            'company_id': 2,
            'journal_id': branch_journals[0]['id'],
            'partner_id': 50,
        }])
        print(f"  ✅ Invoice created! ID: {inv_id2}")
        inv_data2 = x('account.move', 'read', [inv_id2], {'fields': ['name', 'company_id', 'journal_id']})
        print(f"  Details: {inv_data2}")
        x('account.move', 'unlink', [inv_id2])
        print(f"  (Test invoice deleted)")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. TAXES — Can branch use parent's taxes?")
print("=" * 70)

parent_taxes = x('account.tax', 'search_read', 
    [[('company_id', '=', 1)]], {'fields': ['name', 'company_id'], 'limit': 5})
branch_taxes = x('account.tax', 'search_read', 
    [[('company_id', '=', 2)]], {'fields': ['name', 'company_id']})

print(f"  Parent taxes (first 5 of many): {[t['name'] for t in parent_taxes]}")
print(f"  Branch own taxes: {branch_taxes if branch_taxes else 'NONE'}")

# Check tax field — does it use parent_of operator?
tax_field_on_invoice_line = x('account.move.line', 'fields_get', [['tax_ids']], 
    {'attributes': ['string', 'type', 'domain', 'relation']})
print(f"\n  tax_ids field on account.move.line:")
for k, v in tax_field_on_invoice_line.get('tax_ids', {}).items():
    if v:
        print(f"    {k}: {v}")

# Check account.tax company_id field
tax_company_field = x('account.tax', 'fields_get', [['company_id']], 
    {'attributes': ['string', 'type', 'required', 'domain']})
print(f"\n  account.tax company_id field:")
for k, v in tax_company_field.get('company_id', {}).items():
    if v:
        print(f"    {k}: {v}")

# Check if branch can see parent taxes (using parent_of domain)
print(f"\n  Taxes visible to branch (company_id parent_of 2):")
try:
    visible_taxes = x('account.tax', 'search_read', 
        [[('company_id', 'parent_of', 2)]], {'fields': ['name', 'company_id'], 'limit': 5})
    print(f"  Found {len(visible_taxes)} taxes — first 5: {[(t['name'], t['company_id'][1]) for t in visible_taxes]}")
    total = x('account.tax', 'search_count', [[('company_id', 'parent_of', 2)]])
    print(f"  Total taxes visible to branch via parent_of: {total}")
except Exception as e:
    print(f"  parent_of query error: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. ACCOUNTS (Chart of Accounts) — Shared?")
print("=" * 70)

# In Odoo 19, account.account may use company_ids (many2many) instead of company_id
try:
    acct_fields = x('account.account', 'fields_get', [['company_id', 'company_ids']], 
        {'attributes': ['string', 'type', 'required', 'domain', 'relation']})
    for fname, finfo in acct_fields.items():
        print(f"  {fname}:")
        for k, v in finfo.items():
            if v:
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# Check how many accounts the branch can see
try:
    branch_accounts = x('account.account', 'search_read', 
        [[('company_ids', 'in', [2])]], {'fields': ['code', 'name', 'company_ids'], 'limit': 10})
    total_branch_accts = x('account.account', 'search_count', [[('company_ids', 'in', [2])]])
    print(f"\n  Accounts with branch in company_ids: {total_branch_accts}")
    for a in branch_accounts[:5]:
        print(f"    {a['code']} {a['name']} — companies: {a['company_ids']}")
except:
    try:
        branch_accounts = x('account.account', 'search_read', 
            [[('company_id', 'parent_of', 2)]], {'fields': ['code', 'name'], 'limit': 10})
        total_branch_accts = x('account.account', 'search_count', [[('company_id', 'parent_of', 2)]])
        print(f"\n  Accounts via parent_of: {total_branch_accts}")
    except Exception as e:
        print(f"  Error querying accounts: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. RESUPPLY BETWEEN WAREHOUSES — Check routes")
print("=" * 70)

# Check if resupply routes exist between parent and branch warehouses
for w in warehouses:
    wh_detail = x('stock.warehouse', 'read', [w['id']], 
                  {'fields': ['name', 'resupply_wh_ids', 'route_ids', 'company_id']})
    resupply = wh_detail[0].get('resupply_wh_ids', [])
    print(f"  WH {w['id']} ({w['name']}): resupply_from = {resupply}")

# Check if resupply between different companies works
print(f"\n  Checking resupply_wh_ids field definition:")
try:
    resup_field = x('stock.warehouse', 'fields_get', [['resupply_wh_ids']], 
        {'attributes': ['string', 'type', 'domain', 'relation']})
    for k, v in resup_field.get('resupply_wh_ids', {}).items():
        if v:
            print(f"    {k}: {v}")
except Exception as e:
    print(f"    Error: {e}")

# Try to set resupply from parent WH to branch WH
print(f"\n  ATTEMPT: Set Devika Furniture Showroom to resupply from Krishnadas Group WH...")
try:
    x('stock.warehouse', 'write', [6], {'resupply_wh_ids': [(4, 1)]})  # Add WH 1 as resupply source for WH 6
    print(f"  ✅ Resupply link set!")
    
    # Read back
    check = x('stock.warehouse', 'read', [6], {'fields': ['resupply_wh_ids']})
    print(f"  Devika Furniture Showroom resupply_wh_ids: {check[0]['resupply_wh_ids']}")
    
    # Check if routes were auto-created
    routes = x('stock.route', 'search_read', 
        [[('name', 'ilike', 'Devika')]], {'fields': ['name', 'company_id']})
    print(f"  Routes mentioning 'Devika': {routes}")
    
    # Clean up — remove the resupply link
    x('stock.warehouse', 'write', [6], {'resupply_wh_ids': [(3, 1)]})  # Remove WH 1
    print(f"  (Resupply link removed)")
    
except Exception as e:
    print(f"  ❌ FAILED: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. FISCAL POSITIONS — Shared?")
print("=" * 70)
fps = x('account.fiscal.position', 'search_read', [[]], 
        {'fields': ['name', 'company_id']})
for fp in fps:
    print(f"  {fp['name']} → company: {fp['company_id']}")

fp_field = x('account.fiscal.position', 'fields_get', [['company_id']], 
    {'attributes': ['string', 'type', 'required', 'domain']})
print(f"\n  Fiscal position company_id field:")
for k, v in fp_field.get('company_id', {}).items():
    if v:
        print(f"    {k}: {v}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. DEFINITIVE SUMMARY")
print("=" * 70)
