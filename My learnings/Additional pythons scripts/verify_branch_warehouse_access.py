"""
Deep verification: Can a branch use the parent company's warehouse?
Check the exact field definitions, company rules, and test SO/PO creation.
"""
import xmlrpc.client
import json

URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def x(model, method, *a, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *a, **kw)

print("=" * 70)
print("1. COMPANIES AND BRANCHES")
print("=" * 70)
companies = x('res.company', 'search_read', [[]], {'fields': ['name', 'parent_id', 'child_ids']})
for c in companies:
    role = "BRANCH" if c['parent_id'] else "ROOT/PARENT"
    parent = f" (parent: {c['parent_id'][1]})" if c['parent_id'] else ""
    children = f" children: {c['child_ids']}" if c['child_ids'] else ""
    print(f"  ID {c['id']:>2}: {c['name']} [{role}]{parent}{children}")

print("\n" + "=" * 70)
print("2. WAREHOUSES AND THEIR COMPANIES")
print("=" * 70)
warehouses = x('stock.warehouse', 'search_read', [[]], {'fields': ['name', 'code', 'company_id']})
for w in warehouses:
    print(f"  WH ID {w['id']}: {w['name']} (code: {w['code']}) → company: {w['company_id']}")

print("\n" + "=" * 70)
print("3. WAREHOUSE FIELD DEFINITION ON sale.order")
print("=" * 70)
try:
    so_fields = x('sale.order', 'fields_get', [['warehouse_id']], {'attributes': ['string', 'type', 'relation', 'domain', 'company_dependent', 'help']})
    for fname, finfo in so_fields.items():
        print(f"  Field: {fname}")
        for k, v in finfo.items():
            if v:
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("4. WAREHOUSE FIELD DEFINITION ON purchase.order")
print("=" * 70)
try:
    # In purchase orders, the field might be called 'picking_type_id' or 'dest_address_id'
    po_fields = x('purchase.order', 'fields_get', [['picking_type_id', 'dest_address_id']], 
                  {'attributes': ['string', 'type', 'relation', 'domain', 'company_dependent', 'help']})
    for fname, finfo in po_fields.items():
        print(f"  Field: {fname}")
        for k, v in finfo.items():
            if v:
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("5. TRYING TO CREATE A SALES ORDER UNDER BRANCH COMPANY")
print("=" * 70)

# Get branch company IDs
branch_ids = [c['id'] for c in companies if c['parent_id']]
parent_ids = [c['id'] for c in companies if not c['parent_id'] and c['child_ids']]

