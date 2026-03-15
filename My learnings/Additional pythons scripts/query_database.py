"""
Query the exact data in the Odoo database to build a precise reconciliation guide.
"""
import xmlrpc.client
import sys

URL = "https://demo-company15.odoo.com"
DB = "demo-company15"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def sr(model, domain, fields):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'order': 'id asc'})

print("=" * 70)
print("DATABASE STATE REPORT")
print("=" * 70)

# Invoices
print("\n── CUSTOMER INVOICES (Posted) ──")
invoices = sr('account.move', [['move_type', '=', 'out_invoice'], ['state', '=', 'posted']], 
              ['name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date', 'payment_state'])
for inv in invoices:
    print(f"  {inv['name']:20s} | {inv['partner_id'][1]:30s} | Total: ${inv['amount_total']:>10,.2f} | Due: ${inv['amount_residual']:>10,.2f} | {inv['payment_state']}")

# Bills
print("\n── VENDOR BILLS (Posted) ──")
bills = sr('account.move', [['move_type', '=', 'in_invoice'], ['state', '=', 'posted']], 
           ['name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date', 'payment_state'])
for b in bills:
    print(f"  {b['name']:20s} | {b['partner_id'][1]:30s} | Total: ${b['amount_total']:>10,.2f} | Due: ${b['amount_residual']:>10,.2f} | {b['payment_state']}")

# Bank transactions
print("\n── BANK TRANSACTIONS (To Reconcile) ──")
txns = sr('account.bank.statement.line', [['journal_id.code', '=', 'BNK1']], 
          ['date', 'payment_ref', 'partner_id', 'amount', 'is_reconciled'])
reconciled = 0
unreconciled = 0
for t in txns:
    partner = t['partner_id'][1] if t['partner_id'] else '—'
    status = "✅ DONE" if t['is_reconciled'] else "⬜ TODO"
    if t['is_reconciled']:
        reconciled += 1
    else:
        unreconciled += 1
    print(f"  {status} | {t['date']} | ${t['amount']:>10,.2f} | {t['payment_ref'][:45]:45s} | {partner}")

print(f"\n  Summary: {unreconciled} to reconcile, {reconciled} already reconciled")
print(f"  Total transactions: {len(txns)}")
