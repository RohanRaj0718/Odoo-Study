"""
Deep research for 3 recruitment blogs.
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
print("DEEP RESEARCH — BLOG 2: Job Positions & Website Publishing")
print("="*70)

# Full job position data for Odoo ERP Functional Consultant
print("\n--- Full Job Position: Odoo ERP Functional Consultant ---")
job = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read',
    [[['name', '=', 'Odoo ERP Functional Consultant']]],
    {'fields': ['name', 'department_id', 'is_published', 'website_url',
                'no_of_recruitment', 'expected_employees', 'no_of_hired_employee',
                'contract_type_id', 'address_id', 'user_id',
                'description', 'job_details', 'website_description',
                'alias_email', 'alias_full_name', 'alias_id',
                'industry_id', 'interviewer_ids', 'salary_min',
                'salary_max', 'payment_interval', 'expected_degree',
                'application_count', 'new_application_count',
                'company_id']})
if job:
    j = job[0]
    for k, v in sorted(j.items()):
        val_str = str(v)
        if len(val_str) > 200:
            val_str = val_str[:200] + '...'
        print(f"    {k}: {val_str}")

# Check which job positions have website_description set
print("\n--- Job Website Descriptions ---")
jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
    {'fields': ['name', 'website_description']})
for j in jobs:
    wd = str(j.get('website_description') or '')
    has = 'YES' if wd and wd != 'False' and len(wd) > 10 else 'NO'
    print(f"  {j['name']}: has_website_desc={has} (len={len(wd)})")

# Contract types
print("\n--- Contract Types ---")
ct = models.execute_kw(DB, uid, PASSWORD, 'hr.contract.type', 'search_read', [[]],
    {'fields': ['name', 'sequence']})
for c in ct:
    print(f"  {c['name']} (ID: {c['id']}, seq: {c['sequence']})")

# hr.job fields list (application info tab fields)
print("\n--- hr.job Application Info fields ---")
fields = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'fields_get', [],
    {'attributes': ['string', 'type']})
app_fields = ['days_to_answer', 'days_to_answer_label',
              'process_step_label_1', 'process_count_1',
              'process_step_label_2', 'process_count_2',
              'days_to_offer_label', 'days_to_offer',
              'date_process_from', 'date_process_to']
for f in app_fields:
    if f in fields:
        print(f"  {f} ({fields[f]['type']}): {fields[f]['string']}")
    else:
        print(f"  {f}: NOT FOUND")

print("\n="*70)
print("DEEP RESEARCH — BLOG 3: Stages & Email Templates")
print("="*70)

# Full stage data with templates
print("\n--- All Stages with Full Data ---")
stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', [[]],
    {'fields': ['name', 'sequence', 'fold', 'hired_stage', 'template_id',
                'job_ids', 'requirements', 'rotting_threshold_days'],
     'order': 'sequence'})
for s in stages:
    print(f"\n  Stage: {s['name']} (ID: {s['id']})")
    print(f"    Sequence: {s['sequence']}")
    print(f"    Folded: {s['fold']}")
    print(f"    Hired Stage: {s['hired_stage']}")
    print(f"    Email Template: {s['template_id']}")
    print(f"    Job Specific: {s['job_ids']}")
    print(f"    Requirements: {s['requirements']}")
    print(f"    Rotting Days: {s['rotting_threshold_days']}")

# Email templates for recruitment
print("\n--- Recruitment Email Templates ---")
templates = models.execute_kw(DB, uid, PASSWORD, 'mail.template', 'search_read',
    [[['model_id.model', '=', 'hr.applicant']]],
    {'fields': ['name', 'subject', 'email_from', 'email_to',
                'body_html', 'auto_delete', 'model_id']})
for t in templates:
    body = str(t.get('body_html') or '')
    print(f"\n  Template: {t['name']} (ID: {t['id']})")
    print(f"    Subject: {t.get('subject', 'N/A')}")
    print(f"    From: {t.get('email_from', 'N/A')}")
    print(f"    To: {t.get('email_to', 'N/A')}")
    print(f"    Body length: {len(body)} chars")
    # First 150 chars of body (strip HTML)
    import re
    clean = re.sub('<[^<]+?>', '', body)[:150]
    print(f"    Body preview: {clean}")

# Stage model full fields
print("\n--- hr.recruitment.stage All Fields ---")
stage_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'fields_get', [],
    {'attributes': ['string', 'type', 'help']})
for fname, fdata in sorted(stage_fields.items()):
    help_text = fdata.get('help', '')
    if help_text:
        help_text = f" — {help_text[:80]}"
    print(f"  {fname} ({fdata['type']}): {fdata['string']}{help_text}")

print("\n="*70)
print("DEEP RESEARCH — BLOG 4: Refuse & Talent Pools")
print("="*70)

# Talent pools
print("\n--- Existing Talent Pools ---")
pools = models.execute_kw(DB, uid, PASSWORD, 'hr.talent.pool', 'search_read', [[]],
    {'fields': ['name', 'pool_manager', 'no_of_talents', 'description', 'categ_ids']})
if pools:
    for p in pools:
        print(f"  Pool: {p['name']} (ID: {p['id']})")
        print(f"    Manager: {p.get('pool_manager', 'N/A')}")
        print(f"    # Talents: {p['no_of_talents']}")
else:
    print("  No talent pools exist yet")

# hr.candidate model
print("\n--- hr.candidate Model ---")
try:
    cand_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.candidate', 'fields_get', [],
        {'attributes': ['string', 'type']})
    print(f"  hr.candidate has {len(cand_fields)} fields")
    key_fields = ['partner_name', 'email_normalized', 'phone', 'linkedin_profile',
                  'categ_ids', 'application_ids', 'application_count',
                  'talent_pool_ids', 'availability']
    for f in key_fields:
        if f in cand_fields:
            print(f"    {f} ({cand_fields[f]['type']}): {cand_fields[f]['string']}")
except Exception as e:
    print(f"  Error: {e}")

# Get all candidates
print("\n--- All Candidates ---")
try:
    candidates = models.execute_kw(DB, uid, PASSWORD, 'hr.candidate', 'search_read', [[]],
        {'fields': ['partner_name', 'email_normalized', 'application_count',
                    'talent_pool_ids', 'categ_ids']})
    for c in candidates:
        print(f"  {c['partner_name']} | Email: {c['email_normalized']} | Apps: {c['application_count']} | Pools: {c['talent_pool_ids']}")
except Exception as e:
    print(f"  Error: {e}")

# Refuse reason full details
print("\n--- Refuse Reasons with Templates ---")
reasons = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'search_read', [[]],
    {'fields': ['name', 'template_id', 'sequence', 'active'],
     'order': 'sequence'})
for r in reasons:
    print(f"  {r['name']} (ID: {r['id']}) => Template: {r['template_id']}")

# Check archived applicants detail
print("\n--- Archived Applicants Detail ---")
archived = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', False]]],
    {'fields': ['partner_name', 'job_id', 'stage_id', 'refuse_reason_id',
                'refuse_date', 'kanban_state', 'priority', 'email_from',
                'application_status']})
for a in archived:
    print(f"  {a['partner_name']}")
    print(f"    Job: {a['job_id']}")
    print(f"    Stage: {a['stage_id']}")
    print(f"    Refuse Reason: {a['refuse_reason_id']}")
    print(f"    Refuse Date: {a['refuse_date']}")
    print(f"    Status: {a['application_status']}")

# Check active applicants with skills
print("\n--- Active Applicants with Skills ---")
active = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['partner_name', 'job_id', 'stage_id', 'priority',
                'salary_expected', 'salary_proposed',
                'application_status', 'date_closed', 'emp_id',
                'applicant_skill_ids', 'skill_ids']})
for a in active:
    print(f"  {a['partner_name']}")
    print(f"    Job: {a['job_id']}")
    print(f"    Stage: {a['stage_id']}")
    print(f"    Priority: {a['priority']}")
    print(f"    Status: {a['application_status']}")
    print(f"    Salary Expected: {a.get('salary_expected', 'N/A')}")
    print(f"    Salary Proposed: {a.get('salary_proposed', 'N/A')}")
    print(f"    Employee: {a.get('emp_id', 'N/A')}")
    print(f"    Skills: {a.get('applicant_skill_ids', [])}")
    print(f"    Date Closed: {a.get('date_closed', 'N/A')}")

# Check interview-related fields on applicant
print("\n--- Applicant Interview Fields ---")
app_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get', [],
    {'attributes': ['string', 'type']})
interview_fields = {k: v for k, v in app_fields.items()
                    if 'interview' in k.lower() or 'survey' in k.lower()
                    or 'calendar' in k.lower() or 'schedule' in k.lower()
                    or 'talent' in k.lower() or 'refuse' in k.lower()
                    or 'archive' in k.lower()}
for fname, fdata in sorted(interview_fields.items()):
    print(f"  {fname} ({fdata['type']}): {fdata['string']}")

print("\n" + "="*70)
print("RESEARCH COMPLETE")
print("="*70)
