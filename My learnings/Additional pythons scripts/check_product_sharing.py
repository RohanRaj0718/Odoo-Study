"""Check product sharing behavior across companies - which fields are shared vs company-specific."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=10, context=None):
    kw = {'fields': fields, 'limit': limit}
    if context:
        kw['context'] = context
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

# Pick a few products and check their company field + key fields
print("=" * 80)
print("PRODUCT COMPANY FIELD & KEY DATA")
print("=" * 80)

products = sr('product.product', [], 
    ['name', 'company_id', 'list_price', 'standard_price', 'taxes_id', 'supplier_taxes_id', 
     'type', 'categ_id', 'uom_id'], limit=10)

for p in products:
    comp = p['company_id'][1] if p['company_id'] else 'ALL COMPANIES (shared)'
    print(f"\n  [{p['id']}] {p['name']}")
    print(f"    Company:        {comp}")
    print(f"    Sale Price:     ₹{p['list_price']:,.2f}")
    print(f"    Cost Price:     ₹{p['standard_price']:,.2f}")
    print(f"    Sale Taxes:     {p['taxes_id']}")
    print(f"    Purchase Taxes: {p['supplier_taxes_id']}")
    print(f"    Type:           {p['type']}")
    print(f"    Category:       {p['categ_id'][1] if p['categ_id'] else 'N/A'}")
    print(f"    UoM:            {p['uom_id'][1] if p['uom_id'] else 'N/A'}")

# Check if price varies by company using product.product (variant) with company context
print("\n" + "=" * 80)
print("CHECKING IF COST/PRICE CHANGES PER COMPANY CONTEXT")
print("=" * 80)

# Pick one product
test_prod = sr('product.product', [], ['name', 'product_tmpl_id'], limit=1)
if test_prod:
    pid = test_prod[0]['id']
    pname = test_prod[0]['name']
    print(f"\nTest product: [{pid}] {pname}")
    
    companies = sr('res.company', [], ['name'], limit=10)
    for c in companies:
        try:
            data = sr('product.product', [['id', '=', pid]], 
                ['list_price', 'standard_price'], limit=1,
                context={'allowed_company_ids': [c['id']], 'force_company': c['id']})
            if data:
                print(f"  {c['name']:35s} → Sale: ₹{data[0]['list_price']:>10,.2f} | Cost: ₹{data[0]['standard_price']:>10,.2f}")
        except Exception as e:
            print(f"  {c['name']:35s} → Error: {e}")

# Check company-specific fields
print("\n" + "=" * 80)
print("FIELDS MODEL: product.template fields with 'company' in them")
print("=" * 80)

fields = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'fields_get', [], 
    {'attributes': ['string', 'type', 'company_dependent']})

company_dep = []
has_company = []
for fname, fdata in fields.items():
    if fdata.get('company_dependent'):
        company_dep.append((fname, fdata['string'], fdata['type']))
    if 'company' in fname.lower():
        has_company.append((fname, fdata['string'], fdata['type']))

print("\nCompany-Dependent fields (value differs per company):")
for f in sorted(company_dep):
    print(f"  {f[0]:35s} | {f[1]:35s} | {f[2]}")

print(f"\nFields with 'company' in name:")
for f in sorted(has_company):
    print(f"  {f[0]:35s} | {f[1]:35s} | {f[2]}")

# Also check account fields (accounting properties are company-dependent)
print("\n" + "=" * 80)
print("ACCOUNT/PROPERTY FIELDS ON product.template")
print("=" * 80)
prop_fields = {k: v for k, v in fields.items() if 'property' in k.lower() or 'account' in k.lower()}
for fname, fdata in sorted(prop_fields.items()):
    cd = "✅ COMPANY-DEPENDENT" if fdata.get('company_dependent') else ""
    print(f"  {fname:40s} | {fdata['string']:35s} | {fdata['type']:10s} | {cd}")

print("\n=== DONE ===")
