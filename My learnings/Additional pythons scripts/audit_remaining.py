"""Get remaining audit data."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=100):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})
    except Exception as e:
        return f"Error: {e}"

def cnt(model, domain=[]):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])
    except:
        return 0

print("=== PAYMENTS ===")
payments = sr('account.payment', [], ['name', 'partner_id', 'company_id', 'state', 'payment_type', 'amount', 'date', 'journal_id'])
for p in payments:
    print(p)

print("\n=== JOURNAL ENTRIES COUNT PER COMPANY ===")
companies = sr('res.company', [], ['name'])
for c in companies:
    total = cnt('account.move', [['company_id', '=', c['id']]])
    posted = cnt('account.move', [['company_id', '=', c['id']], ['state', '=', 'posted']])
    inv = cnt('account.move', [['company_id', '=', c['id']], ['move_type', 'in', ['out_invoice']]])
    bill = cnt('account.move', [['company_id', '=', c['id']], ['move_type', 'in', ['in_invoice']]])
    pay = cnt('account.payment', [['company_id', '=', c['id']]])
    print(f"  {c['name']}: Total JE={total}, Posted={posted}, Invoices={inv}, Bills={bill}, Payments={pay}")

print("\n=== TAXES ===")
taxes = sr('account.tax', [], ['name', 'type_tax_use', 'amount', 'company_id'], limit=30)
for t in taxes:
    cid = t.get('company_id')
    cname = cid[1] if cid and isinstance(cid, list) else str(cid)
    pct = t.get('amount', 0)
    print(f"  {t['name']} | Use: {t.get('type_tax_use','')} | Rate: {pct} | Company: {cname}")

print("\n=== CUSTOMERS ===")
custs = sr('res.partner', [['customer_rank', '>', 0]], ['name', 'company_id', 'vat'], limit=20)
for c in custs:
    cid = c.get('company_id')
    cname = cid[1] if cid and isinstance(cid, list) else 'All'
    print(f"  {c['name']} | Company: {cname} | GST: {c.get('vat','')}")

print("\n=== VENDORS ===")
vends = sr('res.partner', [['supplier_rank', '>', 0]], ['name', 'company_id', 'vat'], limit=20)
for v in vends:
    cid = v.get('company_id')
    cname = cid[1] if cid and isinstance(cid, list) else 'All'
    print(f"  {v['name']} | Company: {cname} | GST: {v.get('vat','')}")

print("\n=== DONE ===")
