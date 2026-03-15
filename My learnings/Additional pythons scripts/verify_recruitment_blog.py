"""
FINAL VERIFICATION: Cross-check every claim in the recruitment blog against demo DB
"""
import xmlrpc.client

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label} — {detail}")

print("="*70)
print("BLOG VERIFICATION: Recruitment Workflow in Odoo 19")
print("="*70)

# 1. Blog says: "6 default stages"
stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read', 
    [[]], {'order': 'sequence', 'fields': ['name', 'sequence', 'fold', 'hired_stage', 'template_id']})
check("6 default stages exist", len(stages) == 6, f"Found {len(stages)}")

# 2. Stage names match
expected_stages = ['New', 'Qualification', 'First Interview', 'Second Interview', 'Contract Proposal', 'Contract Signed']
actual_stages = [s['name'] for s in stages]
check("Stage names match: New, Qualification, First Interview, Second Interview, Contract Proposal, Contract Signed",
      actual_stages == expected_stages, f"Got {actual_stages}")

# 3. New stage has auto email template
check("New stage has 'Application Acknowledgement' email template",
      stages[0]['template_id'] and 'Acknowledgement' in stages[0]['template_id'][1],
      f"Got {stages[0]['template_id']}")

# 4. Contract Signed is folded and is hired stage
check("Contract Signed stage is folded", stages[5]['fold'] == True)
check("Contract Signed is marked as Hired Stage", stages[5]['hired_stage'] == True)

# 5. Blog says: "7 departments exist"
depts = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search_read', [[]],
    {'fields': ['name']})
dept_names = sorted([d['name'] for d in depts])
check("7 departments exist", len(depts) == 7, f"Found {len(depts)}: {dept_names}")
check("IT / Consulting department exists", 'IT / Consulting' in dept_names, f"Departments: {dept_names}")

# 6. Job position: Odoo ERP Functional Consultant
jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', 
    [[['name', '=', 'Odoo ERP Functional Consultant']]],
    {'fields': ['name', 'department_id', 'no_of_recruitment', 'user_id', 'is_published',
                'website_url', 'contract_type_id', 'application_count', 'no_of_hired_employee']})
