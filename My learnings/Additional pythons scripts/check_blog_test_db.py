#!/usr/bin/env python3
"""Connect to blog-test.odoo.com and check current state."""
import xmlrpc.client

URL = 'https://blog-test.odoo.com'
DB = 'blog-test'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

print('Connecting to', URL, '...')
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
ver = common.version()
print('Server version:', ver.get('server_version'))

uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print('UID:', uid)

if not uid:
    print('AUTH FAILED - trying admin@example.com...')
    uid = common.authenticate(DB, 'admin', 'admin', {})
    print('UID with admin:', uid)

if uid:
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    # Check installed modules
    mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
        [[['state', '=', 'installed']]],
        {'fields': ['name', 'shortdesc'], 'order': 'name'})
    print(f'\nInstalled modules ({len(mods)}):')
    for m in mods:
        name = m['name']
        desc = m['shortdesc']
        print(f'  {name:35s} {desc}')
    
    # Check existing products
    products = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'search_read',
        [[]], {'fields': ['name'], 'limit': 20})
    print(f'\nExisting products ({len(products)}):')
    for p in products:
        print(f'  {p["name"]}')
    
    # Check existing contacts
    contacts = models.execute_kw(DB, uid, PASSWORD, 'res.partner', 'search_read',
        [[['is_company', '=', True]]], {'fields': ['name'], 'limit': 20})
    print(f'\nExisting companies ({len(contacts)}):')
    for c in contacts:
        print(f'  {c["name"]}')
else:
    print('Cannot authenticate!')
