import xmlrpc.client
URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read', 
    [[['name', '=', 'Odoo ERP Functional Consultant']]],
    {'fields': ['name', 'no_of_recruitment', 'expected_employees', 'no_of_hired_employee', 'no_of_employee', 'applicant_hired']})
for j in jobs:
    for k, v in j.items():
        print(f"{k}: {v}")
