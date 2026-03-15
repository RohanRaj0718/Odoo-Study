import xmlrpc.client
URL='https://client-cient.odoo.com'; DB='client-cient'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/common',allow_none=True)
uid=common.authenticate(DB,U,P,{})
models=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/object',allow_none=True)

# Check current quants
quants = models.execute_kw(DB,uid,P,'stock.quant','search_read',
    [[['location_id.usage','=','internal']]],
    {'fields':['product_id','location_id','quantity','inventory_quantity']})
print(f'Stock quants: {len(quants)}')
for q in quants:
    pname = q['product_id'][1] if q['product_id'] else 'N/A'
    lname = q['location_id'][1] if q['location_id'] else 'N/A'
    qty = q['quantity']
    inv = q['inventory_quantity']
    print(f'  {pname} @ {lname}: qty={qty}, inv_qty={inv}')

# If quants exist with inventory_quantity but quantity=0, try applying
for q in quants:
    if q['quantity'] == 0 and q['inventory_quantity'] > 0:
        print(f'\n  Applying inventory for quant {q["id"]}...')
        try:
            models.execute_kw(DB,uid,P,'stock.quant','action_apply_inventory',[[q['id']]])
        except Exception as e:
            # The None return error is expected, action still works
            if 'None' in str(e) or 'allow_none' in str(e):
                print(f'  Applied (ignore None error)')
            else:
                print(f'  Error: {e}')

# Re-check
quants2 = models.execute_kw(DB,uid,P,'stock.quant','search_read',
    [[['location_id.usage','=','internal']]],
    {'fields':['product_id','location_id','quantity','inventory_quantity']})
print(f'\nAfter apply - Stock quants: {len(quants2)}')
for q in quants2:
    pname = q['product_id'][1] if q['product_id'] else 'N/A'
    lname = q['location_id'][1] if q['location_id'] else 'N/A'
    qty = q['quantity']
    inv = q['inventory_quantity']
    print(f'  {pname} @ {lname}: qty={qty}, inv_qty={inv}')
