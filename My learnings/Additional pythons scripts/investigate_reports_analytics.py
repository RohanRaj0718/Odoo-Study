"""
Comprehensive Investigation: Analytic Accounting & Branch-wise Reporting
========================================================================
Checks the practice database (mirror of client PSI database) to determine:
1. Current setup — companies, branches, warehouses, analytic accounts/plans
2. All accounting reports available and their analytic support
3. All methods to view branch-wise reports
4. Warehouse-per-branch reporting capabilities
5. What journal items have analytic distribution vs what don't
"""

import xmlrpc.client
import sys
import json
from collections import Counter, defaultdict

# ── CONNECTION ──
URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("❌ Authentication failed!")
    sys.exit(1)
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def sr(model, domain, fields, limit=0, order=''):
    kw = {'fields': fields}
    if limit: kw['limit'] = limit
    if order: kw['order'] = order
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

def search(model, domain, limit=0):
    kw = {}
    if limit: kw['limit'] = limit
    return models.execute_kw(DB, uid, PASSWORD, model, 'search', [domain], kw)

def count(model, domain):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])

def fields_get(model, attrs=['string','type','relation','selection']):
    return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], {'attributes': attrs})

print("=" * 80)
print("  COMPREHENSIVE INVESTIGATION: ANALYTICS & BRANCH-WISE REPORTING")
print("=" * 80)
print(f"  Database: {DB} | URL: {URL}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: CURRENT DATABASE SETUP
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 1: CURRENT DATABASE STRUCTURE")
print("═" * 80)

# 1a. Companies
print("\n📋 COMPANIES:")
companies = sr('res.company', [], ['name', 'parent_id', 'city', 'state_id', 'currency_id'])
for c in sorted(companies, key=lambda x: x['id']):
    parent = c['parent_id'][1] if c['parent_id'] else 'ROOT (Top-level)'
    state = c['state_id'][1] if c['state_id'] else 'N/A'
    currency = c['currency_id'][1] if c['currency_id'] else 'N/A'
    print(f"  [{c['id']}] {c['name']}")
    print(f"      Parent: {parent} | City: {c['city']} | State: {state} | Currency: {currency}")

# 1b. Branches
print("\n🏢 BRANCHES (res.company — checking branch_ids or parent relationships):")
for c in companies:
    children = [x for x in companies if x.get('parent_id') and x['parent_id'][0] == c['id']]
    if children:
        print(f"  {c['name']} has {len(children)} branches:")
        for ch in children:
            print(f"    → {ch['name']}")

# 1c. Warehouses
print("\n📦 WAREHOUSES:")
whs = sr('stock.warehouse', [], ['name', 'code', 'company_id', 'partner_id', 'lot_stock_id'])
for w in sorted(whs, key=lambda x: x['company_id'][0] if x['company_id'] else 0):
    co = w['company_id'][1] if w['company_id'] else 'N/A'
    print(f"  [{w['id']}] {w['name']} ({w['code']}) — Company: {co}")

# 1d. Stock Locations (internal)
print("\n📍 INTERNAL STOCK LOCATIONS:")
locs = sr('stock.location', [['usage', '=', 'internal']], ['complete_name', 'company_id', 'warehouse_id'])
for loc in sorted(locs, key=lambda x: x['complete_name']):
    co = loc['company_id'][1] if loc['company_id'] else 'SHARED'
    wh = loc['warehouse_id'][1] if loc['warehouse_id'] else 'N/A'
    print(f"  {loc['complete_name']} — Company: {co} | Warehouse: {wh}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: ANALYTIC ACCOUNTING SETUP
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 2: ANALYTIC ACCOUNTING SETUP")
print("═" * 80)

# 2a. Analytic Plans
print("\n📊 ANALYTIC PLANS:")
try:
    plans = sr('account.analytic.plan', [], ['name', 'company_id', 'parent_id', 'color', 'default_applicability'])
    if plans:
        for p in plans:
            co = p['company_id'][1] if p.get('company_id') and p['company_id'] else 'ALL'
            parent = p['parent_id'][1] if p.get('parent_id') and p['parent_id'] else 'Root'
            print(f"  [{p['id']}] {p['name']} — Company: {co} | Parent: {parent}")
            print(f"      Default Applicability: {p.get('default_applicability', 'N/A')}")
    else:
        print("  ⚠️ No analytic plans found!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 2b. Analytic Accounts
print("\n📈 ANALYTIC ACCOUNTS:")
try:
    analytics = sr('account.analytic.account', [], ['name', 'plan_id', 'company_id', 'code', 'active'])
    if analytics:
        for a in analytics:
            co = a['company_id'][1] if a.get('company_id') and a['company_id'] else 'ALL'
            plan = a['plan_id'][1] if a.get('plan_id') and a['plan_id'] else 'N/A'
            print(f"  [{a['id']}] {a['name']} (Code: {a.get('code','')}) — Plan: {plan} | Company: {co}")
    else:
        print("  ⚠️ No analytic accounts found!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 2c. Check analytic lines
print("\n📝 ANALYTIC LINES (sample):")
try:
    al_count = count('account.analytic.line', [])
    print(f"  Total analytic lines: {al_count}")
    if al_count > 0:
        al_sample = sr('account.analytic.line', [], 
            ['name', 'account_id', 'amount', 'date', 'general_account_id', 'company_id', 'move_line_id'], 
            limit=10, order='id desc')
        for al in al_sample:
            acc = al['account_id'][1] if al.get('account_id') and al['account_id'] else 'N/A'
            gen = al['general_account_id'][1] if al.get('general_account_id') and al['general_account_id'] else 'N/A'
            co = al['company_id'][1] if al.get('company_id') and al['company_id'] else 'N/A'
            print(f"    {al['date']} | {al['name']} | Analytic: {acc} | GL Acct: {gen} | Amount: {al['amount']} | Company: {co}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: JOURNAL ENTRIES — ANALYTIC DISTRIBUTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 3: JOURNAL ITEMS — WHICH HAVE ANALYTIC TAGS?")
print("═" * 80)

# Check account.move.line fields for analytic
print("\n🔍 Checking account.move.line fields related to analytics...")
try:
    aml_fields = fields_get('account.move.line')
    analytic_fields = {k: v for k, v in aml_fields.items() if 'analytic' in k.lower()}
    print(f"  Analytic-related fields in journal items:")
    for fname, finfo in sorted(analytic_fields.items()):
        print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Sample journal items - check which account types have analytic distribution
print("\n📊 Analyzing journal items by account type & analytic distribution...")
try:
    # Get all account types
    accounts = sr('account.account', [], ['name', 'code', 'account_type'])
    acct_type_map = {a['id']: a for a in accounts}
    
    # Get journal items with analytic info
    move_lines = sr('account.move.line', [['parent_state','=','posted']], 
        ['account_id', 'analytic_distribution', 'debit', 'credit', 'company_id'],
        limit=500, order='id desc')
    
    # Analyze: which account types have analytic distribution?
    type_with_analytic = defaultdict(int)
    type_without_analytic = defaultdict(int)
    type_total = defaultdict(int)
    
    for ml in move_lines:
        acct_id = ml['account_id'][0] if ml['account_id'] else None
        if acct_id and acct_id in acct_type_map:
            acct_info = acct_type_map[acct_id]
            atype = acct_info['account_type']
            has_analytic = bool(ml.get('analytic_distribution'))
            type_total[atype] += 1
            if has_analytic:
                type_with_analytic[atype] += 1
            else:
                type_without_analytic[atype] += 1
    
    print(f"\n  {'Account Type':<40} {'Total':<8} {'Has Analytic':<15} {'No Analytic':<15} {'%'}")
    print(f"  {'-'*40} {'-'*8} {'-'*15} {'-'*15} {'-'*5}")
    for atype in sorted(type_total.keys()):
        total = type_total[atype]
        with_a = type_with_analytic.get(atype, 0)
        without_a = type_without_analytic.get(atype, 0)
        pct = f"{(with_a/total*100):.0f}%" if total > 0 else "N/A"
        print(f"  {atype:<40} {total:<8} {with_a:<15} {without_a:<15} {pct}")
    
    print(f"\n  KEY INSIGHT:")
    bs_types = ['asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current', 
                'asset_prepayments', 'asset_fixed', 'liability_payable', 'liability_current',
                'liability_non_current', 'equity', 'equity_unaffected', 'off_balance']
    pl_types = ['income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost']
    
    bs_with = sum(type_with_analytic.get(t, 0) for t in bs_types)
    bs_total = sum(type_total.get(t, 0) for t in bs_types)
    pl_with = sum(type_with_analytic.get(t, 0) for t in pl_types)
    pl_total = sum(type_total.get(t, 0) for t in pl_types)
    
    print(f"  Balance Sheet accounts: {bs_with}/{bs_total} have analytic ({(bs_with/bs_total*100):.1f}% if total > 0)" if bs_total > 0 else "  Balance Sheet: No entries")
    print(f"  P&L accounts:          {pl_with}/{pl_total} have analytic ({(pl_with/pl_total*100):.1f}%)" if pl_total > 0 else "  P&L: No entries")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: ALL AVAILABLE ACCOUNTING REPORTS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 4: ALL ACCOUNTING REPORTS — ANALYTIC SUPPORT CHECK")
print("═" * 80)

# Check account.report model (Odoo 17/18/19 new report engine)
print("\n📋 Checking account.report model...")
try:
    reports = sr('account.report', [], ['name', 'root_report_id', 'country_id', 'availability_condition',
                                         'filter_analytic', 'filter_journals', 'filter_multi_company',
                                         'filter_date_range', 'filter_partner', 'filter_account_type',
                                         'filter_unfold_all', 'filter_hierarchy'])
    print(f"  Found {len(reports)} accounting reports\n")
    
    print(f"  {'#':<4} {'Report Name':<45} {'Analytic':<10} {'Journals':<10} {'Partner':<10} {'Multi-Co':<10}")
    print(f"  {'-'*4} {'-'*45} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    
    analytic_yes = []
    analytic_no = []
    
    for r in sorted(reports, key=lambda x: x['name']):
        has_anal = '✅ YES' if r.get('filter_analytic') else '❌ NO'
        has_jour = '✅' if r.get('filter_journals') else '❌'
        has_part = '✅' if r.get('filter_partner') else '❌'
        has_mc = '✅' if r.get('filter_multi_company') else '❌'
        
        print(f"  {r['id']:<4} {r['name']:<45} {has_anal:<10} {has_jour:<10} {has_part:<10} {has_mc:<10}")
        
        if r.get('filter_analytic'):
            analytic_yes.append(r['name'])
        else:
            analytic_no.append(r['name'])
    
    print(f"\n  ═══ SUMMARY ═══")
    print(f"\n  ✅ Reports WITH Analytic Filter ({len(analytic_yes)}):")
    for name in sorted(analytic_yes):
        print(f"    • {name}")
    
    print(f"\n  ❌ Reports WITHOUT Analytic Filter ({len(analytic_no)}):")
    for name in sorted(analytic_no):
        print(f"    • {name}")
        
except Exception as e:
    print(f"  ❌ account.report not available or error: {e}")
    
    # Fallback: check ir.actions.report for accounting
    print("\n  Trying ir.actions.report...")
    try:
        actions = sr('ir.actions.report', [['model','like','account']], ['name', 'model', 'report_name'])
        for a in actions:
            print(f"    • {a['name']} — model: {a['model']}")
    except Exception as e2:
        print(f"  ❌ Error: {e2}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: CHECK OTHER FILTER/GROUPBY OPTIONS FOR REPORTS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 5: ALL AVAILABLE REPORT FILTERS & GROUPBY OPTIONS")
print("═" * 80)

# Check all fields on account.report
try:
    report_fields = fields_get('account.report')
    filter_fields = {k: v for k, v in report_fields.items() if 'filter' in k.lower()}
    print("\n  All filter-related fields on account.report:")
    for fname, finfo in sorted(filter_fields.items()):
        print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: JOURNAL ITEMS — CAN WE FILTER BY WAREHOUSE?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 6: WAREHOUSE / STOCK RELATED FIELDS ON JOURNAL ITEMS")
print("═" * 80)

try:
    aml_fields = fields_get('account.move.line')
    # Check for warehouse, stock, location related fields
    relevant = {k: v for k, v in aml_fields.items() 
                if any(w in k.lower() for w in ['warehouse', 'stock', 'location', 'branch'])}
    if relevant:
        print("  Fields related to warehouse/stock/branch on journal items:")
        for fname, finfo in sorted(relevant.items()):
            print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
    else:
        print("  ⚠️ NO warehouse/stock/location/branch fields found on account.move.line!")
        print("     → This means journal entries have NO direct link to warehouses")
    
    # Check on account.move (parent entry)
    am_fields = fields_get('account.move')
    relevant2 = {k: v for k, v in am_fields.items()
                if any(w in k.lower() for w in ['warehouse', 'stock', 'location', 'branch'])}
    if relevant2:
        print("\n  Fields on account.move (journal entry header):")
        for fname, finfo in sorted(relevant2.items()):
            print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
    else:
        print("\n  ⚠️ NO warehouse/stock/location/branch fields on account.move either!")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 7: INVOICES/BILLS — CHECK ANALYTIC DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 7: INVOICES & BILLS — ANALYTIC DISTRIBUTION")
print("═" * 80)

try:
    # Check posted invoices
    invoices = sr('account.move', [['move_type', 'in', ['out_invoice', 'in_invoice']], ['state','=','posted']], 
        ['name', 'move_type', 'partner_id', 'amount_total', 'company_id', 'invoice_date'],
        limit=20, order='id desc')
    
    print(f"  Found {len(invoices)} recent posted invoices/bills")
    
    for inv in invoices[:5]:
        print(f"\n  📄 {inv['name']} ({inv['move_type']}) — {inv['partner_id'][1] if inv['partner_id'] else 'N/A'}")
        print(f"     Amount: {inv['amount_total']} | Company: {inv['company_id'][1] if inv['company_id'] else 'N/A'}")
        
        # Get lines with analytic
        lines = sr('account.move.line', [['move_id', '=', inv['id']]], 
            ['name', 'account_id', 'debit', 'credit', 'analytic_distribution'])
        for line in lines:
            acct = line['account_id'][1] if line['account_id'] else 'N/A'
            ad = line.get('analytic_distribution', {})
            has_ad = '✅' if ad else '❌'
            print(f"     {has_ad} {acct:<40} D:{line['debit']:>10.2f} C:{line['credit']:>10.2f} | Analytic: {json.dumps(ad) if ad else 'NONE'}")

except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 8: PAYMENTS — ANALYTIC DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 8: PAYMENTS — ANALYTIC ON BANK/CASH ENTRIES?")
print("═" * 80)

try:
    payments = sr('account.payment', [['state', '=', 'posted']], 
        ['name', 'amount', 'payment_type', 'journal_id', 'company_id'],
        limit=10, order='id desc')
    
    print(f"  Found {len(payments)} recent posted payments")
    
    for pay in payments[:5]:
        journal = pay['journal_id'][1] if pay['journal_id'] else 'N/A'
        co = pay['company_id'][1] if pay['company_id'] else 'N/A'
        print(f"\n  💰 {pay['name']} | {pay['payment_type']} | Amount: {pay['amount']} | Journal: {journal} | Company: {co}")
        
        # Get journal entry lines
        # Find the move_id via account.move
        moves = sr('account.move', [['payment_id', '=', pay['id']]], ['name'], limit=1)
        if moves:
            lines = sr('account.move.line', [['move_id', '=', moves[0]['id']]], 
                ['account_id', 'debit', 'credit', 'analytic_distribution'])
            for line in lines:
                acct = line['account_id'][1] if line['account_id'] else 'N/A'
                ad = line.get('analytic_distribution', {})
                has_ad = '✅' if ad else '❌'
                print(f"     {has_ad} {acct:<40} D:{line['debit']:>10.2f} C:{line['credit']:>10.2f} | Analytic: {json.dumps(ad) if ad else 'NONE'}")

except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 9: STOCK VALUATION JOURNAL ENTRIES
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 9: STOCK VALUATION ENTRIES — ANALYTIC?")
print("═" * 80)

try:
    # Find stock journals
    stock_journals = sr('account.journal', [['type', '=', 'general']], ['name', 'code', 'company_id'])
    print(f"  General journals (may include stock): {[j['name'] for j in stock_journals]}")
    
    # Check stock valuation layer
    svl_fields = fields_get('stock.valuation.layer')
    analytic_svl = {k:v for k,v in svl_fields.items() if 'analytic' in k.lower()}
    print(f"\n  Analytic fields on stock.valuation.layer: {list(analytic_svl.keys()) if analytic_svl else 'NONE'}")
    
    # Check stock moves for analytic
    sm_fields = fields_get('stock.move')
    analytic_sm = {k:v for k,v in sm_fields.items() if 'analytic' in k.lower()}
    print(f"  Analytic fields on stock.move: {list(analytic_sm.keys()) if analytic_sm else 'NONE'}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 10: AVAILABLE GROUPBY / PIVOT OPTIONS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 10: JOURNAL ITEMS — ALL GROUPBY OPTIONS")
print("═" * 80)

try:
    aml_fields = fields_get('account.move.line')
    # Show fields that are good candidates for groupby
    group_candidates = {}
    for fname, finfo in aml_fields.items():
        if finfo.get('type') in ['many2one', 'selection']:
            group_candidates[fname] = finfo
    
    print(f"  Groupable fields on journal items ({len(group_candidates)}):")
    useful_ones = ['company_id', 'journal_id', 'account_id', 'partner_id', 'analytic_distribution',
                   'currency_id', 'product_id', 'move_id', 'tax_ids', 'account_type',
                   'parent_state', 'display_type', 'move_type']
    for fname in useful_ones:
        if fname in aml_fields:
            finfo = aml_fields[fname]
            print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 11: CHECK IF REPORT LINE MODEL HAS ANALYTIC
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 11: REPORT LINE & REPORT EXPRESSION MODELS")
print("═" * 80)

try:
    # Check account.report.line
    models_to_check = ['account.report.line', 'account.report.expression']
    for model_name in models_to_check:
        try:
            f = fields_get(model_name)
            print(f"\n  Fields on {model_name} ({len(f)} fields):")
            for fname, finfo in sorted(f.items()):
                if any(w in fname.lower() for w in ['analytic', 'group', 'filter', 'domain', 'formula']):
                    print(f"    • {fname}: {finfo.get('string','?')} (type: {finfo.get('type','?')})")
        except:
            print(f"  {model_name} — not accessible")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 12: CHECK AGED RECEIVABLE / PAYABLE REPORT DETAILS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 12: SPECIFIC REPORT DETAILS — AGED RECEIVABLE/PAYABLE, TAX, etc.")
print("═" * 80)

try:
    key_reports = sr('account.report', 
        [['name', 'in', ['Aged Receivable', 'Aged Payable', 'Tax Report', 'Balance Sheet',
                          'Profit and Loss', 'General Ledger', 'Trial Balance', 'Cash Flow Statement',
                          'Partner Ledger', 'Journal Report']]], 
        ['name', 'filter_analytic', 'filter_journals', 'filter_partner', 'filter_multi_company',
         'filter_account_type', 'filter_date_range', 'filter_hierarchy', 'filter_unfold_all',
         'default_opening_date_filter'])
    
    for r in sorted(key_reports, key=lambda x: x['name']):
        print(f"\n  📊 {r['name']}:")
        for k, v in sorted(r.items()):
            if k not in ['id', 'name']:
                print(f"     {k}: {v}")
                
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 13: INTER-COMPANY / BRANCH TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 13: BRANCH/COMPANY SWITCHING CAPABILITIES")
print("═" * 80)

try:
    # Check user's company access
    users = sr('res.users', [['id', '=', uid]], ['company_id', 'company_ids', 'name'])
    if users:
        u = users[0]
        co = u['company_id'][1] if u['company_id'] else 'N/A'
        cos = u['company_ids'] if u['company_ids'] else []
        print(f"  Current user: {u['name']}")
        print(f"  Active company: {co}")
        print(f"  Allowed company IDs: {cos}")
        
        # Get names for all allowed companies
        if cos:
            allowed = sr('res.company', [['id', 'in', cos]], ['name'])
            print(f"  Allowed companies: {[a['name'] for a in allowed]}")

except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 14: CHECK ANALYTIC PLAN APPLICABILITY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 14: ANALYTIC PLAN APPLICABILITY RULES")
print("═" * 80)

try:
    # Check account.analytic.applicability
    apps = sr('account.analytic.applicability', [], 
        ['analytic_plan_id', 'business_domain', 'applicability', 'product_categ_id', 'company_id'])
    if apps:
        for a in apps:
            plan = a['analytic_plan_id'][1] if a.get('analytic_plan_id') and a['analytic_plan_id'] else 'N/A'
            print(f"  Plan: {plan} | Domain: {a.get('business_domain','?')} | Applicability: {a.get('applicability','?')}")
    else:
        print("  No applicability rules configured")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION 15: CHECK BUDGET MODEL
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  SECTION 15: BUDGET MODULE & ANALYTIC")
print("═" * 80)

try:
    budget_fields = fields_get('account.budget.line')
    print("  Budget line fields (analytic related):")
    for k, v in budget_fields.items():
        if 'analytic' in k.lower():
            print(f"    • {k}: {v.get('string','?')}")
except Exception as e:
    print(f"  Budget model not available: {e}")

# ═══════════════════════════════════════════════════════════════════
# FINAL: SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  FINAL SUMMARY")
print("═" * 80)
print("""
  This script has checked:
  1. ✅ Database structure (companies, branches, warehouses)
  2. ✅ Analytic plans and accounts
  3. ✅ Which journal items carry analytic distribution
  4. ✅ All accounting reports and their analytic filter support
  5. ✅ Warehouse/branch fields on journal entries
  6. ✅ Report filter capabilities
  7. ✅ Stock valuation analytic support
  8. ✅ Company switching access
  
  See output above for detailed analysis.
""")

print("INVESTIGATION COMPLETE!")