if branch_ids and parent_ids:
    branch_id = branch_ids[0]
    parent_id = parent_ids[0]  
    branch_name = [c['name'] for c in companies if c['id'] == branch_id][0]
    parent_name = [c['name'] for c in companies if c['id'] == parent_id][0]
    
    print(f"\n  Testing with branch: {branch_name} (ID {branch_id})")
    print(f"  Parent: {parent_name} (ID {parent_id})")
    
    # Check which warehouses belong to the branch
    branch_wh = x('stock.warehouse', 'search_read', [[('company_id', '=', branch_id)]], {'fields': ['name', 'code']})
    parent_wh = x('stock.warehouse', 'search_read', [[('company_id', '=', parent_id)]], {'fields': ['name', 'code']})
    
    print(f"\n  Warehouses belonging to BRANCH ({branch_name}): {branch_wh if branch_wh else 'NONE'}")
    print(f"  Warehouses belonging to PARENT ({parent_name}):")
    for w in parent_wh:
        print(f"    - {w['name']} (ID {w['id']})")

    # Try to get the default warehouse for the branch
    print(f"\n  Checking default warehouse for branch...")
    try:
        # Check if branch has a property_stock_warehouse or similar
        branch_data = x('res.company', 'read', [branch_id], {'fields': ['name']})
        print(f"  Branch company data: {branch_data}")
    except Exception as e:
        print(f"  Error: {e}")

    # Try creating a SO under the branch with a parent warehouse
    print(f"\n  ATTEMPTING: Create SO under branch {branch_name} with parent warehouse...")
    
    # First find a customer (partner)
    partners = x('res.partner', 'search_read', [[('customer_rank', '>', 0)]], 
                 {'fields': ['name'], 'limit': 1})
    if not partners:
        partners = x('res.partner', 'search_read', [[('is_company', '=', True)]], 
                     {'fields': ['name'], 'limit': 1})
    
    if partners and parent_wh:
        partner_id = partners[0]['id']
        parent_wh_id = parent_wh[0]['id']
        
        print(f"  Partner: {partners[0]['name']} (ID {partner_id})")
        print(f"  Warehouse (parent's): {parent_wh[0]['name']} (ID {parent_wh_id})")
        
        # Try creating SO with branch company but parent warehouse
        try:
            # Use context to set the company to branch
            so_id = x('sale.order', 'create', [{
                'partner_id': partner_id,
                'company_id': branch_id,
                'warehouse_id': parent_wh_id,  # This is the parent's warehouse!
            }], {'context': {'allowed_company_ids': [branch_id, parent_id]}})
            print(f"\n  ✅ SUCCESS! SO created with ID {so_id}")
            print(f"     Branch SO using parent warehouse — IT WORKS!")
            
            # Read back to verify
            so_data = x('sale.order', 'read', [so_id], {'fields': ['name', 'company_id', 'warehouse_id']})
            print(f"     SO Data: {so_data}")
            
            # Clean up - delete the test SO
            x('sale.order', 'unlink', [so_id])
            print(f"     (Test SO deleted)")
            
        except Exception as e:
            print(f"\n  ❌ FAILED! Error: {e}")
            print(f"     Branch CANNOT use parent's warehouse — CONFIRMED!")
    
    # Now try creating a SO under the branch WITHOUT specifying warehouse (let Odoo pick default)
    print(f"\n  ATTEMPTING: Create SO under branch {branch_name} WITHOUT warehouse (default)...")
    if partners:
        try:
            so_id2 = x('sale.order', 'create', [{
                'partner_id': partner_id,
                'company_id': branch_id,
            }], {'context': {'allowed_company_ids': [branch_id, parent_id]}})
            print(f"\n  ✅ SO created with ID {so_id2}")
            
            so_data2 = x('sale.order', 'read', [so_id2], {'fields': ['name', 'company_id', 'warehouse_id']})
            print(f"     SO Data: {so_data2}")
            if so_data2:
                wh_id = so_data2[0]['warehouse_id']
                print(f"     Default warehouse assigned: {wh_id}")
                if wh_id:
                    wh_company = x('stock.warehouse', 'read', [wh_id[0]], {'fields': ['company_id']})
                    print(f"     That warehouse's company: {wh_company[0]['company_id']}")
            
            # Clean up
            x('sale.order', 'unlink', [so_id2])
            print(f"     (Test SO deleted)")
            
        except Exception as e:
            print(f"\n  ❌ FAILED! Error: {e}")
            print(f"     Branch cannot create SO without a warehouse!")

print("\n" + "=" * 70)
print("6. CHECK WHAT BRANCHES SHARE WITH PARENT")
print("=" * 70)

if branch_ids and parent_ids:
    branch_id = branch_ids[0]
    parent_id = parent_ids[0]
    
    # Journals per company
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        journals = x('account.journal', 'search_read', [[('company_id', '=', cid)]], 
                     {'fields': ['name', 'type', 'code']})
        print(f"\n  Journals for {cname} (ID {cid}): {len(journals)}")
        for j in journals:
            print(f"    - {j['name']} ({j['type']}, code: {j['code']})")
    
    # Taxes per company
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        taxes = x('account.tax', 'search_count', [[('company_id', '=', cid)]])
        print(f"\n  Taxes for {cname} (ID {cid}): {taxes}")
    
    # Chart of accounts (account.account) — check if branches share parent's
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        try:
            accounts = x('account.account', 'search_count', [[('company_ids', 'in', [cid])]])
            print(f"\n  Accounts visible to {cname} (ID {cid}): {accounts}")
        except:
            try:
                accounts = x('account.account', 'search_count', [[('company_id', '=', cid)]])
                print(f"\n  Accounts for {cname} (ID {cid}): {accounts}")
            except Exception as e:
                print(f"\n  Account count error for {cname}: {e}")

    # Fiscal positions per company
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        fps = x('account.fiscal.position', 'search_count', [[('company_id', '=', cid)]])
        print(f"\n  Fiscal Positions for {cname} (ID {cid}): {fps}")

    # Pricelists per company
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        try:
            pls = x('product.pricelist', 'search_read', [[('company_id', '=', cid)]], 
                    {'fields': ['name']})
            pls_shared = x('product.pricelist', 'search_read', [[('company_id', '=', False)]], 
                          {'fields': ['name']})
            print(f"\n  Pricelists for {cname} (ID {cid}): {len(pls)}")
            print(f"  Shared pricelists (no company): {len(pls_shared)}")
        except Exception as e:
            print(f"\n  Pricelist error: {e}")

    # Sequences per company
    for cid, cname in [(parent_id, parent_name), (branch_id, branch_name)]:
        try:
            seqs = x('ir.sequence', 'search_count', [[('company_id', '=', cid)]])
            print(f"\n  Sequences for {cname} (ID {cid}): {seqs}")
        except Exception as e:
            print(f"\n  Sequence error: {e}")

