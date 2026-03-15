"""
Create demo transactions (payments) in each branch/company
so the user can demonstrate branch-wise reporting properly.
Also check existing invoices to register payments against them.
"""
import xmlrpc.client
import time

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=100, order=None):
    kw = {'fields': fields, 'limit': limit}
    if order:
        kw['order'] = order
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

def cnt(model, domain=[]):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])

# ============================================================
# Step 1: Get all posted invoices/bills with amount_residual > 0
# (i.e., not yet fully paid)
# ============================================================
print("=" * 60)
print("UNPAID / PARTIALLY PAID INVOICES & BILLS")
print("=" * 60)

unpaid = sr('account.move', 
    [['state', '=', 'posted'], ['payment_state', 'in', ['not_paid', 'partial']], 
     ['move_type', 'in', ['out_invoice', 'in_invoice']]],
    ['name', 'move_type', 'partner_id', 'company_id', 'amount_total', 'amount_residual', 
     'currency_id', 'payment_state'],
    limit=50, order='company_id, move_type, name')

companies_data = {}
for inv in unpaid:
    cid = inv['company_id'][0] if inv['company_id'] else 0
    cname = inv['company_id'][1] if inv['company_id'] else 'Unknown'
    if cid not in companies_data:
        companies_data[cid] = {'name': cname, 'invoices': [], 'bills': []}
    
    entry = {
        'id': inv['id'],
        'name': inv['name'],
        'partner': inv['partner_id'][1] if inv['partner_id'] else 'N/A',
        'partner_id': inv['partner_id'][0] if inv['partner_id'] else False,
        'total': inv['amount_total'],
        'residual': inv['amount_residual'],
        'state': inv['payment_state']
    }
    
    if inv['move_type'] == 'out_invoice':
        companies_data[cid]['invoices'].append(entry)
    else:
        companies_data[cid]['bills'].append(entry)

for cid in sorted(companies_data.keys()):
    cdata = companies_data[cid]
    print(f"\n--- {cdata['name']} (ID: {cid}) ---")
    
    if cdata['invoices']:
        print("  UNPAID INVOICES:")
        for inv in cdata['invoices']:
            print(f"    {inv['name']} | {inv['partner']} | Total: {inv['total']} | Due: {inv['residual']} | Status: {inv['state']}")
    else:
        print("  No unpaid invoices")
    
    if cdata['bills']:
        print("  UNPAID BILLS:")
        for b in cdata['bills']:
            print(f"    {b['name']} | {b['partner']} | Total: {b['total']} | Due: {b['residual']} | Status: {b['state']}")
    else:
        print("  No unpaid bills")

# ============================================================
# Step 2: Get bank journals per company (needed for payments)
# ============================================================
print("\n" + "=" * 60)
print("BANK/CASH JOURNALS PER COMPANY")
print("=" * 60)

journals = sr('account.journal', [['type', 'in', ['bank', 'cash']]], 
    ['name', 'type', 'company_id'], limit=30)

journal_map = {}
for j in journals:
    cid = j['company_id'][0] if j['company_id'] else 0
    cname = j['company_id'][1] if j['company_id'] else 'Unknown'
    if cid not in journal_map:
        journal_map[cid] = {'name': cname, 'journals': []}
    journal_map[cid]['journals'].append({'id': j['id'], 'name': j['name'], 'type': j['type']})
    print(f"  [{cid}] {cname}: {j['name']} ({j['type']}) - ID: {j['id']}")

# ============================================================
# Step 3: Get all report menu items available
# ============================================================
print("\n" + "=" * 60)
print("ACCOUNTING REPORT MENUS")
print("=" * 60)

menus = sr('ir.ui.menu', [['name', 'ilike', 'reporting']], ['name', 'parent_id', 'complete_name'], limit=20)
for m in menus:
    print(f"  {m.get('complete_name', m['name'])}")

# Also check for specific report models
print("\n--- Checking report availability ---")
report_models = [
    'account.report',  # Financial reports engine
]
for rm in report_models:
    try:
        count = cnt(rm)
        print(f"  {rm}: {count} records")
    except Exception as e:
        print(f"  {rm}: Error - {e}")

# Get available reports
try:
    reports = sr('account.report', [], ['name', 'country_id'], limit=30)
    for r in reports:
        country = r.get('country_id', [False, ''])[1] if r.get('country_id') else 'Global'
        print(f"  Report: {r['name']} | Country: {country}")
except Exception as e:
    print(f"  Could not fetch reports: {e}")

print("\n" + "=" * 60)
print("SUMMARY - WHAT NEEDS TO BE DONE FOR DEMO")
print("=" * 60)
for cid in sorted(companies_data.keys()):
    cdata = companies_data[cid]
    inv_count = len(cdata['invoices'])
    bill_count = len(cdata['bills'])
    pay_count = cnt('account.payment', [['company_id', '=', cid]])
    print(f"\n{cdata['name']}:")
    print(f"  Unpaid Invoices: {inv_count}")
    print(f"  Unpaid Bills: {bill_count}")
    print(f"  Existing Payments: {pay_count}")
    if pay_count == 0:
        print(f"  >> NEEDS PAYMENTS for demo!")

print("\n=== DONE ===")
