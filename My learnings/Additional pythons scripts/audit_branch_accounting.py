"""
Comprehensive audit of client-cient database:
- Accounting setup per company/branch
- Journals per company
- Existing invoices, bills, payments per company
- Chart of accounts structure
- Partner Ledger data availability
"""
import xmlrpc.client
import json

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=200):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})
    except Exception as e:
        return f"Error: {e}"

def count(model, domain=[]):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])
    except:
        return 0

# ============ COMPANIES ============
print("=" * 60)
print("1. COMPANIES")
print("=" * 60)
companies = sr('res.company', [], ['name', 'parent_id', 'vat', 'street', 'city', 'state_id', 'country_id', 'currency_id'])
for c in companies:
    print(f"\n  [{c['id']}] {c['name']}")
    print(f"    Parent: {c.get('parent_id', [False, 'None'])}")
    print(f"    VAT/GSTIN: {c.get('vat', 'None')}")
    print(f"    Location: {c.get('city', '')}, {c.get('state_id', ['',''])[1] if c.get('state_id') else ''}")
    print(f"    Currency: {c.get('currency_id', ['',''])[1] if c.get('currency_id') else ''}")

# ============ JOURNALS PER COMPANY ============
print("\n" + "=" * 60)
print("2. ACCOUNTING JOURNALS PER COMPANY")
print("=" * 60)
journals = sr('account.journal', [], ['name', 'type', 'code', 'company_id'])
by_company = {}
for j in journals:
    cname = j['company_id'][1] if j.get('company_id') else 'Shared'
    by_company.setdefault(cname, []).append(j)
for cname, jlist in sorted(by_company.items()):
    print(f"\n  Company: {cname}")
    for j in jlist:
        print(f"    [{j['code']}] {j['name']} (type: {j['type']})")

# ============ CHART OF ACCOUNTS ============
print("\n" + "=" * 60)
print("3. CHART OF ACCOUNTS (sample)")
print("=" * 60)
accounts = sr('account.account', [], ['code', 'name', 'account_type', 'company_ids'], limit=30)
if accounts and not isinstance(accounts, str):
    for a in accounts:
        cids = a.get('company_ids', [])
        print(f"  {a.get('code', '')} | {a['name']} | Type: {a.get('account_type', '')} | Companies: {cids}")
else:
    print(f"  Result: {accounts}")

# ============ INVOICES PER COMPANY ============
print("\n" + "=" * 60)
print("4. CUSTOMER INVOICES")
print("=" * 60)
invoices = sr('account.move', [['move_type', 'in', ['out_invoice', 'out_refund']]], 
              ['name', 'partner_id', 'company_id', 'state', 'move_type', 'amount_total', 'invoice_date', 'payment_state'])
if invoices and not isinstance(invoices, str):
    for inv in invoices:
        print(f"  {inv['name']} | Partner: {inv.get('partner_id', ['',''])[1]} | Company: {inv.get('company_id', ['',''])[1]} | State: {inv['state']} | Amount: {inv.get('amount_total', 0)} | Payment: {inv.get('payment_state', '')} | Date: {inv.get('invoice_date', '')}")
else:
    print(f"  Result: {invoices}")

print(f"\n  Total customer invoices: {count('account.move', [['move_type', 'in', ['out_invoice', 'out_refund']]])}")

# ============ VENDOR BILLS PER COMPANY ============
print("\n" + "=" * 60)
print("5. VENDOR BILLS")
print("=" * 60)
bills = sr('account.move', [['move_type', 'in', ['in_invoice', 'in_refund']]], 
           ['name', 'partner_id', 'company_id', 'state', 'move_type', 'amount_total', 'invoice_date', 'payment_state'])
if bills and not isinstance(bills, str):
    for b in bills:
        print(f"  {b['name']} | Partner: {b.get('partner_id', ['',''])[1]} | Company: {b.get('company_id', ['',''])[1]} | State: {b['state']} | Amount: {b.get('amount_total', 0)} | Payment: {b.get('payment_state', '')} | Date: {b.get('invoice_date', '')}")
else:
    print(f"  Result: {bills}")

print(f"\n  Total vendor bills: {count('account.move', [['move_type', 'in', ['in_invoice', 'in_refund']]])}")

# ============ PAYMENTS PER COMPANY ============
print("\n" + "=" * 60)
print("6. PAYMENTS")
print("=" * 60)
payments = sr('account.payment', [], 
              ['name', 'partner_id', 'company_id', 'state', 'payment_type', 'amount', 'date', 'journal_id'])
