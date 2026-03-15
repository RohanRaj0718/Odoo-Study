"""
Verify all claims in the 3 recruitment blogs against the live demo database.
Blog 2: Job Positions & Website Publishing
Blog 3: Recruitment Stages & Email Templates
Blog 4: Refuse Applicants & Talent Pools
"""
import xmlrpc.client
import sys

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

passed = 0
failed = 0

def check(description, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {description}")
    else:
        failed += 1
        print(f"  FAIL: {description}")

print("="*70)
print("BLOG 2 VERIFICATION: Job Positions & Website Publishing")
print("="*70)

# Check 7 job positions exist
jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', [[]],
    {'fields': ['name', 'department_id', 'is_published', 'no_of_recruitment',
                'expected_employees', 'no_of_hired_employee', 'contract_type_id',
                'user_id', 'website_url', 'application_count',
                'new_application_count', 'salary_min', 'salary_max',
                'payment_interval', 'address_id', 'interviewer_ids',
                'description', 'website_description', 'job_details',
                'company_id']})
job_names = [j['name'] for j in jobs]
check("7 job positions exist", len(jobs) == 7)
check("HR Manager exists", 'HR Manager' in job_names)
check("Machine Operator exists", 'Machine Operator' in job_names)
check("Manufacturing Manager exists", 'Manufacturing Manager' in job_names)
check("Odoo ERP Functional Consultant exists", 'Odoo ERP Functional Consultant' in job_names)
check("Purchase Manager exists", 'Purchase Manager' in job_names)
check("Quality Inspector exists", 'Quality Inspector' in job_names)
check("Sales Manager exists", 'Sales Manager' in job_names)

# Odoo ERP Functional Consultant details
fc = [j for j in jobs if j['name'] == 'Odoo ERP Functional Consultant'][0]
check("FC department is IT / Consulting", fc['department_id'] and 'IT / Consulting' in str(fc['department_id']))
check("FC is published", fc['is_published'] == True)
check("FC contract type is Permanent", fc['contract_type_id'] and 'Permanent' in str(fc['contract_type_id']))
check("FC recruiter is Rohan Raj", fc['user_id'] and 'Rohan Raj' in str(fc['user_id']))
check("FC has 2 applications", fc['application_count'] == 2)
check("FC website URL contains /jobs/odoo-erp-functional-consultant-8", '/jobs/odoo-erp-functional-consultant-8' in str(fc.get('website_url', '')))
check("FC salary_min is 0", fc['salary_min'] == 0.0)
check("FC salary_max is 0", fc['salary_max'] == 0.0)
check("FC payment_interval is monthly", fc['payment_interval'] == 'monthly')
check("FC address_id is not set", not fc['address_id'])
check("FC interviewers empty", fc['interviewer_ids'] == [])
check("FC expected_employees is 2", fc['expected_employees'] == 2)
check("FC has website description", len(str(fc.get('website_description', '') or '')) > 100)
check("FC has job description", len(str(fc.get('description', '') or '')) > 50)
check("FC has job_details (Application Info)", len(str(fc.get('job_details', '') or '')) > 20)
check("FC company is SmartTech Retail", 'SmartTech Retail' in str(fc.get('company_id', '')))

# Manufacturing Manager published
mm = [j for j in jobs if j['name'] == 'Manufacturing Manager'][0]
check("Manufacturing Manager is published", mm['is_published'] == True)

# Other positions not published
for name in ['HR Manager', 'Machine Operator', 'Purchase Manager', 'Quality Inspector', 'Sales Manager']:
    j = [x for x in jobs if x['name'] == name][0]
    check(f"{name} is not published", j['is_published'] == False)

# Only FC has website description
for j in jobs:
    if j['name'] == 'Odoo ERP Functional Consultant':
        continue
    wd = str(j.get('website_description', '') or '')
    check(f"{j['name']} has no website description", len(wd) < 20)

# 13 contract types
ct = models.execute_kw(DB, uid, PASSWORD, 'hr.contract.type', 'search_read', [[]],
    {'fields': ['name']})
ct_names = [c['name'] for c in ct]
check("13 contract types exist", len(ct) == 13)
for expected in ['Permanent', 'Temporary', 'Full-Time', 'Part-Time', 'Intern']:
    check(f"Contract type '{expected}' exists", expected in ct_names)

