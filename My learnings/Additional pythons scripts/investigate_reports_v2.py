"""
DEEP DIVE Part 2: Correct field discovery + report analysis for Odoo 19 (saas-19.1)
Also creates test transactions WITH analytic distribution to verify reporting.
"""

import xmlrpc.client
import sys
import json
from collections import defaultdict

# ── CONNECTION ──
URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("❌ Auth failed!"); sys.exit(1)
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

def create(model, vals):
    return models.execute_kw(DB, uid, PASSWORD, model, 'create', [vals])

def write(model, ids, vals):
    return models.execute_kw(DB, uid, PASSWORD, model, 'write', [ids, vals])

def execute(model, method, args=[], kwargs={}):
    return models.execute_kw(DB, uid, PASSWORD, model, method, args, kwargs)

print("=" * 80)
print("  DEEP DIVE #2: ODOO 19 REPORTS & ANALYTIC — CORRECTED")
print("=" * 80)

# ═══════════════════════════════════════════════════════════════════
# PART A: DISCOVER EXACT FIELDS ON account.report
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART A: ALL FIELDS ON account.report MODEL")
print("═" * 80)

report_fields = fields_get('account.report')
print(f"\n  Total fields: {len(report_fields)}")
print("\n  ALL fields:")
for fname, finfo in sorted(report_fields.items()):
    ftype = finfo.get('type','?')
    label = finfo.get('string','?')
    print(f"    • {fname:<40} {ftype:<15} {label}")

# ═══════════════════════════════════════════════════════════════════
# PART B: QUERY ALL REPORTS WITH CORRECT FIELDS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART B: ALL ACCOUNTING REPORTS WITH THEIR FILTERS")
print("═" * 80)

# Get only fields we know exist (from Part A)
filter_field_names = [k for k in report_fields.keys() if 'filter' in k.lower()]
base_fields = ['name', 'root_report_id', 'country_id', 'availability_condition'] + filter_field_names

try:
    reports = sr('account.report', [], base_fields)
    print(f"\n  Found {len(reports)} reports")
    
    print(f"\n  Filter fields available: {filter_field_names}")
    
    print(f"\n  {'ID':<5} {'Report Name':<50} ", end="")
    for ff in filter_field_names:
        short = ff.replace('filter_','').replace('default_','')[:12]
        print(f"{short:<14}", end="")
    print()
    print(f"  {'-'*5} {'-'*50} ", end="")
    for ff in filter_field_names:
        print(f"{'-'*14}", end="")
    print()
    
    for r in sorted(reports, key=lambda x: x['name']):
        root = r['root_report_id'][1] if r.get('root_report_id') and r['root_report_id'] else ''
        display_name = r['name']
        if root and root != display_name:
            display_name = f"{display_name} ({root})"
        
        print(f"  {r['id']:<5} {display_name:<50} ", end="")
        for ff in filter_field_names:
            val = r.get(ff, '')
            if val is True:
                print(f"{'✅ YES':<14}", end="")
            elif val is False:
                print(f"{'❌ NO':<14}", end="")
            elif val:
                print(f"{str(val)[:12]:<14}", end="")
            else:
                print(f"{'—':<14}", end="")
        print()
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART C: ANALYTIC PLANS - GET CORRECT FIELDS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART C: ANALYTIC PLANS — CORRECT FIELDS FOR ODOO 19")
print("═" * 80)

plan_fields = fields_get('account.analytic.plan')
print(f"\n  Fields on account.analytic.plan:")
for fname, finfo in sorted(plan_fields.items()):
    print(f"    • {fname:<30} {finfo.get('type','?'):<12} {finfo.get('string','?')}")

# Now query with correct fields
plan_field_names = [k for k in plan_fields.keys() if k not in ['__last_update']]
# Use safe subset
safe_plan_fields = ['name', 'parent_id', 'color']
for f in ['default_applicability', 'description', 'sequence', 'complete_name']:
    if f in plan_fields:
        safe_plan_fields.append(f)

