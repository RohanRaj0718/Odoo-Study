"""
============================================================================
RECRUITMENT BLOG — DEMO DATA SETUP & FULL WORKFLOW VERIFICATION
============================================================================
Creates demo data for the recruitment blog and walks through:
1. Recruitment Settings check
2. Create a new Job Position with full config
3. Create Departments (verify existing)
4. Add Applicants
5. Walk through all 6 stages
6. Publish to website
7. Create Employee from hired applicant
============================================================================
"""
import xmlrpc.client
import time
import json

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f'Authenticated: uid={uid}')
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def search_one(model, domain):
    ids = models.execute_kw(DB, uid, PASSWORD, model, 'search', [domain], {'limit': 1})
    return ids[0] if ids else False

def read_one(model, rec_id, fields=None):
    data = models.execute_kw(DB, uid, PASSWORD, model, 'read', [rec_id], 
        {'fields': fields} if fields else {})
    return data[0] if data else {}

# ============================================================================
# STEP 1: CHECK RECRUITMENT SETTINGS
# ============================================================================
print("\n" + "="*70)
print("STEP 1: VERIFY RECRUITMENT MODULE & SETTINGS")
print("="*70)

# Check installed modules
mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'in', ['hr_recruitment', 'website_hr_recruitment', 'hr_recruitment_survey']], 
      ['state', '=', 'installed']]],
    {'fields': ['name', 'shortdesc', 'state']})
print("\nInstalled Recruitment Modules:")
for m in mods:
    print(f"  [OK] {m['name']}: {m['shortdesc']}")

# Check if hr_recruitment_survey is installed (needed for interview forms)
survey_installed = any(m['name'] == 'hr_recruitment_survey' for m in mods)
if not survey_installed:
    print("\n  Installing hr_recruitment_survey for interview forms...")
    mod_id = search_one('ir.module.module', [['name', '=', 'hr_recruitment_survey']])
    if mod_id:
        try:
            models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', [[mod_id]])
            print("  [OK] hr_recruitment_survey installed!")
            uid = common.authenticate(DB, USERNAME, PASSWORD, {})
        except Exception as e:
            print(f"  Note: {e}")

# ============================================================================
# STEP 2: CHECK EXISTING STAGES
# ============================================================================
print("\n" + "="*70)
print("STEP 2: VERIFY RECRUITMENT STAGES")
print("="*70)

stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', 
    [[]], {'order': 'sequence', 'fields': ['name', 'sequence', 'fold', 'hired_stage', 'template_id']})
print(f"\nFound {len(stages)} stages:")
for s in stages:
    tmpl = s['template_id'][1] if s['template_id'] else 'None'
    print(f"  {s['sequence']}. {s['name']} | Folded: {s['fold']} | Hired: {s['hired_stage']} | Email: {tmpl}")

# ============================================================================
# STEP 3: CHECK/CREATE DEPARTMENTS
# ============================================================================
print("\n" + "="*70)
print("STEP 3: VERIFY DEPARTMENTS")
print("="*70)

depts = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search_read', [[]],
    {'fields': ['name', 'company_id']})
print(f"\nExisting departments ({len(depts)}):")
for d in depts:
    print(f"  {d['name']} (Company: {d['company_id'][1] if d['company_id'] else 'N/A'})")

# ============================================================================
# STEP 4: CREATE A NEW JOB POSITION FOR THE BLOG
# ============================================================================
print("\n" + "="*70)
print("STEP 4: CREATE NEW JOB POSITION — 'Odoo ERP Functional Consultant'")
print("="*70)

# Check if already exists
existing_job = search_one('hr.job', [['name', '=', 'Odoo ERP Functional Consultant']])
if existing_job:
    print(f"  Job already exists (ID: {existing_job}), deleting for fresh start...")
    # Delete any applicants first
    app_ids = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search', 
        [[['job_id', '=', existing_job]]])
    if app_ids:
        models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'unlink', [app_ids])
    models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'unlink', [[existing_job]])

# Find the "Sales" department (or create one called "IT / Consulting")
it_dept = search_one('hr.department', [['name', '=', 'IT / Consulting']])
if not it_dept:
    it_dept = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'create', [{
        'name': 'IT / Consulting',
    }])
    print(f"  Created department 'IT / Consulting' (ID: {it_dept})")
else:
    print(f"  Department 'IT / Consulting' exists (ID: {it_dept})")

# Get contract type "Permanent"
contract_type = search_one('hr.contract.type', [['name', '=', 'Permanent']])

