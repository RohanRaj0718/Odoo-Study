"""Fix: Look up correct sale tax IDs per company, delete draft invoices, recreate properly."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=50):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# Step 1: Find sale taxes (type_tax_use=sale) per company
print("=" * 60)
print("SALE TAXES BY COMPANY")
print("=" * 60)

taxes = sr('account.tax', [['type_tax_use', '=', 'sale']], 
           ['name', 'company_id', 'amount', 'amount_type', 'tax_group_id'], limit=100)

company_taxes = {}
for t in taxes:
    cid = t['company_id'][0]
    cname = t['company_id'][1]
    if cid not in company_taxes:
        company_taxes[cid] = {'name': cname, 'taxes': []}
    company_taxes[cid]['taxes'].append({
        'id': t['id'],
        'name': t['name'],
        'amount': t['amount'],
        'type': t['amount_type'],
        'group': t['tax_group_id'][1] if t['tax_group_id'] else None
    })

for cid, data in sorted(company_taxes.items()):
    print(f"\n{data['name']} (ID={cid}):")
    for t in sorted(data['taxes'], key=lambda x: x['name']):
        print(f"  ID={t['id']:4d} | {t['name']:40s} | {t['amount']:6.1f}% | {t['type']} | group={t['group']}")

# Step 2: Look up GST 18% (SGST 9% + CGST 9%) equivalent per company
print("\n" + "=" * 60)
print("LOOKING FOR 9% SGST + 9% CGST PER COMPANY")
print("=" * 60)

for cid, data in sorted(company_taxes.items()):
    sgst = [t for t in data['taxes'] if 'SGST' in t['name'] and 'Sale' in t['name'] and t['amount'] == 9.0]
    cgst = [t for t in data['taxes'] if 'CGST' in t['name'] and 'Sale' in t['name'] and t['amount'] == 9.0]
    
    # Also check for GST 18%
    gst18 = [t for t in data['taxes'] if '18' in t['name'] and t['amount'] == 18.0]
    
    print(f"\n{data['name']} (ID={cid}):")
    if sgst:
        print(f"  SGST 9%: {[t['id'] for t in sgst]} - {sgst[0]['name']}")
    if cgst:
        print(f"  CGST 9%: {[t['id'] for t in cgst]} - {cgst[0]['name']}")
    if gst18:
        print(f"  GST 18%: {[t['id'] for t in gst18]} - {gst18[0]['name']}")
    if not sgst and not cgst and not gst18:
        # Show all with 9% amount
        nine = [t for t in data['taxes'] if t['amount'] == 9.0]
        print(f"  9% taxes: {[(t['id'], t['name']) for t in nine]}")
        eighteen = [t for t in data['taxes'] if t['amount'] == 18.0]
        print(f"  18% taxes: {[(t['id'], t['name']) for t in eighteen]}")

# Step 3: Check what draft invoices need to be deleted
print("\n" + "=" * 60)
print("DRAFT INVOICES TO CLEAN UP")
print("=" * 60)

drafts = sr('account.move', [['id', 'in', [57, 58, 59, 60, 61]], ['state', '=', 'draft']], 
            ['name', 'state', 'move_type', 'company_id'])
for d in drafts:
    print(f"  ID={d['id']} | {d['name']} | {d['state']} | {d['move_type']} | {d['company_id'][1]}")

print("\n=== DONE ===")