if payments and not isinstance(payments, str):
    for p in payments:
        partner = p.get('partner_id')
        pname = partner[1] if partner and isinstance(partner, list) else str(partner)
        company = p.get('company_id')
        cname = company[1] if company and isinstance(company, list) else str(company)
        journal = p.get('journal_id')
        jname = journal[1] if journal and isinstance(journal, list) else str(journal)
        print(f"  {p['name']} | Partner: {pname} | Company: {cname} | Type: {p.get('payment_type', '')} | Amount: {p.get('amount', 0)} | State: {p['state']} | Journal: {jname} | Date: {p.get('date', '')}")
else:
    print(f"  Result: {payments}")

print(f"\n  Total payments: {count('account.payment', [])}")

# ============ JOURNAL ENTRIES (ACCOUNTING ENTRIES) ============
print("\n" + "=" * 60)
print("7. JOURNAL ENTRIES COUNT PER COMPANY")
print("=" * 60)
for c in companies:
    cnt = count('account.move', [['company_id', '=', c['id']]])
    posted = count('account.move', [['company_id', '=', c['id']], ['state', '=', 'posted']])
    print(f"  {c['name']}: Total={cnt}, Posted={posted}")

# ============ BANK ACCOUNTS / JOURNALS ============
print("\n" + "=" * 60)
print("8. BANK JOURNALS")
print("=" * 60)
bank_journals = sr('account.journal', [['type', 'in', ['bank', 'cash']]], 
                   ['name', 'type', 'code', 'company_id', 'bank_account_id'])
for bj in bank_journals:
    print(f"  {bj['name']} ({bj['type']}) | Code: {bj['code']} | Company: {bj.get('company_id', ['',''])[1]} | Bank Acct: {bj.get('bank_account_id', [False, 'None'])}")

# ============ FISCAL POSITIONS ============
print("\n" + "=" * 60)
print("9. FISCAL POSITIONS")
print("=" * 60)
fps = sr('account.fiscal.position', [], ['name', 'company_id'])
if fps and not isinstance(fps, str):
    for fp in fps:
        print(f"  {fp['name']} | Company: {fp.get('company_id', ['',''])[1]}")
else:
    print(f"  Result: {fps}")

# ============ TAXES ============
print("\n" + "=" * 60)
print("10. TAXES (sample)")
print("=" * 60)
taxes = sr('account.tax', [], ['name', 'type_tax_use', 'amount', 'company_id'], limit=20)
for t in taxes:
    print(f"  {t['name']} | Use: {t.get('type_tax_use', '')} | Rate: {t.get('amount', '')}% | Company: {t.get('company_id', ['',''])[1]}")

# ============ CONTACTS WITH ACCOUNTING RELEVANCE ============
print("\n" + "=" * 60)
print("11. CUSTOMERS/VENDORS WITH TRANSACTIONS")
print("=" * 60)
partners = sr('res.partner', [['customer_rank', '>', 0]], ['name', 'company_id', 'customer_rank', 'supplier_rank', 'vat'], limit=20)
print("  --- Customers ---")
for p in partners:
    print(f"  {p['name']} | Company: {p.get('company_id', [False, 'All'])} | CustRank: {p.get('customer_rank',0)} | SupRank: {p.get('supplier_rank',0)} | GST: {p.get('vat','')}")

partners_v = sr('res.partner', [['supplier_rank', '>', 0]], ['name', 'company_id', 'supplier_rank', 'vat'], limit=20)
print("\n  --- Vendors ---")
for p in partners_v:
    print(f"  {p['name']} | Company: {p.get('company_id', [False, 'All'])} | SupRank: {p.get('supplier_rank',0)} | GST: {p.get('vat','')}")

# ============ PRODUCTS WITH ACCOUNTING ============
print("\n" + "=" * 60)
print("12. PRODUCTS - TYPE & INVOICING")
print("=" * 60)
products = sr('product.template', [], ['name', 'type', 'list_price', 'standard_price', 'company_id', 'taxes_id'], limit=15)
for pr in products:
    print(f"  {pr['name']} | Type: {pr.get('type','')} | Sale: {pr.get('list_price',0)} | Cost: {pr.get('standard_price',0)} | Company: {pr.get('company_id', [False, 'All'])} | Taxes: {pr.get('taxes_id', [])}")

print("\n\n=== AUDIT COMPLETE ===")