try:
    plans = sr('account.analytic.plan', [], safe_plan_fields)
    print(f"\n  Analytic Plans:")
    for p in plans:
        parent = p['parent_id'][1] if p.get('parent_id') and p['parent_id'] else 'Root'
        print(f"    [{p['id']}] {p['name']} (Parent: {parent})")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART D: ANALYTIC ACCOUNTS - FIELDS & DATA
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART D: ANALYTIC ACCOUNTS — DETAILED")
print("═" * 80)

aa_fields = fields_get('account.analytic.account')
print(f"\n  Fields on account.analytic.account:")
for fname, finfo in sorted(aa_fields.items()):
    print(f"    • {fname:<30} {finfo.get('type','?'):<12} {finfo.get('string','?')}")

safe_aa_fields = ['name', 'plan_id', 'code', 'active']
for f in ['company_id', 'partner_id', 'balance', 'debit', 'credit']:
    if f in aa_fields:
        safe_aa_fields.append(f)

try:
    accounts = sr('account.analytic.account', [], safe_aa_fields)
    print(f"\n  Analytic Accounts ({len(accounts)}):")
    for a in accounts:
        plan = a['plan_id'][1] if a.get('plan_id') and a['plan_id'] else 'N/A'
        co = a['company_id'][1] if a.get('company_id') and a['company_id'] else 'ALL' 
        bal = a.get('balance', 'N/A')
        print(f"    [{a['id']}] {a['name']} — Plan: {plan} | Company: {co} | Balance: {bal}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART E: CREATE BRANCH-SPECIFIC WAREHOUSES AND TEST DATA
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART E: CHECKING/CREATING TEST DATA WITH ANALYTIC DISTRIBUTION")
print("═" * 80)

# Get company IDs
companies = sr('res.company', [], ['name'])
company_map = {c['name']: c['id'] for c in companies}
print(f"  Companies: {company_map}")

# Get analytic account IDs  
analytic_accounts = sr('account.analytic.account', [], ['name', 'plan_id'])
analytic_map = {a['name']: a['id'] for a in analytic_accounts}
print(f"  Analytic Accounts: {analytic_map}")

# Get plan IDs
analytic_plans = sr('account.analytic.plan', [], ['name'])
plan_map = {p['name']: p['id'] for p in analytic_plans}
print(f"  Analytic Plans: {plan_map}")

# Check if we need to create warehouse-specific analytic accounts
print("\n  Checking if warehouse analytic accounts exist...")
whs = sr('stock.warehouse', [], ['name', 'code', 'company_id'])
wh_analytics_needed = []
for wh in whs:
    wh_name = wh['name']
    if wh_name not in analytic_map:
        wh_analytics_needed.append(wh)

if wh_analytics_needed:
    print(f"  Need to create analytic accounts for {len(wh_analytics_needed)} warehouses")
    
    # First check if a Warehouses plan exists
    if 'Warehouses' not in plan_map:
        print("  Creating 'Warehouses' analytic plan...")
        try:
            wh_plan_id = create('account.analytic.plan', {'name': 'Warehouses'})
            plan_map['Warehouses'] = wh_plan_id
            print(f"  ✅ Created Warehouses plan (ID: {wh_plan_id})")
        except Exception as e:
            print(f"  ⚠️ Could not create plan: {e}")
            wh_plan_id = plan_map.get('Branches', list(plan_map.values())[0])
    else:
        wh_plan_id = plan_map['Warehouses']
    
    for wh in wh_analytics_needed:
        try:
            vals = {'name': wh['name'], 'plan_id': wh_plan_id}
            aa_id = create('account.analytic.account', vals)
            analytic_map[wh['name']] = aa_id
            print(f"  ✅ Created analytic account for warehouse: {wh['name']} (ID: {aa_id})")
        except Exception as e:
            print(f"  ⚠️ Error creating for {wh['name']}: {e}")
else:
    print("  All warehouses already have analytic accounts")

# Refresh analytic accounts
analytic_accounts = sr('account.analytic.account', [], ['name', 'plan_id'])
analytic_map = {a['name']: a['id'] for a in analytic_accounts}
print(f"\n  Updated Analytic Map: {analytic_map}")

# ═══════════════════════════════════════════════════════════════════
# PART F: CREATE TEST INVOICES WITH ANALYTIC DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART F: CREATING TEST INVOICES WITH ANALYTIC DISTRIBUTION")
print("═" * 80)

# Get necessary data
krishnadas_id = company_map.get('Krishnadas Group', 1)

# Get customers
customers = sr('res.partner', [['customer_rank', '>', 0]], ['name', 'id'], limit=5)
print(f"  Customers: {[(c['name'], c['id']) for c in customers]}")

# Get a product
products = sr('product.product', [], ['name', 'id'], limit=5)
print(f"  Products: {[(p['name'], p['id']) for p in products]}")

# Get sale journal
journals = sr('account.journal', [['type', '=', 'sale'], ['company_id', '=', krishnadas_id]], 
    ['name', 'id'])
print(f"  Sale Journals: {[(j['name'], j['id']) for j in journals]}")

# Get purchase journal
purch_journals = sr('account.journal', [['type', '=', 'purchase'], ['company_id', '=', krishnadas_id]], 
    ['name', 'id'])
print(f"  Purchase Journals: {[(j['name'], j['id']) for j in purch_journals]}")

# Get income account
income_accts = sr('account.account', [['account_type', '=', 'income'], ['company_id', '=', krishnadas_id]], 
    ['name', 'code'], limit=3)
print(f"  Income Accounts: {[(a['code'], a['name']) for a in income_accts]}")

# Get expense account
expense_accts = sr('account.account', [['account_type', '=', 'expense'], ['company_id', '=', krishnadas_id]], 
    ['name', 'code'], limit=3)
print(f"  Expense Accounts: {[(a['code'], a['name']) for a in expense_accts]}")

# Get vendors
vendors = sr('res.partner', [['supplier_rank', '>', 0]], ['name', 'id'], limit=5)
print(f"  Vendors: {[(v['name'], v['id']) for v in vendors]}")

# Now create invoices — one per branch analytic
branch_analytics = {
    'Krishnadas group': analytic_map.get('Krishnadas group'),
    'Devika Furniture': analytic_map.get('Devika Furniture'),
    'KDesign Interior': analytic_map.get('KDesign Interior'),
}

print(f"\n  Branch Analytics: {branch_analytics}")

if customers and products and journals:
    for branch_name, analytic_id in branch_analytics.items():
        if not analytic_id:
            print(f"  ⚠️ No analytic account for {branch_name}, skipping")
            continue
        
        # Build analytic distribution JSON
        analytic_dist = json.dumps({str(analytic_id): 100})
        
        try:
            # Create customer invoice
            customer = customers[0]
            product = products[0]
            journal = journals[0]
            
            inv_vals = {
                'move_type': 'out_invoice',
                'partner_id': customer['id'],
                'journal_id': journal['id'],
                'company_id': krishnadas_id,
                'invoice_date': '2026-02-24',
                'invoice_line_ids': [(0, 0, {
                    'name': f'Test Sale - {branch_name}',
                    'quantity': 5,
                    'price_unit': 1000 + (list(branch_analytics.keys()).index(branch_name) * 500),
                    'analytic_distribution': {str(analytic_id): 100},
                })]
            }
            
            inv_id = create('account.move', inv_vals)
            print(f"  ✅ Created Invoice for {branch_name}: ID {inv_id}")
            
            # Confirm/Post the invoice
            try:
                execute('account.move', 'action_post', [[inv_id]])
                print(f"     ✅ Posted!")
            except Exception as e:
                print(f"     ⚠️ Could not post: {e}")
            
        except Exception as e:
            print(f"  ❌ Error creating invoice for {branch_name}: {e}")
        
        # Create vendor bill
        if vendors and purch_journals:
            try:
                vendor = vendors[0]
                pj = purch_journals[0]
                
                bill_vals = {
                    'move_type': 'in_invoice',
                    'partner_id': vendor['id'],
                    'journal_id': pj['id'],
                    'company_id': krishnadas_id,
                    'invoice_date': '2026-02-24',
                    'invoice_line_ids': [(0, 0, {
                        'name': f'Test Purchase - {branch_name}',
                        'quantity': 3,
                        'price_unit': 800 + (list(branch_analytics.keys()).index(branch_name) * 300),
                        'analytic_distribution': {str(analytic_id): 100},
                    })]
                }
                
                bill_id = create('account.move', bill_vals)
                print(f"  ✅ Created Bill for {branch_name}: ID {bill_id}")
                
                try:
                    execute('account.move', 'action_post', [[bill_id]])
                    print(f"     ✅ Posted!")
                except Exception as e:
                    print(f"     ⚠️ Could not post: {e}")
                    
            except Exception as e:
                print(f"  ❌ Error creating bill for {branch_name}: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART G: VERIFY ANALYTIC LINES CREATED
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART G: VERIFY — ANALYTIC LINES NOW?")
print("═" * 80)

try:
    al_count = count('account.analytic.line', [])
    print(f"  Total analytic lines: {al_count}")
    
    if al_count > 0:
        al_fields = fields_get('account.analytic.line')
        safe_al_fields = ['name', 'amount', 'date', 'account_id']
        for f in ['general_account_id', 'company_id', 'move_line_id', 'plan_id', 'category']:
            if f in al_fields:
                safe_al_fields.append(f)
        
        lines = sr('account.analytic.line', [], safe_al_fields, limit=20, order='id desc')
        for al in lines:
            acc = al['account_id'][1] if al.get('account_id') and al['account_id'] else 'N/A'
            gen = al.get('general_account_id', ['','N/A'])
            gen_name = gen[1] if isinstance(gen, list) and len(gen) > 1 else str(gen)
            co = al.get('company_id', ['','N/A'])
            co_name = co[1] if isinstance(co, list) and len(co) > 1 else str(co)
            print(f"    {al.get('date','?')} | {al.get('name','?'):<40} | Analytic: {acc:<20} | GL: {gen_name} | Amt: {al.get('amount',0):>10.2f} | Co: {co_name}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART H: RE-ANALYZE — WHICH ACCOUNTS NOW HAVE ANALYTIC?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART H: RE-ANALYZE — WHICH ACCOUNT TYPES HAVE ANALYTIC?")
print("═" * 80)

try:
    accounts = sr('account.account', [], ['name', 'code', 'account_type'])
    acct_type_map = {a['id']: a for a in accounts}
    
    move_lines = sr('account.move.line', [['parent_state','=','posted']], 
        ['account_id', 'analytic_distribution', 'debit', 'credit', 'company_id'],
        limit=1000, order='id desc')
    
    type_with = defaultdict(int)
    type_without = defaultdict(int)
    type_total = defaultdict(int)
    
    for ml in move_lines:
        acct_id = ml['account_id'][0] if ml['account_id'] else None
        if acct_id and acct_id in acct_type_map:
            atype = acct_type_map[acct_id]['account_type']
            aname = acct_type_map[acct_id]['name']
            has = bool(ml.get('analytic_distribution'))
            type_total[atype] += 1
            if has:
                type_with[atype] += 1
            else:
                type_without[atype] += 1
    
    print(f"\n  {'Account Type':<35} {'Total':<8} {'WITH Analytic':<15} {'WITHOUT':<10} {'%'}")
    print(f"  {'-'*35} {'-'*8} {'-'*15} {'-'*10} {'-'*5}")
    for atype in sorted(type_total.keys()):
        t = type_total[atype]
        w = type_with.get(atype, 0)
        wo = type_without.get(atype, 0)
        pct = f"{(w/t*100):.0f}%" if t > 0 else "N/A"
        print(f"  {atype:<35} {t:<8} {w:<15} {wo:<10} {pct}")
    
    print(f"\n  ═══ CRITICAL FINDING ═══")
    # Check specific accounts
    print(f"\n  Breakdown by specific account:")
    acct_with = defaultdict(int)
    acct_without = defaultdict(int)
    for ml in move_lines:
        acct_id = ml['account_id'][0] if ml['account_id'] else None
        if acct_id and acct_id in acct_type_map:
            key = f"{acct_type_map[acct_id]['code']} {acct_type_map[acct_id]['name']}"
            if ml.get('analytic_distribution'):
                acct_with[key] += 1
            else:
                acct_without[key] += 1
    
    all_accts = set(list(acct_with.keys()) + list(acct_without.keys()))
    for acct in sorted(all_accts):
        w = acct_with.get(acct, 0)
        wo = acct_without.get(acct, 0)
        indicator = "✅" if w > 0 else "❌"
        print(f"  {indicator} {acct:<50} WITH: {w}, WITHOUT: {wo}")

except Exception as e:
    print(f"  ❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# PART I: TEST REPORTING — READ REPORT DATA VIA API
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART I: AVAILABLE REPORTS — WITH ALL CORRECT FILTER INFO")
print("═" * 80)

try:
    # Get reports with only the fields we confirmed exist
    reports = sr('account.report', [], 
        ['name', 'filter_analytic_groupby', 'filter_journals', 'filter_partner',
         'filter_multi_company', 'filter_date_range', 'filter_hierarchy',
         'filter_account_type', 'filter_budgets', 'filter_aml_ir_filters',
         'filter_unfold_all', 'filter_unreconciled', 'filter_show_draft',
         'filter_period_comparison', 'filter_growth_comparison', 'filter_hide_0_lines',
         'root_report_id', 'country_id'])
    
    print(f"\n  === MASTER TABLE: ALL {len(reports)} REPORTS ===\n")
    
    # Categorize
    analytic_yes = []
    analytic_no = []
    
    for r in sorted(reports, key=lambda x: x['name']):
        has_anal = r.get('filter_analytic_groupby', False)
        has_jour = r.get('filter_journals', False)
        has_part = r.get('filter_partner', False)
        has_mc = r.get('filter_multi_company', '')
        has_budget = r.get('filter_budgets', False)
        country = r['country_id'][1] if r.get('country_id') and r['country_id'] else 'Generic'
        root = r['root_report_id'][1] if r.get('root_report_id') and r['root_report_id'] else ''
        
        anal_str = '✅ ANALYTIC' if has_anal else '❌'
        
        print(f"  [{r['id']:>3}] {r['name']:<45} {anal_str:<14} Journals:{('✅' if has_jour else '❌'):<4} Partner:{('✅' if has_part else '❌'):<4} MultiCo:{str(has_mc):<14} Budget:{'✅' if has_budget else '❌'} Country:{country}")
        
        if has_anal:
            analytic_yes.append(r['name'])
        else:
            analytic_no.append(r['name'])
    
    print(f"\n\n  ════════════════════════════════════════════")
    print(f"  REPORTS THAT SUPPORT ANALYTIC GROUP BY ({len(analytic_yes)}):")
    print(f"  ════════════════════════════════════════════")
    for n in sorted(analytic_yes):
        print(f"    ✅ {n}")
    
    print(f"\n  ════════════════════════════════════════════")
    print(f"  REPORTS THAT DO NOT SUPPORT ANALYTIC ({len(analytic_no)}):")
    print(f"  ════════════════════════════════════════════")
    for n in sorted(analytic_no):
        print(f"    ❌ {n}")

except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════════
# PART J: CHECK ALL WAYS TO FILTER/VIEW BRANCH WISE
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART J: ALL METHODS TO VIEW DATA BRANCH-WISE")
print("═" * 80)

print("""
  METHOD 1: COMPANY SWITCHING (Multi-Company)
  ──────────────────────────────────────────
  → Switch active company in top-right selector
  → ALL reports instantly show data for that company only
  → Works for: EVERY SINGLE REPORT
  → Limitation: Only works if branch = separate company
""")

print(f"  Your database company structure:")
companies = sr('res.company', [], ['name', 'parent_id'])
for c in sorted(companies, key=lambda x: x['id']):
    parent = c['parent_id'][1] if c['parent_id'] else 'ROOT'
    indent = "    " if c['parent_id'] else "  "
    print(f"  {indent}{'└─' if c['parent_id'] else '●'} [{c['id']}] {c['name']} (Parent: {parent})")

print("""
  METHOD 2: ANALYTIC GROUP BY (filter_analytic_groupby)
  ──────────────────────────────────────────────
  → Available ONLY on reports with filter_analytic_groupby = True
  → Shows data grouped/filtered by analytic account (=branch)
  → Only affects P&L lines (income/expense) that carry analytic tags
""")

print("""
  METHOD 3: JOURNAL FILTER
  ──────────────────────────────────────────────
  → Filter reports by specific journals
  → If you create branch-specific journals, this helps
  → Example: "Sales - Devika", "Sales - KDesign", etc.
  → Works on reports with filter_journals = True
""")

# Check current journals
print(f"  Current Journals:")
all_journals = sr('account.journal', [], ['name', 'type', 'company_id', 'code'])
for j in sorted(all_journals, key=lambda x: (x['company_id'][1] if x['company_id'] else '', x['name'])):
    co = j['company_id'][1] if j['company_id'] else 'N/A'
    print(f"    {j['code']:<8} {j['name']:<40} Type: {j['type']:<12} Company: {co}")

print("""
  METHOD 4: PARTNER-BASED FILTERING
  ──────────────────────────────────────────────
  → Filter by customer/vendor on reports with filter_partner = True
  → Useful for Aged Receivable, Aged Payable, Partner Ledger
  → Not directly branch-wise, but helps narrow data
""")

print("""
  METHOD 5: CUSTOM EXCEL EXPORT + PIVOT
  ──────────────────────────────────────────────
  → Export journal items with analytic distribution column
  → Build pivot tables in Excel by branch
  → Works for any data, no limitations
  → Manual process
""")

# ═══════════════════════════════════════════════════════════════════
# PART K: WAREHOUSE-SPECIFIC REPORTING
# ═══════════════════════════════════════════════════════════════════
print("\n" + "═" * 80)
print("  PART K: WAREHOUSE-PER-BRANCH REPORTING")
print("═" * 80)

# Check stock report models
print("\n  Checking stock/inventory report models...")
stock_models = ['stock.report', 'stock.quantity.history', 'report.stock.quantity']
for sm in stock_models:
    try:
        f = fields_get(sm)
        print(f"\n  {sm} — {len(f)} fields:")
        for fname, finfo in sorted(f.items()):
            if any(w in fname.lower() for w in ['warehouse', 'company', 'location', 'analytic', 'branch']):
                print(f"    • {fname}: {finfo.get('string','?')} ({finfo.get('type','?')})")
    except Exception as e:
        print(f"  {sm} — Not accessible: {str(e)[:80]}")

# Check if stock picking has analytic
print("\n  Checking stock.picking for analytic fields...")
try:
    sp_fields = fields_get('stock.picking')
    analytic_sp = {k:v for k,v in sp_fields.items() if 'analytic' in k.lower()}
    print(f"  Analytic fields on stock.picking: {list(analytic_sp.keys()) if analytic_sp else 'NONE'}")
    for k, v in analytic_sp.items():
        print(f"    • {k}: {v.get('string','?')} ({v.get('type','?')})")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Check stock.move for analytic
print("\n  Checking stock.move for analytic fields...")
try:
    sm_fields = fields_get('stock.move')
    analytic_sm = {k:v for k,v in sm_fields.items() if 'analytic' in k.lower()}
    print(f"  Analytic fields on stock.move: {list(analytic_sm.keys()) if analytic_sm else 'NONE'}")
    for k, v in analytic_sm.items():
        print(f"    • {k}: {v.get('string','?')} ({v.get('type','?')})")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Check sale.order and purchase.order for analytic
for model_name in ['sale.order.line', 'purchase.order.line']:
    print(f"\n  Checking {model_name} for analytic fields...")
    try:
        f = fields_get(model_name)
        analytic_f = {k:v for k,v in f.items() if 'analytic' in k.lower()}
        print(f"  Analytic fields: {list(analytic_f.keys()) if analytic_f else 'NONE'}")
        for k, v in analytic_f.items():
            print(f"    • {k}: {v.get('string','?')} ({v.get('type','?')})")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "═" * 80)
print("  INVESTIGATION #2 COMPLETE!")
print("═" * 80)
