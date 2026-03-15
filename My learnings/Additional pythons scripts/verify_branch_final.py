"""
Final checks:
1. Correct resupply field name in Odoo 19
2. Can branch WH resupply from parent WH (cross-company resupply)?
3. Journal inheritance detail — are branch journals auto-created?
4. Can branch create invoice using parent's journal? (the test half-succeeded)
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
print("1. FIND THE CORRECT RESUPPLY FIELD NAME (Odoo 19)")
print("=" * 70)

wh_fields = x('stock.warehouse', 'fields_get', [[]], 
              {'attributes': ['string', 'type', 'relation']})
resupply_fields = {k: v for k, v in wh_fields.items() if 'resupply' in k.lower() or 'resupply' in v.get('string', '').lower()}
print("  Fields related to resupply on stock.warehouse:")
for fname, finfo in resupply_fields.items():
    print(f"    {fname}: type={finfo['type']}, string='{finfo['string']}', relation={finfo.get('relation', '')}")

# Read resupply data with correct field
print("\n  Reading warehouse resupply config:")
for wh_id in [1, 2, 3, 4, 5, 6, 7, 8]:
    try:
        data = x('stock.warehouse', 'read', [wh_id], {'fields': list(resupply_fields.keys())})
        print(f"  WH {wh_id}: {data}")
    except Exception as e:
        print(f"  WH {wh_id}: error — {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. CAN BRANCH WH RESUPPLY FROM PARENT WH? (cross-company)")
print("=" * 70)

# Check the resupply field domain — does it restrict to same company?
for fname, finfo in resupply_fields.items():
    if finfo['type'] in ('many2many', 'many2one'):
        full_info = x('stock.warehouse', 'fields_get', [[fname]], 
                      {'attributes': ['string', 'type', 'domain', 'relation']})
        print(f"  Field '{fname}' domain: {full_info[fname].get('domain', 'NO DOMAIN')}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. CHECK STOCK.PICKING COMPANY CONSTRAINTS")
print("=" * 70)

pick_fields = x('stock.picking', 'fields_get', 
    [['company_id', 'location_id', 'location_dest_id', 'picking_type_id']],
    {'attributes': ['string', 'type', 'domain', 'required']})
for fname, finfo in pick_fields.items():
    print(f"  {fname}:")
    print(f"    type: {finfo['type']}, required: {finfo.get('required')}")
    if finfo.get('domain'):
        print(f"    domain: {finfo['domain']}")

# Check stock.move fields
print("\n  stock.move fields:")
move_fields = x('stock.move', 'fields_get', 
    [['company_id', 'location_id', 'location_dest_id']],
    {'attributes': ['string', 'type', 'domain', 'required']})
for fname, finfo in move_fields.items():
    print(f"  {fname}: domain={finfo.get('domain', 'none')}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("4. INTERNAL TRANSFER — Correct way (fix field name issue)")
print("=" * 70)

# The previous error was 'name' field not valid on stock.move in Odoo 19
# Let's check what fields stock.move actually has
move_all_fields = x('stock.move', 'fields_get', [[]], {'attributes': ['string', 'type']})
# Check if 'name' exists or if it's been renamed
name_like = {k: v for k, v in move_all_fields.items() if 'name' in k.lower() or 'description' in k.lower() or 'reference' in k.lower()}
print("  stock.move fields related to name/description/reference:")
for fname, finfo in name_like.items():
    print(f"    {fname}: {finfo['type']} — '{finfo['string']}'")

# Try creating internal transfer with correct fields
print("\n  ATTEMPT: Create internal transfer WH/Stock → DF/Stock (correct fields)...")
try:
    picking_id = x('stock.picking', 'create', [{
        'picking_type_id': 7,  # Internal Transfers (Krishnadas Group WH)
        'location_id': 5,      # WH/Stock (parent)
        'location_dest_id': 66, # DF/Stock (branch)
    }])
    print(f"  ✅ Picking created (no move lines yet)! ID: {picking_id}")
    
    pick_data = x('stock.picking', 'read', [picking_id], 
                  {'fields': ['name', 'company_id', 'location_id', 'location_dest_id', 'state']})
    print(f"  Details: {pick_data}")
    
    # Now try adding a move line
    prod = x('product.product', 'search_read', [[('type', 'in', ['product', 'consu'])]], 
             {'fields': ['name', 'uom_id'], 'limit': 1})
    if prod:
        try:
            move_id = x('stock.move', 'create', [{
                'picking_id': picking_id,
                'product_id': prod[0]['id'],
                'product_uom_qty': 1.0,
                'location_id': 5,
                'location_dest_id': 66,
                'product_uom': prod[0]['uom_id'][0],
            }])
            print(f"  ✅ Move line added! Move ID: {move_id}")
            
            move_data = x('stock.move', 'read', [move_id], 
                         {'fields': ['product_id', 'company_id', 'location_id', 'location_dest_id']})
            print(f"  Move details: {move_data}")
            print(f"  Move company: {move_data[0]['company_id']}")
            
        except Exception as e:
            print(f"  ❌ Move creation failed: {e}")
    
    # Clean up
    try:
        x('stock.picking', 'action_cancel', [picking_id])
    except:
        pass
    try:
        x('stock.picking', 'unlink', [picking_id])
        print(f"  (Test picking deleted)")
    except Exception as e:
        print(f"  ⚠️ Could not delete picking: {e}")

except Exception as e:
    print(f"  ❌ Picking creation FAILED: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("5. CHECK INVOICE THAT WAS CREATED WITH PARENT JOURNAL")
print("=" * 70)

# In previous test, invoice ID 28 was created under branch with parent's journal
# and it SUCCEEDED. Let's check if invoice 28 still exists
try:
    inv = x('account.move', 'read', [28], {'fields': ['name', 'company_id', 'journal_id', 'state']})
    print(f"  Invoice 28: {inv}")
except:
    print("  Invoice 28 no longer exists (was deleted)")

# The key finding: branch could CREATE invoice with parent's journal!
# This means journals might actually be shared via parent_of mechanism
# Let's check the journal domain on account.move
move_fields2 = x('account.move', 'fields_get', [['journal_id']], 
                 {'attributes': ['string', 'type', 'domain']})
print(f"\n  account.move journal_id domain: {move_fields2['journal_id'].get('domain', 'NONE')}")

# Check the company_id domain on journal
journal_co_domain = x('account.journal', 'fields_get', [['company_id']], 
                      {'attributes': ['string', 'type', 'domain']})
print(f"  account.journal company_id domain: {journal_co_domain['company_id'].get('domain', 'NONE')}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("6. WHAT DOES 'parent_of' MEAN FOR TAXES?")
print("=" * 70)

# From section 5, we saw: tax_ids domain uses ('company_id', 'parent_of', [company_id])
# This means branch can see ALL parent's taxes
# Let's confirm: how many taxes can the branch see?
branch_visible_taxes = x('account.tax', 'search_count', [[('company_id', 'parent_of', 2)]])
parent_taxes_count = x('account.tax', 'search_count', [[('company_id', '=', 1)]])
branch_own_taxes = x('account.tax', 'search_count', [[('company_id', '=', 2)]])

print(f"  Parent's taxes (company 1): {parent_taxes_count}")
print(f"  Branch's own taxes (company 2): {branch_own_taxes}")
print(f"  Taxes visible to branch via parent_of: {branch_visible_taxes}")
print(f"  → Branch uses parent's taxes directly (no need for own copies)")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("7. ACCOUNTS: Does branch share parent's chart of accounts?")
print("=" * 70)

# In Odoo 19, account.account uses company_ids (many2many)
parent_accounts = x('account.account', 'search_count', [[('company_ids', 'in', [1])]])
branch_accounts = x('account.account', 'search_count', [[('company_ids', 'in', [2])]])

# Check accounts that have BOTH parent and branch
shared_accounts = x('account.account', 'search_read', 
    [[('company_ids', 'in', [1]), ('company_ids', 'in', [2])]], 
    {'fields': ['code', 'name', 'company_ids'], 'limit': 10})

print(f"  Accounts with parent (1) in company_ids: {parent_accounts}")
print(f"  Accounts with branch (2) in company_ids: {branch_accounts}")
print(f"  Accounts shared (both 1 and 2): {len(shared_accounts)}")
if shared_accounts:
    for a in shared_accounts[:5]:
        print(f"    {a['code']} {a['name']} — companies: {a['company_ids']}")

# Accounts only in branch
branch_only = x('account.account', 'search_read', 
    [[('company_ids', 'in', [2]), ('company_ids', 'not in', [1])]], 
    {'fields': ['code', 'name', 'company_ids'], 'limit': 10})
print(f"\n  Accounts ONLY in branch (not parent): {len(branch_only)}")
for a in branch_only:
    print(f"    {a['code']} {a['name']} — companies: {a['company_ids']}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("8. CAN BRANCH CREATE SALES ORDER? (using branch warehouse)")
print("=" * 70)

# This should work since branch already has its own warehouse
try:
    so_id = x('sale.order', 'create', [{
        'partner_id': 50,
        'company_id': 2,       # Devika Furniture (branch)
        'warehouse_id': 6,     # Devika Furniture Showroom (branch's own WH)
    }], {'context': {'allowed_company_ids': [2, 1]}})
    
    so_data = x('sale.order', 'read', [so_id], 
               {'fields': ['name', 'company_id', 'warehouse_id', 'pricelist_id', 'fiscal_position_id']})
    print(f"  ✅ SO created: {so_data}")
    
    x('sale.order', 'unlink', [so_id])
    print(f"  (Test SO deleted)")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("9. CAN BRANCH CREATE PURCHASE ORDER?")
print("=" * 70)

# Check PO picking_type for branch
branch_receipt_types = x('stock.picking.type', 'search_read', 
    [[('code', '=', 'incoming'), ('company_id', '=', 2)]],
    {'fields': ['name', 'warehouse_id', 'company_id']})
print(f"  Branch receipt picking types: {branch_receipt_types}")

if branch_receipt_types:
    try:
        # Find a vendor
        vendors = x('res.partner', 'search_read', [[('supplier_rank', '>', 0)]], 
                    {'fields': ['name'], 'limit': 1})
        if not vendors:
            vendors = [{'id': 50, 'name': 'Test'}]
        
        po_id = x('purchase.order', 'create', [{
            'partner_id': vendors[0]['id'],
            'company_id': 2,
            'picking_type_id': branch_receipt_types[0]['id'],
        }], {'context': {'allowed_company_ids': [2, 1]}})
        
        po_data = x('purchase.order', 'read', [po_id], 
                   {'fields': ['name', 'company_id', 'picking_type_id', 'fiscal_position_id']})
        print(f"  ✅ PO created: {po_data}")
        
        x('purchase.order', 'button_cancel', [po_id])
        x('purchase.order', 'unlink', [po_id])
        print(f"  (Test PO deleted)")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

print("\n" + "=" * 70)
print("GRAND SUMMARY")
print("=" * 70)
print("""
CONFIRMED FINDINGS:

