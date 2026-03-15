#!/usr/bin/env python3
"""
Get the view arch definitions for the 3 Referral reports via XML-RPC.
This will tell us the exact default groupby, measures, etc.
"""

import xmlrpc.client

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def search_read(model, domain, fields, limit=10):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read',
                             [domain], {'fields': fields, 'limit': limit})

# Get the ir.actions.act_window for each report
print("=" * 60)
print("SEARCHING FOR REFERRAL REPORT ACTIONS")
print("=" * 60)

# Search for actions related to referral reports
actions = search_read('ir.actions.act_window', 
    [['res_model', 'in', ['hr.referral.report', 'hr.referral.reward.report', 'hr.referral.points']]],
    ['name', 'res_model', 'view_mode', 'domain', 'context', 'search_view_id', 'view_ids'],
    20)

for action in actions:
    print(f"\n--- Action: {action['name']} ---")
    print(f"  Model: {action['res_model']}")
    print(f"  View Mode: {action['view_mode']}")
    print(f"  Domain: {action['domain']}")
    print(f"  Context: {action['context']}")
    print(f"  Search View ID: {action['search_view_id']}")
    print(f"  View IDs: {action['view_ids']}")

# Get views for hr.referral.report
print("\n\n" + "=" * 60)
print("VIEWS FOR hr.referral.report")
print("=" * 60)

views = search_read('ir.ui.view',
    [['model', '=', 'hr.referral.report']],
    ['name', 'type', 'arch_db', 'priority'],
    20)

for v in views:
    print(f"\n--- View: {v['name']} (type={v['type']}, priority={v['priority']}) ---")
    arch = v.get('arch_db', '')
    if arch:
        print(f"  Arch:\n{arch}")

# Get views for hr.referral.reward.report
print("\n\n" + "=" * 60)
print("VIEWS FOR hr.referral.reward.report")
print("=" * 60)

views2 = search_read('ir.ui.view',
    [['model', '=', 'hr.referral.reward.report']],
    ['name', 'type', 'arch_db', 'priority'],
    20)

for v in views2:
    print(f"\n--- View: {v['name']} (type={v['type']}, priority={v['priority']}) ---")
    arch = v.get('arch_db', '')
    if arch:
        print(f"  Arch:\n{arch}")

# Get views for hr.referral.points
print("\n\n" + "=" * 60)
print("VIEWS FOR hr.referral.points")
print("=" * 60)

views3 = search_read('ir.ui.view',
    [['model', '=', 'hr.referral.points']],
    ['name', 'type', 'arch_db', 'priority'],
    20)

for v in views3:
    print(f"\n--- View: {v['name']} (type={v['type']}, priority={v['priority']}) ---")
    arch = v.get('arch_db', '')
    if arch:
        print(f"  Arch:\n{arch}")

# Also get the search views
print("\n\n" + "=" * 60)
print("SEARCH VIEWS")
print("=" * 60)

for model_name in ['hr.referral.report', 'hr.referral.reward.report', 'hr.referral.points']:
    search_views = search_read('ir.ui.view',
        [['model', '=', model_name], ['type', '=', 'search']],
        ['name', 'arch_db'],
        5)
    for sv in search_views:
        print(f"\n--- Search View for {model_name}: {sv['name']} ---")
        print(f"  {sv.get('arch_db', '')}")

print("\n=== DONE ===")
