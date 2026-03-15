"""
Install Website HR Recruitment + Full deep exploration of Recruitment module
"""
import xmlrpc.client
import time

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f'Authenticated: uid={uid}')

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Install website_hr_recruitment
print("\n=== Installing website_hr_recruitment module ===")
mod_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search',
    [[['name', '=', 'website_hr_recruitment']]])
if mod_ids:
    print(f"  Module ID: {mod_ids[0]}")
    try:
        models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', [mod_ids])
        print("  website_hr_recruitment installed successfully!")
    except Exception as e:
        print(f"  Install note: {e}")

# Re-authenticate
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

# =============================================
# DEEP EXPLORATION OF RECRUITMENT MODULE
# =============================================

print("\n" + "="*70)
print("RECRUITMENT MODULE — COMPLETE EXPLORATION")
print("="*70)

# 1. All installed recruitment-related modules
print("\n--- 1. INSTALLED MODULES ---")
mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'ilike', 'recruit'], ['state', '=', 'installed']]],
    {'fields': ['name', 'shortdesc']})
for m in mods:
    print(f"  {m['name']}: {m['shortdesc']}")

# 2. Recruitment Stages
print("\n--- 2. RECRUITMENT STAGES ---")
try:
    stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', 
        [[]], {'order': 'sequence'})
    for s in stages:
        print(f"\n  Stage: {s.get('name')} (ID: {s['id']}, Seq: {s.get('sequence')})")
        print(f"    Folded: {s.get('fold', False)}")
        print(f"    Hired Stage: {s.get('hired_stage', False)}")
        print(f"    Template: {s.get('template_id', False)}")
        print(f"    Requirements: {s.get('requirements', False)}")
        print(f"    Legend Blocked: {s.get('legend_blocked', False)}")
        print(f"    Legend Done: {s.get('legend_done', False)}")
        print(f"    Legend Normal: {s.get('legend_normal', False)}")
except Exception as e:
    print(f"  Error: {e}")

# 3. hr.recruitment.stage fields
print("\n--- 3. STAGE MODEL FIELDS ---")
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'fields_get', [],
        {'attributes': ['string', 'type']})
    for fname, finfo in sorted(fields.items()):
        print(f"  {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  Error: {e}")

# 4. hr.applicant fields
print("\n--- 4. APPLICANT MODEL FIELDS ---")
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get', [],
        {'attributes': ['string', 'type', 'required']})
    for fname, finfo in sorted(fields.items()):
        req = " [REQ]" if finfo.get('required') else ""
        print(f"  {fname} ({finfo['type']}): {finfo['string']}{req}")
except Exception as e:
    print(f"  Error: {e}")

# 5. hr.candidate fields (Odoo 19 has a candidate model)
print("\n--- 5. HR.CANDIDATE MODEL FIELDS ---")
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.candidate', 'fields_get', [],
        {'attributes': ['string', 'type']})
    for fname, finfo in sorted(fields.items()):
        print(f"  {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  Error: {e}")

# 6. Job positions after recruitment install - check new fields
print("\n--- 6. HR.JOB FIELDS (after recruitment module) ---")
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'fields_get', [],
        {'attributes': ['string', 'type']})
    for fname, finfo in sorted(fields.items()):
        print(f"  {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  Error: {e}")

# 7. Job positions - full data with new fields
print("\n--- 7. JOB POSITIONS (full read) ---")
try:
    jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
        {'limit': 3})
    for j in jobs:
        print(f"\n  === {j.get('name')} (ID: {j['id']}) ===")
        for k, v in sorted(j.items()):
            if v and k != '__last_update':
                print(f"    {k}: {v}")
except Exception as e:
    print(f"  Error: {e}")

# 8. Check existing applicants
print("\n--- 8. EXISTING APPLICANTS ---")
try:
    apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read', [[]],
        {'limit': 10})
    if not apps:
        print("  No applicants found (fresh install)")
    else:
        for a in apps:
            name = a.get('partner_name', a.get('candidate_id', 'N/A'))
            stage = a.get('stage_id', [False, 'N/A'])
            job = a.get('job_id', [False, 'N/A'])
            print(f"  {name} | Stage: {stage} | Job: {job}")
except Exception as e:
    print(f"  Error: {e}")

# 9. Check hr.recruitment.source model
print("\n--- 9. RECRUITMENT SOURCES ---")
try:
    sources = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.source', 'search_read', [[]],
        {})
    if not sources:
        print("  No custom sources found")
    for s in sources:
        print(f"  {s.get('name', 'N/A')} (ID: {s['id']})")
except Exception as e:
    print(f"  Model may not exist: {e}")

# 10. UTM sources
print("\n--- 10. UTM SOURCES ---")
try:
    sources = models.execute_kw(DB, uid, PASSWORD, 'utm.source', 'search_read', [[]],
        {'fields': ['name'], 'limit': 20})
    for s in sources:
        print(f"  {s['name']}")
except Exception as e:
    print(f"  Error: {e}")

# 11. Check website_published field on job
print("\n--- 11. WEBSITE PUBLISHED STATUS ---")
try:
    jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
        {'fields': ['name', 'website_published', 'is_published', 'website_url', 'website_id']})
    for j in jobs:
        print(f"  {j['name']}: published={j.get('website_published', j.get('is_published', 'N/A'))}")
except Exception as e:
    print(f"  Error: {e}")

# 12. Employment types
print("\n--- 12. EMPLOYMENT TYPES ---")
try:
    types = models.execute_kw(DB, uid, PASSWORD, 'hr.contract.type', 'search_read', [[]],
        {'fields': ['name']})
    for t in types:
        print(f"  {t['name']}")
except Exception as e:
    print(f"  Error: {e}")

# 13. Activity types related to recruitment
print("\n--- 13. ACTIVITY TYPES ---")
try:
    acts = models.execute_kw(DB, uid, PASSWORD, 'mail.activity.type', 'search_read', 
        [[['res_model', 'in', ['hr.applicant', False]]]],
        {'fields': ['name', 'res_model', 'summary']})
    for a in acts:
        print(f"  {a['name']} | Model: {a.get('res_model', 'All')} | Summary: {a.get('summary', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("EXPLORATION COMPLETE")
print("="*70)