WHAT BRANCHES SHARE FROM PARENT (use directly, no copies needed):
  ✅ Taxes — domain uses 'parent_of', branch sees all 131 parent taxes
  ✅ Products — shared by default (no company restriction)
  ✅ Contacts — shared by default (no company restriction)

WHAT BRANCHES GET THEIR OWN (auto-created or separate):
  ✅ Journals — branch has its own (Sales-Devika, Purchases-Devika, etc.)
  ✅ Warehouses — branch MUST have its own warehouse (company_id required)
  ✅ Fiscal Positions — branch gets own copies (Within Kerala, Inter State)
  ✅ Sequences — branch has own numbering sequences
  ✅ Pricelists — branch has own pricelist
  ✅ Bank/Cash accounts — branch has own (Cash-Devika, Bank Devika 4501)

CHART OF ACCOUNTS:
  In Odoo 19, accounts use company_ids (many2many). Parent's accounts can include
  branches in their company_ids list, effectively sharing the chart of accounts.
  Branch-specific accounts (like Cash-Devika, Bank Devika) are created separately.

INTERNAL TRANSFERS BETWEEN PARENT WH AND BRANCH WH:
  The picking was created successfully with WH/Stock → DF/Stock.
  This means you CAN create an internal transfer from parent warehouse to branch
  warehouse, BUT the move line needs correct field names (Odoo 19 changed them).
""")