check("Job 'Odoo ERP Functional Consultant' exists", len(jobs) == 1)
if jobs:
    j = jobs[0]
    check("Job department is IT / Consulting", j['department_id'] and j['department_id'][1] == 'IT / Consulting',
          f"Got {j['department_id']}")
    check("Job target is 2", j['no_of_recruitment'] == 2, f"Got {j['no_of_recruitment']}")
    check("Job recruiter is Rohan Raj", j['user_id'] and j['user_id'][1] == 'Rohan Raj',
          f"Got {j['user_id']}")
    check("Job is published", j['is_published'] == True)
    check("Job has website URL", bool(j['website_url']), f"Got {j['website_url']}")
    check("Job contract type is Permanent", j['contract_type_id'] and j['contract_type_id'][1] == 'Permanent',
          f"Got {j['contract_type_id']}")
    check("Job has 2 applications", j['application_count'] == 2, f"Got {j['application_count']}")
    check("Job has 1 hired", j['no_of_hired_employee'] == 1, f"Got {j['no_of_hired_employee']}")
    job_id = j['id']

    # 7. Applicant: Anitha Menon — hired
    anitha = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
        [[['partner_name', '=', 'Anitha Menon'], ['job_id', '=', job_id]]],
        {'fields': ['partner_name', 'stage_id', 'priority', 'salary_expected', 'salary_proposed',
                    'email_from', 'partner_phone', 'employee_id', 'date_closed',
                    'salary_expected_extra', 'salary_proposed_extra', 'linkedin_profile']})
    check("Anitha Menon applicant exists", len(anitha) == 1)
    if anitha:
        a = anitha[0]
        check("Anitha is in Contract Signed stage", a['stage_id'] and a['stage_id'][1] == 'Contract Signed',
              f"Got {a['stage_id']}")
        check("Anitha evaluation is Very Good (2)", a['priority'] == '2', f"Got {a['priority']}")
        check("Anitha expected salary is 55000", a['salary_expected'] == 55000.0, f"Got {a['salary_expected']}")
        check("Anitha proposed salary is 52000", a['salary_proposed'] == 52000.0, f"Got {a['salary_proposed']}")
        check("Anitha email is anitha.menon@example.com", a['email_from'] == 'anitha.menon@example.com',
              f"Got {a['email_from']}")
        check("Anitha has employee record", bool(a['employee_id']), f"Got {a['employee_id']}")
        check("Anitha hire date is set", bool(a['date_closed']), f"Got {a['date_closed']}")
        check("Anitha has LinkedIn profile", bool(a['linkedin_profile']))
        
        if a['employee_id']:
            emp = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'read', [a['employee_id'][0]],
                {'fields': ['name', 'department_id', 'job_id', 'job_title']})
            if emp:
                e = emp[0]
                check("Employee name is Anitha Menon", e['name'] == 'Anitha Menon')
                check("Employee dept is IT / Consulting", e['department_id'] and e['department_id'][1] == 'IT / Consulting')
                check("Employee job position matches", e['job_id'] and 'Odoo ERP Functional Consultant' in e['job_id'][1])
                check("Employee job title matches", 'Odoo ERP Functional Consultant' in str(e.get('job_title', '')))

    # 8. Applicant: Rahul Sharma — in Qualification
    rahul = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
        [[['partner_name', '=', 'Rahul Sharma'], ['job_id', '=', job_id]]],
        {'fields': ['partner_name', 'stage_id', 'priority', 'salary_expected', 'email_from']})
    check("Rahul Sharma applicant exists", len(rahul) == 1)
    if rahul:
        r = rahul[0]
        check("Rahul is in Qualification stage", r['stage_id'] and r['stage_id'][1] == 'Qualification',
              f"Got {r['stage_id']}")
        check("Rahul evaluation is Good (1)", r['priority'] == '1', f"Got {r['priority']}")
        check("Rahul expected salary is 60000", r['salary_expected'] == 60000.0, f"Got {r['salary_expected']}")

    # 9. Applicant: Priya Nair — refused/archived
    priya = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
        [[['partner_name', '=', 'Priya Nair'], ['job_id', '=', job_id], ['active', '=', False]]],
        {'fields': ['partner_name', 'active', 'refuse_reason_id']})
    check("Priya Nair is archived (refused)", len(priya) == 1)
    if priya:
        check("Priya has a refuse reason", bool(priya[0]['refuse_reason_id']), 
              f"Got {priya[0]['refuse_reason_id']}")

# 10. Blog says Manufacturing Manager is also published
mfg = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read',
    [[['name', '=', 'Manufacturing Manager']]],
    {'fields': ['is_published']})
check("Manufacturing Manager is published", mfg and mfg[0]['is_published'] == True)

# 11. Refuse reasons exist
reasons = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant.refuse.reason', 'search_read',
    [[]], {'fields': ['name']})
reason_names = [r['name'] for r in reasons]
check("Refuse reasons exist (6)", len(reasons) >= 5, f"Found {len(reasons)}: {reason_names}")
check("'Does not fit the job requirements' reason exists", 
      any('fit' in r.lower() or 'requirement' in r.lower() for r in reason_names),
      f"Reasons: {reason_names}")

# 12. Employment types
types = models.execute_kw(DB, uid, PASSWORD, 'hr.contract.type', 'search_read', [[]],
    {'fields': ['name']})
type_names = [t['name'] for t in types]
check("Employment type 'Permanent' exists", 'Permanent' in type_names)
check("Employment type 'Full-Time' exists", 'Full-Time' in type_names)
check("Employment type 'Intern' exists", 'Intern' in type_names)

# 13. Modules installed
mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'in', ['hr_recruitment', 'website_hr_recruitment', 'hr_recruitment_survey']],
      ['state', '=', 'installed']]],
    {'fields': ['name']})
mod_names = [m['name'] for m in mods]
check("hr_recruitment installed", 'hr_recruitment' in mod_names)
check("website_hr_recruitment installed", 'website_hr_recruitment' in mod_names)
check("hr_recruitment_survey installed", 'hr_recruitment_survey' in mod_names)

# Summary
print("\n" + "="*70)
print(f"VERIFICATION COMPLETE: {passed} PASSED, {failed} FAILED out of {passed+failed} checks")
print("="*70)
