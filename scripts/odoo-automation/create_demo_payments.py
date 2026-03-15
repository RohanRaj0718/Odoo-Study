"""
Create demo payments for each company/branch to support branch-wise reporting demo.
Uses account.payment.create directly (standalone payments).
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def sr(model, domain, fields, limit=100):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

def create(model, vals):
    return models.execute_kw(DB, uid, PASSWORD, model, 'create', [vals])

def action(model, method, ids):
    return models.execute_kw(DB, uid, PASSWORD, model, method, [ids])

# ============================================================
# We'll create payments by registering them against invoices
# using the wizard approach: action_register_payment
# ============================================================

# First, let's try creating standalone payments
# Payment for Krishnadas Group - Customer payment from Anoop Krishnan Nair
print("=== Creating Payments ===\n")

# Krishnadas Group (ID: 1)
# Bank Yes 0024 = journal_id 12
# Partner: Anoop Krishnan Nair - need partner_id
partners = sr('res.partner', [['name', '=', 'Anoop Krishnan Nair']], ['id', 'name'])
anoop_id = partners[0]['id'] if partners else None
print(f"Anoop Krishnan Nair partner_id: {anoop_id}")

partners = sr('res.partner', [['name', '=', 'Deepa Nambiar']], ['id', 'name'])
deepa_id = partners[0]['id'] if partners else None
print(f"Deepa Nambiar partner_id: {deepa_id}")

partners = sr('res.partner', [['name', '=', 'Suresh Menon']], ['id', 'name'])
suresh_id = partners[0]['id'] if partners else None
print(f"Suresh Menon partner_id: {suresh_id}")

partners = sr('res.partner', [['name', '=', 'Skyline Apartments Kochi']], ['id', 'name'])
skyline_id = partners[0]['id'] if partners else None
print(f"Skyline Apartments Kochi partner_id: {skyline_id}")

partners = sr('res.partner', [['name', 'ilike', 'Cochin Laminate']], ['id', 'name'])
cochin_id = partners[0]['id'] if partners else None
print(f"Cochin Laminate House partner_id: {cochin_id}")

partners = sr('res.partner', [['name', 'ilike', 'Kerala Blinds']], ['id', 'name'])
kerala_blinds_id = partners[0]['id'] if partners else None
print(f"Kerala Blinds partner_id: {kerala_blinds_id}")

partners = sr('res.partner', [['name', 'ilike', 'Malabar Furnishing']], ['id', 'name'])
malabar_id = partners[0]['id'] if partners else None
print(f"Malabar Furnishing partner_id: {malabar_id}")

partners = sr('res.partner', [['name', 'ilike', 'Varghese']], ['id', 'name'])
varghese_id = partners[0]['id'] if partners else None
print(f"Varghese & Sons partner_id: {varghese_id}")

payments_to_create = [
    # Krishnadas Group customer payments
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': anoop_id,
        'amount': 5000.0,
        'journal_id': 12,  # Bank Yes 0024
        'company_id': 1,
        'date': '2026-03-03',
    },
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': deepa_id,
        'amount': 2000.0,
        'journal_id': 12,
        'company_id': 1,
        'date': '2026-03-03',
    },
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': varghese_id,
        'amount': 25000.0,
        'journal_id': 12,
        'company_id': 1,
        'date': '2026-03-03',
    },
    # Krishnadas Group vendor payment
    {
        'payment_type': 'outbound',
        'partner_type': 'supplier',
        'partner_id': cochin_id,
        'amount': 3000.0,
        'journal_id': 12,
        'company_id': 1,
        'date': '2026-03-03',
    },
    # KDESIGN INTERIOR customer payment
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': suresh_id,
        'amount': 10000.0,
        'journal_id': 36,  # Bank KDESIGN 7802
        'company_id': 3,
        'date': '2026-03-03',
    },
    # KDESIGN INTERIOR vendor payment
    {
        'payment_type': 'outbound',
        'partner_type': 'supplier',
        'partner_id': kerala_blinds_id,
        'amount': 11250.0,
        'journal_id': 36,
        'company_id': 3,
        'date': '2026-03-03',
    },
    # KDESIGN INTERIOR FURNISHING customer payment
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': skyline_id,
        'amount': 15000.0,
        'journal_id': 21,  # Bank (default for KDESIGN FURNISHING)
        'company_id': 4,
        'date': '2026-03-03',
    },
    # Devika Furniture customer payment (additional)  
    {
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'partner_id': deepa_id,
        'amount': 5000.0,
        'journal_id': 30,  # Bank Devika 4501
        'company_id': 2,
        'date': '2026-03-03',
    },
    # Devika Furniture vendor payment
    {
        'payment_type': 'outbound',
        'partner_type': 'supplier',
        'partner_id': malabar_id,
        'amount': 10000.0,
        'journal_id': 30,
        'company_id': 2,
        'date': '2026-03-03',
    },
]

created_ids = []
for i, pay in enumerate(payments_to_create):
    try:
        pid = create('account.payment', pay)
        desc = f"{pay['payment_type']} {pay['partner_type']} company={pay['company_id']}"
        print(f"  [{i+1}] Created payment ID {pid}: {desc} | Amount {pay['amount']}")
        created_ids.append(pid)
    except Exception as e:
        desc = f"{pay['payment_type']} {pay['partner_type']} company={pay['company_id']}"
        print(f"  [{i+1}] FAILED: {desc} | Error: {e}")

# Now try to confirm/post the payments
print(f"\n=== Confirming {len(created_ids)} payments ===")
for pid in created_ids:
    try:
        action('account.payment', 'action_post', [pid])
        print(f"  Payment {pid}: POSTED successfully")
    except Exception as e:
        print(f"  Payment {pid}: Post failed - {e}")

# Final count
print("\n=== FINAL PAYMENT COUNT PER COMPANY ===")
companies = sr('res.company', [], ['name'])
for c in companies:
    total = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', 
        [[['company_id', '=', c['id']]]])
    posted = models.execute_kw(DB, uid, PASSWORD, 'account.payment', 'search_count', 
        [[['company_id', '=', c['id']], ['state', '!=', 'draft']]])
    print(f"  {c['name']}: Total={total}, Posted/Confirmed={posted}")

print("\n=== DONE ===")
