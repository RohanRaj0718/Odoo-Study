"""
Explore Recruitment Module in Demo Database
"""
import xmlrpc.client

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f'Authenticated: uid={uid}')

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# 1. Check if recruitment module is installed
print("\n" + "="*70)
print("1. INSTALLED HR/RECRUITMENT MODULES")
print("="*70)
modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'in', ['hr_recruitment', 'hr_recruitment_sign', 'website_hr_recruitment', 
                       'hr', 'website', 'hr_recruitment_survey']], 
      ['state', '=', 'installed']]],
    {'fields': ['name', 'shortdesc', 'state']})
for m in modules:
    print(f"  {m['name']}: {m['shortdesc']} ({m['state']})")

if not any(m['name'] == 'hr_recruitment' for m in modules):
    print("\n  *** Recruitment module is NOT installed! ***")
    print("  Checking if it's available to install...")
    avail = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
        [[['name', 'like', 'hr_recruit']]],
        {'fields': ['name', 'shortdesc', 'state']})
    for m in avail:
        print(f"  {m['name']}: {m['shortdesc']} ({m['state']})")

# 2. Get all fields of hr.job model
print("\n" + "="*70)
print("2. HR.JOB MODEL FIELDS")
print("="*70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'fields_get', [],
        {'attributes': ['string', 'type', 'required']})
    for fname, finfo in sorted(fields.items()):
        req = " [REQUIRED]" if finfo.get('required') else ""
        print(f"  {fname} ({finfo['type']}): {finfo['string']}{req}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Job positions with ALL fields
print("\n" + "="*70)
print("3. JOB POSITIONS (hr.job) - ALL DATA")
print("="*70)
try:
    jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]], {})
    if not jobs:
        print("  No job positions found.")
    for j in jobs:
        print(f"\n  --- {j.get('name', 'N/A')} (ID: {j['id']}) ---")
        for k, v in sorted(j.items()):
            if v and k != '__last_update':
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Recruitment stages
print("\n" + "="*70)
print("4. RECRUITMENT STAGES (hr.recruitment.stage)")
print("="*70)
try:
    stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', [[]], 
        {'order': 'sequence'})
    if not stages:
        print("  No stages found.")
    for s in stages:
        print(f"\n  Stage: {s.get('name', 'N/A')} (ID: {s['id']}, Seq: {s.get('sequence', 'N/A')})")
        for k, v in sorted(s.items()):
            if v and k not in ('__last_update', 'name', 'id'):
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# 5. Applicants
print("\n" + "="*70)
print("5. APPLICANTS (hr.applicant)")
print("="*70)
try:
    applicants = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read', [[]],
        {'limit': 10})
    if not applicants:
        print("  No applicants found.")
    for a in applicants:
        print(f"\n  Applicant: {a.get('partner_name', a.get('candidate_id', 'N/A'))} (ID: {a['id']})")
        for k, v in sorted(a.items()):
            if v and k != '__last_update':
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# 6. Departments
print("\n" + "="*70)
print("6. DEPARTMENTS (hr.department)")
print("="*70)
try:
    depts = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search_read', [[]],
        {'fields': ['name', 'company_id', 'parent_id', 'manager_id']})
    for d in depts:
        mgr = d['manager_id'][1] if d['manager_id'] else 'N/A'
        parent = d['parent_id'][1] if d['parent_id'] else 'None'
        company = d['company_id'][1] if d['company_id'] else 'N/A'
        print(f"  {d['name']} | Manager: {mgr} | Parent: {parent} | Company: {company}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("EXPLORATION COMPLETE")
print("="*70)