print(f"\nBlog 2 Results: {passed} passed, {failed} failed")
blog2_passed = passed
blog2_failed = failed

print("\n" + "="*70)
print("BLOG 3 VERIFICATION: Stages & Email Templates")
print("="*70)

# 6 stages exist
stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', [[]],
    {'fields': ['name', 'sequence', 'fold', 'hired_stage', 'template_id',
                'job_ids', 'requirements', 'rotting_threshold_days'],
     'order': 'sequence'})
check("6 stages exist", len(stages) == 6)

# Stage names and order
expected_stages = [
    ('New', 0), ('Qualification', 1), ('First Interview', 2),
    ('Second Interview', 3), ('Contract Proposal', 4), ('Contract Signed', 5)
]
for name, seq in expected_stages:
    s = [x for x in stages if x['name'] == name]
    check(f"Stage '{name}' exists", len(s) > 0)
    if s:
        check(f"Stage '{name}' sequence is {seq}", s[0]['sequence'] == seq)

# New stage has Application Acknowledgement template
new_stage = [s for s in stages if s['name'] == 'New'][0]
check("New stage has email template", new_stage['template_id'] != False)
check("New stage template is Application Acknowledgement",
      'Application Acknowledgement' in str(new_stage['template_id']))

# Other stages have no templates
for name in ['Qualification', 'First Interview', 'Second Interview', 'Contract Proposal', 'Contract Signed']:
    s = [x for x in stages if x['name'] == name][0]
    check(f"Stage '{name}' has no email template", s['template_id'] == False)

# Contract Signed is folded and hired
cs = [s for s in stages if s['name'] == 'Contract Signed'][0]
check("Contract Signed is folded", cs['fold'] == True)
check("Contract Signed is hired stage", cs['hired_stage'] == True)

# Other stages not folded and not hired
for name in ['New', 'Qualification', 'First Interview', 'Second Interview', 'Contract Proposal']:
    s = [x for x in stages if x['name'] == name][0]
    check(f"Stage '{name}' is not folded", s['fold'] == False)
    check(f"Stage '{name}' is not hired stage", s['hired_stage'] == False)

# All stages global (no job_ids)
for s in stages:
    check(f"Stage '{s['name']}' is global (no job_ids)", s['job_ids'] == [])

# All stages have 0 rotting days
for s in stages:
    check(f"Stage '{s['name']}' rotting days is 0", s['rotting_threshold_days'] == 0)

# No requirements on any stage
for s in stages:
    check(f"Stage '{s['name']}' has no requirements", not s['requirements'])

# 5 email templates for recruitment
templates = models.execute_kw(DB, uid, PASSWORD, 'mail.template', 'search_read',
    [[['model_id.model', '=', 'hr.applicant']]],
    {'fields': ['name', 'subject']})
template_names = [t['name'] for t in templates]
check("5 recruitment email templates exist", len(templates) == 5)
for expected in ['Recruitment: Application Acknowledgement', 'Recruitment: Interest',
                 'Recruitment: Not interested anymore', 'Recruitment: Refuse',
                 'Recruitment: Schedule interview']:
    check(f"Template '{expected}' exists", expected in template_names)

# Template subjects
ack_tmpl = [t for t in templates if 'Acknowledgement' in t['name']][0]
check("Acknowledgement template subject contains job name placeholder",
      '{{ object.job_id.name }}' in str(ack_tmpl.get('subject', '')))

blog3_passed = passed - blog2_passed
blog3_failed = failed - blog2_failed
print(f"\nBlog 3 Results: {blog3_passed} passed, {blog3_failed} failed")

print("\n" + "="*70)
print("BLOG 4 VERIFICATION: Refuse & Talent Pools")
print("="*70)

# 6 refuse reasons
reasons = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'search_read', [[]],
    {'fields': ['name', 'template_id', 'sequence', 'active'],
     'order': 'sequence'})
check("6 refuse reasons exist", len(reasons) == 6)