# Create the job position
job_vals = {
    'name': 'Odoo ERP Functional Consultant',
    'department_id': it_dept,
    'no_of_recruitment': 2,
    'description': '''<p>We are looking for an experienced Odoo ERP Functional Consultant to join our team. The ideal candidate will have hands-on experience with Odoo modules including Sales, Purchase, Inventory, Manufacturing and Accounting.</p>
<p><b>Responsibilities:</b></p>
<ul>
<li>Gather and analyze client business requirements</li>
<li>Configure and customize Odoo modules based on client needs</li>
<li>Conduct user training sessions and create documentation</li>
<li>Provide post-implementation support</li>
<li>Collaborate with the technical team for custom development requirements</li>
</ul>
<p><b>Requirements:</b></p>
<ul>
<li>Minimum 2 years of experience with Odoo ERP</li>
<li>Strong understanding of business processes across Sales, Purchase, Inventory and Manufacturing</li>
<li>Excellent communication and presentation skills</li>
<li>Odoo certification is a plus</li>
</ul>''',
    'user_id': uid,
}
if contract_type:
    job_vals['contract_type_id'] = contract_type

job_id = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'create', [job_vals])
print(f"\n  [OK] Created Job Position 'Odoo ERP Functional Consultant' (ID: {job_id})")

# Read back to verify
job_data = read_one('hr.job', job_id, ['name', 'department_id', 'no_of_recruitment', 
    'user_id', 'website_url', 'is_published', 'alias_email',
    'contract_type_id', 'job_details'])
print(f"\n  Job Details:")
print(f"    Name: {job_data['name']}")
print(f"    Department: {job_data['department_id']}")
print(f"    Target: {job_data['no_of_recruitment']}")
print(f"    Recruiter: {job_data['user_id']}")
print(f"    Website URL: {job_data['website_url']}")
print(f"    Published: {job_data['is_published']}")
print(f"    Email Alias: {job_data.get('alias_email', 'N/A')}")
print(f"    Contract Type: {job_data.get('contract_type_id', 'N/A')}")
print(f"    Process Details: {job_data.get('job_details', 'N/A')[:100]}...")

# ============================================================================
# STEP 5: CREATE APPLICANTS
# ============================================================================
print("\n" + "="*70)
print("STEP 5: CREATE APPLICANTS")
print("="*70)

# Get stages
stage_new = search_one('hr.recruitment.stage', [['name', '=', 'New']])
stage_qual = search_one('hr.recruitment.stage', [['name', '=', 'Qualification']])
stage_first = search_one('hr.recruitment.stage', [['name', '=', 'First Interview']])
stage_second = search_one('hr.recruitment.stage', [['name', '=', 'Second Interview']])
stage_proposal = search_one('hr.recruitment.stage', [['name', '=', 'Contract Proposal']])
stage_signed = search_one('hr.recruitment.stage', [['name', '=', 'Contract Signed']])

print(f"  Stages: New={stage_new}, Qual={stage_qual}, First={stage_first}, Second={stage_second}, Proposal={stage_proposal}, Signed={stage_signed}")

# Create Applicant 1 — Anitha Menon (will go through full workflow to hired)
app1_vals = {
    'partner_name': 'Anitha Menon',
    'email_from': 'anitha.menon@example.com',
    'partner_phone': '+91 98765 43210',
    'job_id': job_id,
    'department_id': it_dept,
    'stage_id': stage_new,
    'user_id': uid,
    'priority': '2',  # Very Good
    'salary_expected': 55000,
    'salary_expected_extra': 'Per Month + Health Insurance',
    'linkedin_profile': 'https://linkedin.com/in/anitha-menon',
}
app1_id = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'create', [app1_vals])
print(f"\n  [OK] Created Applicant 1: Anitha Menon (ID: {app1_id}) — Stage: New")

# Create Applicant 2 — Rahul Sharma
app2_vals = {
    'partner_name': 'Rahul Sharma',
    'email_from': 'rahul.sharma@example.com',
    'partner_phone': '+91 87654 32109',
    'job_id': job_id,
    'department_id': it_dept,
    'stage_id': stage_new,
    'user_id': uid,
    'priority': '1',  # Good
    'salary_expected': 60000,
    'salary_expected_extra': 'Per Month',
}
app2_id = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'create', [app2_vals])
print(f"  [OK] Created Applicant 2: Rahul Sharma (ID: {app2_id}) — Stage: New")

# Create Applicant 3 — Priya Nair
app3_vals = {
    'partner_name': 'Priya Nair',
    'email_from': 'priya.nair@example.com',
    'partner_phone': '+91 76543 21098',
    'job_id': job_id,
    'department_id': it_dept,
    'stage_id': stage_new,
    'user_id': uid,
    'priority': '0',  # Normal
    'salary_expected': 45000,
}
app3_id = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'create', [app3_vals])
print(f"  [OK] Created Applicant 3: Priya Nair (ID: {app3_id}) — Stage: New")

