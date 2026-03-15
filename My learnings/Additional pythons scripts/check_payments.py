import xmlrpc.client
URL='https://client-cient.odoo.com'; DB='client-cient'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
uid = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB,U,P,{})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

pays = m.execute_kw(DB,uid,P,'account.payment','search_read',[[]], 
    {'fields':['partner_id','amount','state','company_id','payment_type','partner_type','date'], 'limit':50})
print(f'Total payments: {len(pays)}')
for p in pays:
    cname = p['company_id'][1][:15] if p['company_id'] else 'N/A'
    pname = p['partner_id'][1][:25] if p['partner_id'] else 'N/A'
    print(f"  ID={p['id']:3d} | {cname:15s} | {pname:25s} | {p['payment_type']:8s} | {p['amount']:>10,.2f} | state={p['state']} | {p['date']}")