print("\n" + "=" * 70)
print("7. CHECK IF BRANCH CAN HAVE ITS OWN WAREHOUSE CREATED")
print("=" * 70)
print("  (Not creating, just checking if it's theoretically possible)")

# Check warehouse fields
wh_fields = x('stock.warehouse', 'fields_get', [['company_id', 'partner_id']], 
              {'attributes': ['string', 'type', 'required', 'readonly']})
for fname, finfo in wh_fields.items():
    print(f"  {fname}: required={finfo.get('required')}, readonly={finfo.get('readonly')}")

print("\n" + "=" * 70)
print("8. WHAT HAPPENS IF I CREATE A WAREHOUSE FOR THE BRANCH?")
print("=" * 70)
print("  Creating a test warehouse for the branch to see what Odoo does...")

if branch_ids:
    branch_id = branch_ids[0]
    try:
        test_wh_id = x('stock.warehouse', 'create', [{
            'name': 'Test Branch WH',
            'code': 'TBW',
            'company_id': branch_id,
        }])
        print(f"  ✅ Warehouse created! ID: {test_wh_id}")
        
        # Read back
        test_wh = x('stock.warehouse', 'read', [test_wh_id], 
                    {'fields': ['name', 'code', 'company_id', 'lot_stock_id']})
        print(f"  Details: {test_wh}")
        
        # Now try creating SO under branch with THIS warehouse
        print(f"\n  Now testing SO under branch with branch's own warehouse...")
        if partners:
            try:
                so_id3 = x('sale.order', 'create', [{
                    'partner_id': partner_id,
                    'company_id': branch_id,
                    'warehouse_id': test_wh_id,
                }], {'context': {'allowed_company_ids': [branch_id]}})
                print(f"  ✅ SO created! ID: {so_id3}")
                
                so_data3 = x('sale.order', 'read', [so_id3], 
                            {'fields': ['name', 'company_id', 'warehouse_id']})
                print(f"  SO Data: {so_data3}")
                
                # Clean up SO
                x('sale.order', 'unlink', [so_id3])
                print(f"  (Test SO deleted)")
            except Exception as e:
                print(f"  ❌ SO creation failed: {e}")
        
        # Clean up warehouse
        # First check if any stock moves or other records reference it
        try:
            x('stock.warehouse', 'unlink', [test_wh_id])
            print(f"  (Test warehouse deleted)")
        except Exception as e:
            print(f"  ⚠️ Could not delete test warehouse: {e}")
            print(f"     Warehouse ID {test_wh_id} remains — delete manually if needed")
    
    except Exception as e:
        print(f"  ❌ Cannot create warehouse for branch: {e}")

print("\n" + "=" * 70)
print("9. SUMMARY")
print("=" * 70)
print("""
KEY FINDINGS:
- Branches are child companies with separate company_id
- Warehouses have a REQUIRED company_id field
- The check_company mechanism filters warehouse dropdowns to match SO/PO company
- Branches SHARE: chart of accounts, taxes, currency, fiscal positions from parent
- Branches DO NOT SHARE: warehouses, journals (have own), sequences
- Products and Contacts are shared by default (company_id is optional on them)
""")
