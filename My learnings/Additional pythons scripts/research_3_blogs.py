"""
Research & verify features for 3 recruitment blogs:
Blog 1: Creating Job Positions & Publishing to Website
Blog 2: Customizing Recruitment Stages and Email Templates
Blog 3: Refusing Applicants and Managing Talent Pools
"""
import xmlrpc.client

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

print("="*70)
print("BLOG 1 RESEARCH: Job Positions & Publishing to Website")
print("="*70)

# All job positions with website fields
print("\n--- Job Positions with Website Data ---")
jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
    {'fields': ['name', 'department_id', 'is_published', 'website_url', 'full_url',
                'no_of_recruitment', 'contract_type_id', 'address_id', 'user_id',
                'description', 'job_details', 'website_description', 'alias_email',
                'alias_full_name', 'industry_id', 'interviewer_ids', 'salary_min',
                'salary_max', 'payment_interval', 'expected_degree',
                'application_count', 'new_application_count']})
for j in jobs:
    print(f"\n  {j['name']} (ID: {j['id']})")
    print(f"    Department: {j['department_id']}")
    print(f"    Published: {j['is_published']}")
    print(f"    URL: {j['website_url']}")
    print(f"    Email Alias: {j.get('alias_email') or j.get('alias_full_name', 'N/A')}")
    print(f"    Contract Type: {j.get('contract_type_id', 'N/A')}")
    print(f"    Address: {j.get('address_id', 'N/A')}")
    print(f"    Industry: {j.get('industry_id', 'N/A')}")
    print(f"    Salary: {j.get('salary_min', 0)} - {j.get('salary_max', 0)} ({j.get('payment_interval', 'N/A')})")
    print(f"    Target: {j['no_of_recruitment']}")
    print(f"    Recruiter: {j.get('user_id', 'N/A')}")
    print(f"    Interviewers: {j.get('interviewer_ids', [])}")
    print(f"    Expected Degree: {j.get('expected_degree', 'N/A')}")
    print(f"    Apps: {j['application_count']} | New: {j['new_application_count']}")
    desc = str(j.get('description', '') or '')
    print(f"    Description: {desc[:120]}...")
    wd = str(j.get('website_description', '') or '')
    print(f"    Website Desc: {wd[:120]}...")
    jd = str(j.get('job_details', '') or '')
    print(f"    Job Details: {jd[:120]}...")

# Check available industries
print("\n--- Industries Available ---")
industries = models.execute_kw(DB, uid, PASSWORD, 'res.partner.industry', 'search_read', [[]],
    {'fields': ['name'], 'limit': 15})
for i in industries:
    print(f"  {i['name']}")
print(f"  ... (total available, showing first 15)")

# Check addresses
print("\n--- Company Addresses ---")
partners = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search_read',
    [[['is_company', '=', True], ['name', 'ilike', 'SmartTech']]],
    {'fields': ['name', 'street', 'city', 'state_id', 'country_id']})
for p in partners:
    print(f"  {p['name']}: {p.get('street', '')} {p.get('city', '')} {p.get('state_id', '')} {p.get('country_id', '')}")

print("\n" + "="*70)
print("BLOG 2 RESEARCH: Customizing Stages & Email Templates")
print("="*70)

# All stages with full details
print("\n--- All Stage Fields ---")
stage_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'fields_get', [],
    {'attributes': ['string', 'type']})
for fname, finfo in sorted(stage_fields.items()):
    print(f"  {fname} ({finfo['type']}): {finfo['string']}")

print("\n--- All Stages with Full Data ---")
stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', [[]],
    {'order': 'sequence'})
for s in stages:
    print(f"\n  {s['name']} (ID: {s['id']}, Seq: {s['sequence']})")
    for k, v in sorted(s.items()):
        if v and k not in ('__last_update', 'name', 'id'):
            print(f"    {k}: {v}")

# Email templates for recruitment
print("\n--- Recruitment Email Templates ---")
templates = models.execute_kw(DB, uid, PASSWORD, 'mail.template', 'search_read',
    [[['model', '=', 'hr.applicant']]],
    {'fields': ['name', 'subject', 'model']})
for t in templates:
    print(f"  {t['name']} | Subject: {t.get('subject', 'N/A')}")

print("\n" + "="*70)
print("BLOG 3 RESEARCH: Refusing Applicants & Talent Pools")
print("="*70)

# Refuse reasons
print("\n--- Refuse Reasons ---")
reasons = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'search_read', [[]],
    {})
for r in reasons:
    print(f"\n  {r['name']} (ID: {r['id']})")
    for k, v in sorted(r.items()):
        if v and k not in ('__last_update', 'name', 'id'):
            print(f"    {k}: {v}")

# Refuse reason fields
print("\n--- Refuse Reason Model Fields ---")
try:
    rr_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'fields_get', [],
        {'attributes': ['string', 'type']})
    for fname, finfo in sorted(rr_fields.items()):
        print(f"  {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  Error: {e}")

# Check talent pool model
print("\n--- Talent Pool Model ---")
try:
    tp_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.talent.pool', 'fields_get', [],
        {'attributes': ['string', 'type']})
    print(f"  hr.talent.pool exists with {len(tp_fields)} fields:")
    for fname, finfo in sorted(tp_fields.items()):
        print(f"    {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  hr.talent.pool: {e}")

# Check if there's a refuse wizard
print("\n--- Refuse Wizard ---")
try:
    rw_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse', 'fields_get', [],
        {'attributes': ['string', 'type']})
    print(f"  hr.applicant.refuse wizard exists with {len(rw_fields)} fields:")
    for fname, finfo in sorted(rw_fields.items()):
        print(f"    {fname} ({finfo['type']}): {finfo['string']}")
except Exception as e:
    print(f"  hr.applicant.refuse wizard: {e}")

# Check archived/refused applicants
print("\n--- Archived/Refused Applicants ---")
archived = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', False]]],
    {'fields': ['partner_name', 'refuse_reason_id', 'refuse_date', 'job_id', 'stage_id', 'kanban_state']})
for a in archived:
    reason = a['refuse_reason_id'][1] if a['refuse_reason_id'] else 'No reason'
    job = a['job_id'][1] if a['job_id'] else 'N/A'
    stage = a['stage_id'][1] if a['stage_id'] else 'N/A'
    print(f"  {a['partner_name']} | Job: {job} | Stage: {stage} | Reason: {reason} | Date: {a.get('refuse_date', 'N/A')}")

# Check all active applicants current state
print("\n--- Active Applicants ---")
active = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['partner_name', 'job_id', 'stage_id', 'priority', 'kanban_state', 
                'email_from', 'salary_expected', 'salary_proposed', 'source_id', 'medium_id']})
for a in active:
    job = a['job_id'][1] if a['job_id'] else 'N/A'
    stage = a['stage_id'][1] if a['stage_id'] else 'N/A'
    source = a['source_id'][1] if a['source_id'] else 'N/A'
    print(f"  {a['partner_name']} | Job: {job} | Stage: {stage} | Priority: {a['priority']} | Kanban: {a['kanban_state']} | Source: {source}")

# Check application_status field options
print("\n--- Application Status Options ---")
try:
    app_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get', 
        ['application_status'], {'attributes': ['string', 'type', 'selection']})
    if 'application_status' in app_fields:
        print(f"  Type: {app_fields['application_status']['type']}")
        print(f"  Selection: {app_fields['application_status'].get('selection', 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("RESEARCH COMPLETE")
print("="*70)