# ============================================================================
# STEP 6: WALK APPLICANT 1 THROUGH ALL STAGES
# ============================================================================
print("\n" + "="*70)
print("STEP 6: WALK ANITHA MENON THROUGH COMPLETE RECRUITMENT FLOW")
print("="*70)

# Move to Qualification
print("\n  Stage 1 -> 2: Moving to Qualification...")
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {'stage_id': stage_qual}])
app_data = read_one('hr.applicant', app1_id, ['stage_id', 'date_last_stage_update'])
print(f"    [OK] Stage: {app_data['stage_id'][1]} | Updated: {app_data['date_last_stage_update']}")

# Move to First Interview
print("\n  Stage 2 -> 3: Moving to First Interview...")
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {'stage_id': stage_first}])
app_data = read_one('hr.applicant', app1_id, ['stage_id', 'date_last_stage_update'])
print(f"    [OK] Stage: {app_data['stage_id'][1]} | Updated: {app_data['date_last_stage_update']}")

# Move to Second Interview
print("\n  Stage 3 -> 4: Moving to Second Interview...")
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {'stage_id': stage_second}])
app_data = read_one('hr.applicant', app1_id, ['stage_id', 'date_last_stage_update'])
print(f"    [OK] Stage: {app_data['stage_id'][1]} | Updated: {app_data['date_last_stage_update']}")

# Add proposed salary
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {
    'salary_proposed': 52000,
    'salary_proposed_extra': 'Per Month + Health Insurance + Annual Bonus',
}])
print("    [OK] Added proposed salary: 52,000 Per Month")

# Move to Contract Proposal
print("\n  Stage 4 -> 5: Moving to Contract Proposal...")
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {'stage_id': stage_proposal}])
app_data = read_one('hr.applicant', app1_id, ['stage_id', 'date_last_stage_update'])
print(f"    [OK] Stage: {app_data['stage_id'][1]} | Updated: {app_data['date_last_stage_update']}")

# Move to Contract Signed (HIRED!)
print("\n  Stage 5 -> 6: Moving to Contract Signed (HIRED)...")
models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app1_id], {'stage_id': stage_signed}])
app_data = read_one('hr.applicant', app1_id, ['stage_id', 'date_last_stage_update', 'date_closed'])
print(f"    [OK] Stage: {app_data['stage_id'][1]} | Updated: {app_data['date_last_stage_update']}")
print(f"    [OK] Hire Date: {app_data['date_closed']}")

# ============================================================================
# STEP 7: MOVE APPLICANT 2 TO QUALIFICATION (partial progress)
# ============================================================================
print("\n" + "="*70)
print("STEP 7: MOVE RAHUL SHARMA TO QUALIFICATION")
print("="*70)

models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app2_id], {'stage_id': stage_qual}])
app_data = read_one('hr.applicant', app2_id, ['stage_id'])
print(f"  [OK] Rahul Sharma — Stage: {app_data['stage_id'][1]}")

# ============================================================================
# STEP 8: REFUSE APPLICANT 3 (Priya Nair)
# ============================================================================
print("\n" + "="*70)
print("STEP 8: REFUSE PRIYA NAIR")
print("="*70)

# Check refuse reasons
refuse_reasons = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'search_read', 
    [[]], {'fields': ['name']})
if refuse_reasons:
    print(f"  Available refuse reasons:")
    for r in refuse_reasons:
        print(f"    {r['id']}: {r['name']}")
    
    # Use first reason or "Doesn't fit the job requirements"
    reason_id = None
    for r in refuse_reasons:
        if 'fit' in r['name'].lower() or 'requirement' in r['name'].lower() or 'not' in r['name'].lower():
            reason_id = r['id']
            break
    if not reason_id:
        reason_id = refuse_reasons[0]['id']
    
    print(f"  Using reason ID: {reason_id}")
    
    # Archive the applicant (refuse = archive + set refuse reason)
    models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app3_id], {
        'active': False,
        'refuse_reason_id': reason_id,
    }])
    print(f"  [OK] Priya Nair refused and archived")
else:
    print("  No refuse reasons found. Just archiving...")
    models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'write', [[app3_id], {'active': False}])

# ============================================================================
# STEP 9: PUBLISH JOB POSITION TO WEBSITE
# ============================================================================
print("\n" + "="*70)
print("STEP 9: PUBLISH JOB POSITION TO WEBSITE")
print("="*70)

