#!/usr/bin/env python3
"""
Blog Verification Script — Part 1: Install mrp_subcontracting module
Then verify it's installed before proceeding.
"""
import xmlrpc.client
import time

URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
print(f'Connected as UID {uid}')

# ── Check if mrp_subcontracting is installed ──
mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'mrp_subcontracting']]],
    {'fields': ['name', 'state']})
print(f'mrp_subcontracting state: {mod[0]["state"] if mod else "NOT FOUND"}')

if mod and mod[0]['state'] != 'installed':
    print('Installing mrp_subcontracting...')
    mod_id = mod[0]['id']
    models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', [[mod_id]])
    print('Installation triggered. Waiting 15s for completion...')
    time.sleep(15)
    
    # Re-authenticate after module install
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    # Verify
    mod2 = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
        [[['name', '=', 'mrp_subcontracting']]],
        {'fields': ['name', 'state']})
    print(f'After install: {mod2[0]["state"]}')
elif mod and mod[0]['state'] == 'installed':
    print('Already installed!')

# Also check mrp_workorder 
wo_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'mrp_workorder']]],
    {'fields': ['name', 'state']})
print(f'mrp_workorder state: {wo_mod[0]["state"] if wo_mod else "NOT FOUND"}')

# Check for subcontracting-related settings
# After installing subcontracting, check the routes created
routes = models.execute_kw(DB, uid, PASSWORD, 'stock.route', 'search_read',
    [[['name', 'ilike', 'subcontract']]],
    {'fields': ['name', 'active']})
print(f'\nSubcontracting routes found:')
for r in routes:
    print(f'  {r["name"]} (active={r["active"]})')

print('\n=== Module setup complete ===')
