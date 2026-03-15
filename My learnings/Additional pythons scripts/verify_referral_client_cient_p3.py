#!/usr/bin/env python3
"""
Pass 3: Get applicant and employee data from client-cient.odoo.com (fixed fields).
"""

import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def main():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def search_read(model, domain=[], fields=[], limit=0):
        kw = {'fields': fields}
        if limit:
            kw['limit'] = limit
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

    # ── Active Applicants ──
    print("=" * 70)
    print("ACTIVE APPLICANTS (fixed)")
    print("=" * 70)
    applicants = search_read('hr.applicant', [('active','=',True)],
                              ['partner_name','stage_id','job_id','priority',
                               'ref_user_id','user_id','department_id','kanban_state',
                               'date_closed','create_date'])
    print(f"Total active: {len(applicants)}")
    for a in applicants:
        print(f"\n  Name: {a.get('partner_name','N/A')}")
        print(f"    Stage: {a.get('stage_id', 'N/A')}")
        print(f"    Job: {a.get('job_id', 'N/A')}")
        print(f"    Priority: {a.get('priority', 'N/A')}")
        print(f"    Referred By: {a.get('ref_user_id', 'None')}")
        print(f"    Recruiter: {a.get('user_id', 'N/A')}")
        print(f"    Department: {a.get('department_id', 'N/A')}")
        print(f"    Kanban: {a.get('kanban_state', 'N/A')}")
        print(f"    Hire Date: {a.get('date_closed', 'N/A')}")
        print(f"    Applied: {a.get('create_date', 'N/A')}")

    # ── Archived Applicants ──
    print("\n" + "=" * 70)
    print("ARCHIVED APPLICANTS")
    print("=" * 70)
    archived = search_read('hr.applicant', [('active','=',False)],
                            ['partner_name','stage_id','job_id','priority',
                             'ref_user_id','create_date','kanban_state'])
    print(f"Total archived: {len(archived)}")
    for a in archived:
        print(f"\n  Name: {a.get('partner_name','N/A')}")
        print(f"    Stage: {a.get('stage_id', 'N/A')}")
        print(f"    Job: {a.get('job_id', 'N/A')}")
        print(f"    Priority: {a.get('priority', 'N/A')}")

    # ── Employees ──
    print("\n" + "=" * 70)
    print("EMPLOYEES (all)")
    print("=" * 70)
    emps = search_read('hr.employee', [], ['name','department_id','job_id','company_id','job_title'])
    print(f"Total employees: {len(emps)}")
    for e in emps:
        print(f"  {e['name']:30s} | Dept: {e.get('department_id','N/A')}")
        print(f"    Job: {e.get('job_id','N/A')} | Title: {e.get('job_title','N/A')}")
        print(f"    Company: {e.get('company_id','N/A')}")

    # ── Check employee_id on applicants ──
    print("\n" + "=" * 70)
    print("FINDING CORRECT EMPLOYEE LINK FIELD")
    print("=" * 70)
    af = search_read('hr.applicant', [('active','=',True)], [], limit=1)
    if af:
        emp_fields = [k for k in af[0].keys() if 'emp' in k.lower() or 'employee' in k.lower()]
        print(f"Fields with 'emp/employee': {emp_fields}")

    # ── Published status check ──
    print("\n" + "=" * 70)
    print("JOB PUBLISHED STATUS (checking is_published vs website_published)")
    print("=" * 70)
    jobs = search_read('hr.job', [], ['name','website_published','is_published'])
    for j in jobs:
        print(f"  {j['name']:40s} | web_published={j.get('website_published')} | is_published={j.get('is_published')}")

    print("\n" + "=" * 70)
    print("PASS 3 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