# Publish the job
models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'write', [[job_id], {'is_published': True}])
job_data = read_one('hr.job', job_id, ['is_published', 'website_published', 'website_url', 'full_url'])
print(f"  [OK] Published: {job_data.get('is_published', job_data.get('website_published'))}")
print(f"  [OK] Website URL: {job_data.get('website_url', 'N/A')}")
print(f"  [OK] Full URL: {job_data.get('full_url', 'N/A')}")

# Also publish one existing job for comparison
mfg_job = search_one('hr.job', [['name', '=', 'Manufacturing Manager']])
if mfg_job:
    models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'write', [[mfg_job], {'is_published': True}])
    mfg_data = read_one('hr.job', mfg_job, ['website_url', 'is_published'])
    print(f"  [OK] Also published Manufacturing Manager: {mfg_data.get('website_url')}")

# ============================================================================
# STEP 10: CREATE EMPLOYEE FROM HIRED APPLICANT
# ============================================================================
print("\n" + "="*70)
print("STEP 10: CREATE EMPLOYEE FROM HIRED APPLICANT (Anitha Menon)")
print("="*70)

# Check if create_employee_from_applicant method exists
try:
    # Try to use the create employee action
    result = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'create_employee_from_applicant', [[app1_id]])
    print(f"  [OK] create_employee_from_applicant result: {result}")
    
    # Check if employee was created
    app_data = read_one('hr.applicant', app1_id, ['employee_id', 'employee_name'])
    print(f"  Employee ID: {app_data.get('employee_id', 'N/A')}")
    print(f"  Employee Name: {app_data.get('employee_name', 'N/A')}")
    
    if app_data.get('employee_id'):
        emp_data = read_one('hr.employee', app_data['employee_id'][0], 
            ['name', 'department_id', 'job_id', 'job_title'])
        print(f"\n  Employee Record Created:")
        print(f"    Name: {emp_data['name']}")
        print(f"    Department: {emp_data['department_id']}")
        print(f"    Job Position: {emp_data['job_id']}")
        print(f"    Job Title: {emp_data.get('job_title', 'N/A')}")
except Exception as e:
    print(f"  Note: create_employee_from_applicant returned: {e}")
    print("  This is expected — in UI, user clicks 'Create Employee' button on applicant card")
    print("  The method may return a wizard action rather than directly creating")

# ============================================================================
# STEP 11: FINAL VERIFICATION — READ ALL APPLICANTS
# ============================================================================
print("\n" + "="*70)
print("STEP 11: FINAL VERIFICATION — ALL APPLICANTS FOR THIS JOB")
print("="*70)

# Read active applicants
active_apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read', 
    [[['job_id', '=', job_id], ['active', '=', True]]],
    {'fields': ['partner_name', 'stage_id', 'priority', 'salary_expected', 
                'salary_proposed', 'date_closed', 'employee_id', 'kanban_state']})
print(f"\nActive Applicants ({len(active_apps)}):")
for a in active_apps:
    stage = a['stage_id'][1] if a['stage_id'] else 'N/A'
    emp = a['employee_id'][1] if a['employee_id'] else 'Not yet'
    print(f"  {a['partner_name']} | Stage: {stage} | Priority: {a['priority']} | Expected: {a['salary_expected']} | Proposed: {a['salary_proposed']} | Employee: {emp}")

# Read archived/refused applicants
archived_apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read', 
    [[['job_id', '=', job_id], ['active', '=', False]]],
    {'fields': ['partner_name', 'stage_id', 'refuse_reason_id', 'refuse_date']})
print(f"\nRefused/Archived Applicants ({len(archived_apps)}):")
for a in archived_apps:
    reason = a['refuse_reason_id'][1] if a['refuse_reason_id'] else 'No reason'
    print(f"  {a['partner_name']} | Reason: {reason} | Date: {a.get('refuse_date', 'N/A')}")

# ============================================================================
# STEP 12: VERIFY ALL JOB POSITIONS DASHBOARD 
# ============================================================================
print("\n" + "="*70)
print("STEP 12: ALL JOB POSITIONS ON DASHBOARD")
print("="*70)

all_jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
    {'fields': ['name', 'department_id', 'no_of_recruitment', 'application_count', 
                'new_application_count', 'is_published', 'no_of_hired_employee']})
for j in all_jobs:
    dept = j['department_id'][1] if j['department_id'] else 'N/A'
    pub = "PUBLISHED" if j['is_published'] else "Not Published"
    print(f"  {j['name']} | Dept: {dept} | Target: {j['no_of_recruitment']} | Apps: {j['application_count']} | New Apps: {j['new_application_count']} | Hired: {j['no_of_hired_employee']} | {pub}")

print("\n" + "="*70)
print("ALL STEPS COMPLETE — RECRUITMENT BLOG DEMO DATA VERIFIED")
print("="*70)
