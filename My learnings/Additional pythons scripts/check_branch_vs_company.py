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

print("=" * 80)
print("1. ALL COMPANIES - Full Details")
print("=" * 80)
companies = x('res.company', [], ['name', 'parent_id', 'child_ids', 'company_registry', 'vat', 'partner_id'])
for c in companies:
    parent = c['parent_id'][1] if c['parent_id'] else "NONE (Root Company)"
    children = c['child_ids'] if c['child_ids'] else []
    print(f"\n  ID: {c['id']}")
    print(f"  Name: {c['name']}")
    print(f"  Parent: {parent}")
    print(f"  Child Company IDs: {children}")
    print(f"  VAT/GSTIN: {c.get('vat', 'N/A')}")
    print(f"  Company Registry: {c.get('company_registry', 'N/A')}")

# Check if there's a 'branch' field (Odoo 17+ feature)
print("\n" + "=" * 80)
print("2. CHECKING FOR BRANCH-RELATED FIELDS ON res.company")
print("=" * 80)
try:
    # Try to get fields that contain 'branch' in the name
    all_fields = models.execute_kw(DB, uid, PWD, 'res.company', 'fields_get', [], {'attributes': ['string', 'type', 'help']})
    branch_fields = {k: v for k, v in all_fields.items() if 'branch' in k.lower() or 'branch' in v.get('string', '').lower()}
    if branch_fields:
        for fname, finfo in branch_fields.items():
            print(f"  Field: {fname}")
            print(f"    Label: {finfo['string']}")
            print(f"    Type: {finfo['type']}")
            print(f"    Help: {finfo.get('help', 'N/A')}")
    else:
        print("  No branch-specific fields found on res.company")
except Exception as e:
    print(f"  Error: {e}")

# Check if companies have the 'branch' concept via parent_id
print("\n" + "=" * 80)
print("3. COMPANY HIERARCHY TREE")
print("=" * 80)
root_companies = [c for c in companies if not c['parent_id']]
for root in root_companies:
    print(f"\n  ROOT: {root['name']} (ID: {root['id']})")
    children = [c for c in companies if c['parent_id'] and c['parent_id'][0] == root['id']]
    for child in children:
        print(f"    └── CHILD: {child['name']} (ID: {child['id']})")
        grandchildren = [c for c in companies if c['parent_id'] and c['parent_id'][0] == child['id']]
        for gc in grandchildren:
            print(f"        └── GRANDCHILD: {gc['name']} (ID: {gc['id']})")

# Check warehouses and which company they belong to
print("\n" + "=" * 80)
print("4. WAREHOUSES - Which Company Owns Each")
print("=" * 80)
warehouses = x('stock.warehouse', [], ['name', 'code', 'company_id'])
for w in warehouses:
    print(f"  Warehouse: {w['name']} ({w['code']}) → Company: {w['company_id'][1]} (ID: {w['company_id'][0]})")

# Check users and their company/branch assignments
print("\n" + "=" * 80)
print("5. USERS - Company Assignments")
print("=" * 80)
users = x('res.users', [('share', '=', False)], ['name', 'login', 'company_id', 'company_ids'])
for u in users:
    print(f"\n  User: {u['name']} ({u['login']})")
    print(f"    Current Company: {u['company_id'][1]} (ID: {u['company_id'][0]})")
    # Get company names for all allowed companies
    if u['company_ids']:
        allowed = x('res.company', [('id', 'in', u['company_ids'])], ['name'])
        allowed_names = [f"{a['name']} (ID:{a['id']})" for a in allowed]
        print(f"    Allowed Companies: {', '.join(allowed_names)}")

# Check inter-company settings
print("\n" + "=" * 80)
print("6. INTER-COMPANY MODULE STATUS")
print("=" * 80)
modules = x('ir.module.module', [('name', 'in', [
    'base_branch_company',
    'account_inter_company_rules',
    'sale_purchase_inter_company_rules',
    'branch',
])], ['name', 'state', 'shortdesc'])
if modules:
    for m in modules:
        print(f"  {m['name']}: {m['state']} ({m['shortdesc']})")
else:
    print("  No branch/inter-company modules found")

# Check all installed modules related to company/branch
print("\n" + "=" * 80)
print("7. ALL INSTALLED MODULES WITH 'branch' OR 'multi' OR 'inter' IN NAME")
print("=" * 80)
related_modules = x('ir.module.module', [
    ('state', '=', 'installed'),
    '|', '|', '|',
    ('name', 'ilike', 'branch'),
    ('name', 'ilike', 'multi_company'),
    ('name', 'ilike', 'inter_company'),
    ('name', 'ilike', 'intercompany'),
], ['name', 'state', 'shortdesc'])
if related_modules:
    for m in related_modules:
        print(f"  {m['name']}: {m['shortdesc']}")
else:
    print("  None found")

# Check res.company for any additional relevant fields
print("\n" + "=" * 80)
print("8. res.company FIELDS RELATED TO PARENT/CHILD/MULTI")
print("=" * 80)
relevant_fields = {k: v for k, v in all_fields.items() if any(word in k.lower() for word in ['parent', 'child', 'multi', 'inter', 'rule'])}
for fname, finfo in relevant_fields.items():
    print(f"  {fname}: {finfo['string']} ({finfo['type']})")

# Check the actual parent_id values explicitly
print("\n" + "=" * 80)
print("9. EXPLICIT PARENT-CHILD CHECK")
print("=" * 80)
for c in companies:
    if c['name'] in ['Georgeon Furniture', 'PSQUARE INTERIOR']:
        print(f"\n  {c['name']}:")
        print(f"    parent_id = {c['parent_id']}")
        print(f"    child_ids = {c['child_ids']}")
        if c['parent_id']:
            print(f"    → This IS a child/branch of: {c['parent_id'][1]}")
        else:
            print(f"    → This is a STANDALONE root company (NOT a branch)")