# Check each reason and its template
reason_template_map = {
    'Refused by applicant: salary': 'Not interested anymore',
    'Refused by applicant: job fit': 'Not interested anymore',
    'Does not fit the job requirements': 'Refuse',
    'Job already fulfilled': 'Refuse',
    'Duplicate': 'Refuse',
    'Spam': 'Refuse'
}
for reason_name, expected_tmpl in reason_template_map.items():
    r = [x for x in reasons if x['name'] == reason_name]
    check(f"Refuse reason '{reason_name}' exists", len(r) > 0)
    if r:
        check(f"Refuse reason '{reason_name}' linked to '{expected_tmpl}' template",
              expected_tmpl in str(r[0]['template_id']))

# All refuse reasons are active
for r in reasons:
    check(f"Refuse reason '{r['name']}' is active", r['active'] == True)

# Applicant statuses
# Anitha Menon - hired
active_apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['partner_name', 'application_status', 'stage_id', 'job_id',
                'refuse_reason_id', 'priority', 'salary_expected', 'salary_proposed']})
anitha = [a for a in active_apps if a['partner_name'] == 'Anitha Menon']
check("Anitha Menon is active", len(anitha) > 0)
if anitha:
    check("Anitha Menon status is hired", anitha[0]['application_status'] == 'hired')
    check("Anitha Menon in Contract Signed", 'Contract Signed' in str(anitha[0]['stage_id']))

rahul = [a for a in active_apps if a['partner_name'] == 'Rahul Sharma']
check("Rahul Sharma is active", len(rahul) > 0)
if rahul:
    check("Rahul Sharma status is ongoing", rahul[0]['application_status'] == 'ongoing')
    check("Rahul Sharma in Qualification", 'Qualification' in str(rahul[0]['stage_id']))

# Priya Nair - archived/refused
archived_apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', False]]],
    {'fields': ['partner_name', 'application_status', 'stage_id', 'job_id',
                'refuse_reason_id']})
priya = [a for a in archived_apps if a['partner_name'] == 'Priya Nair']
check("Priya Nair is archived", len(priya) > 0)
if priya:
    check("Priya Nair status is refused", priya[0]['application_status'] == 'refused')
    check("Priya Nair refuse reason is 'Refused by applicant: job fit'",
          'job fit' in str(priya[0]['refuse_reason_id']))
    check("Priya Nair stage is New (where she was when refused)",
          'New' in str(priya[0]['stage_id']))
    check("Priya Nair job is Odoo ERP Functional Consultant",
          'Odoo ERP Functional Consultant' in str(priya[0]['job_id']))

# Talent pool model exists
try:
    tp_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.talent.pool', 'fields_get', [],
        {'attributes': ['string', 'type']})
    check("hr.talent.pool model exists", len(tp_fields) > 0)
    check("Talent pool has 'name' field", 'name' in tp_fields)
    check("Talent pool has 'pool_manager' field", 'pool_manager' in tp_fields)
    check("Talent pool has 'talent_ids' field", 'talent_ids' in tp_fields)
    check("Talent pool has 'description' field", 'description' in tp_fields)
    check("Talent pool has 'categ_ids' field (tags)", 'categ_ids' in tp_fields)
    check("Talent pool has 'company_id' field", 'company_id' in tp_fields)
except:
    check("hr.talent.pool model exists", False)

# No talent pools created yet
pools = models.execute_kw(DB, uid, PASSWORD, 'hr.talent.pool', 'search_read', [[]],
    {'fields': ['name']})
check("No talent pools exist yet", len(pools) == 0)

# Applicant has talent pool fields
app_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get', [],
    {'attributes': ['string', 'type']})
check("Applicant has talent_pool_ids field", 'talent_pool_ids' in app_fields)
check("Applicant has talent_pool_count field", 'talent_pool_count' in app_fields)
check("Applicant has refuse_reason_id field", 'refuse_reason_id' in app_fields)
check("Applicant has refuse_date field", 'refuse_date' in app_fields)
check("Applicant has application_status field", 'application_status' in app_fields)

# Application status is selection with correct options
check("application_status is selection type", app_fields['application_status']['type'] == 'selection')

blog4_passed = passed - blog2_passed - blog3_passed
blog4_failed = failed - blog2_failed - blog3_failed
print(f"\nBlog 4 Results: {blog4_passed} passed, {blog4_failed} failed")

print("\n" + "="*70)
print(f"OVERALL: {passed} PASSED / {passed + failed} TOTAL ({failed} FAILED)")
print("="*70)
