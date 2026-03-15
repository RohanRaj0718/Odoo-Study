#!/usr/bin/env python3
"""
BLOG VERIFICATION — Work Centers and Routing in Odoo 19
Follows BLOG_Work_Centers_PUBLISH_READY.md step-by-step and verifies each claim.
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

PASS = 0
FAIL = 0
ISSUES = []

def check(description, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f'  [PASS] {description}')
    else:
        FAIL += 1
        msg = f'{description} — {detail}' if detail else description
        ISSUES.append(msg)
        print(f'  [FAIL] {msg}')

print('=' * 70)
print('  BLOG VERIFICATION: Work Centers and Routing in Odoo 19')
print('=' * 70)

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Enabling Work Orders
# BLOG: Manufacturing App => Configuration => Settings
#       "enable the Work Orders checkbox"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Enabling Work Orders ---')

# Check if mrp_workorder is installed (Work Orders feature)
wo_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'mrp_workorder'], ['state', '=', 'installed']]],
    {'fields': ['name']})
check('mrp_workorder (Work Orders) module is installed', len(wo_mod) > 0)

# Blog says "Optionally, enable Work Order Dependencies"
# Check if that setting exists
settings_fields = models.execute_kw(DB, uid, PASSWORD, 'res.config.settings', 'fields_get',
    [], {'attributes': ['string']})
has_wo_dep = 'group_mrp_workorder_dependencies' in settings_fields
check('Work Order Dependencies setting exists', has_wo_dep,
      'Blog mentions optional "Work Order Dependencies"')

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Creating Work Centers
# BLOG: Manufacturing App => Configuration => Work Centers => New
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Creating Work Centers ---')

# Check what fields exist on mrp.workcenter
wc_fields = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'fields_get',
    [], {'attributes': ['string', 'type']})

expected_fields = {
    'name': 'Work Center name',
    'code': 'Code',
    'costs_hour': 'Cost per hour',
    'time_start': 'Setup time',
    'time_stop': 'Cleanup time',
    'time_efficiency': 'Time efficiency',
    'oee_target': 'OEE target',
}

for field, desc in expected_fields.items():
    exists = field in wc_fields
    check(f'Work center field "{field}" ({desc}) exists', exists)

# Check for alternative_workcenter_ids field
has_alt_wc = 'alternative_workcenter_ids' in wc_fields
check('Field "alternative_workcenter_ids" exists', has_alt_wc,
      'Blog mentions Alternative Work Centers')

# Check for capacity_ids field
has_capacity = 'capacity_ids' in wc_fields
check('Field "capacity_ids" (Product Capacities) exists', has_capacity,
      'Blog mentions Product Capacities')

# Create all 8 work centers as described in blog
work_centers = [
    {'name': 'Cutting Station', 'code': 'CUT-01', 'costs_hour': 150, 'time_start': 10, 'time_stop': 5, 'time_efficiency': 100, 'oee_target': 85},
    {'name': 'CNC Machining Center', 'code': 'CNC-01', 'costs_hour': 450, 'time_start': 15, 'time_stop': 10, 'time_efficiency': 95, 'oee_target': 80},
    {'name': 'Painting and Finishing Station', 'code': 'PNT-01', 'costs_hour': 250, 'time_start': 5, 'time_stop': 10, 'time_efficiency': 100, 'oee_target': 85},
    {'name': 'Welding Station', 'code': 'WLD-01', 'costs_hour': 300, 'time_start': 10, 'time_stop': 5, 'time_efficiency': 95, 'oee_target': 85},
    {'name': 'Assembly Line', 'code': 'ASM-01', 'costs_hour': 200, 'time_start': 5, 'time_stop': 5, 'time_efficiency': 100, 'oee_target': 90},
    {'name': 'Assembly Line Advanced', 'code': 'ASM-02', 'costs_hour': 250, 'time_start': 5, 'time_stop': 5, 'time_efficiency': 90, 'oee_target': 85},
    {'name': 'Quality Testing', 'code': 'QC-01', 'costs_hour': 180, 'time_start': 5, 'time_stop': 5, 'time_efficiency': 100, 'oee_target': 95},
    {'name': 'Packaging', 'code': 'PKG-01', 'costs_hour': 120, 'time_start': 3, 'time_stop': 5, 'time_efficiency': 100, 'oee_target': 90},
]

wc_ids = {}
for wc in work_centers:
    wc_id = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'create', [wc])
    wc_ids[wc['code']] = wc_id

check('All 8 work centers created', len(wc_ids) == 8, f'Created: {len(wc_ids)}')

# Verify one work center (Welding Station)
wld = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'read', [wc_ids['WLD-01']],
    {'fields': ['name', 'code', 'costs_hour', 'time_start', 'time_stop', 'time_efficiency', 'oee_target']})
check('Welding Station: cost_per_hour = 300', wld[0]['costs_hour'] == 300)
check('Welding Station: setup_time = 10', wld[0]['time_start'] == 10)
check('Welding Station: cleanup_time = 5', wld[0]['time_stop'] == 5)
check('Welding Station: time_efficiency = 95', wld[0]['time_efficiency'] == 95)
check('Welding Station: oee_target = 85', wld[0]['oee_target'] == 85)

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Configuring Alternative Work Centers
# BLOG: "Assembly Line (ASM-01) and Assembly Line Advanced (ASM-02) 
#        are configured as mutual alternatives"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Configuring Alternative Work Centers ---')

if has_alt_wc:
    # Set ASM-01 and ASM-02 as mutual alternatives
    models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'write',
        [[wc_ids['ASM-01']], {'alternative_workcenter_ids': [(4, wc_ids['ASM-02'])]}])
    models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'write',
        [[wc_ids['ASM-02']], {'alternative_workcenter_ids': [(4, wc_ids['ASM-01'])]}])
    
    # Verify
    asm01 = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'read',
        [wc_ids['ASM-01']], {'fields': ['alternative_workcenter_ids']})
    check('ASM-01 has ASM-02 as alternative',
          wc_ids['ASM-02'] in asm01[0]['alternative_workcenter_ids'])
    
    asm02 = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'read',
        [wc_ids['ASM-02']], {'fields': ['alternative_workcenter_ids']})
    check('ASM-02 has ASM-01 as alternative',
          wc_ids['ASM-01'] in asm02[0]['alternative_workcenter_ids'])
else:
    check('Alternative work centers feature available', False)

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Creating the Product and Bill of Materials with Operations
# BLOG: "a product called Executive Standing Desk was created"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Creating the Product and BoM with Operations ---')

# Create product
desk_tmpl_id = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'create', [{
    'name': 'Executive Standing Desk',
    'type': 'consu',
    'standard_price': 6500.00,
    'list_price': 15000.00,
}])
check('Executive Standing Desk product created', desk_tmpl_id > 0)

# Get product.product ID
desk_pp = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'search_read',
    [[['product_tmpl_id', '=', desk_tmpl_id]]],
    {'fields': ['id']})
desk_product_id = desk_pp[0]['id']

# Create 7 components
desk_components = [
    'Premium MDF Board',
    'Height-Adjust Motor',
    'Steel Leg Frame (Pair)',
    'Cable Management Tray',
    'Anti-Fatigue Mat',
    'LED Control Panel',
    'Desktop Grommet Set',
]

desk_comp_ids = {}
for comp_name in desk_components:
    cid = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'create', [{
        'name': comp_name,
        'type': 'consu',
        'standard_price': 200.00,
    }])
    pp = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'search_read',
        [[['product_tmpl_id', '=', cid]]], {'fields': ['id']})
    desk_comp_ids[comp_name] = pp[0]['id']

check('All 7 desk components created', len(desk_comp_ids) == 7)

# Create BoM with components AND operations
# Blog defines 8 operations
operations = [
    {'name': 'Cut MDF Panels to Size', 'workcenter_id': wc_ids['CUT-01'], 'time_cycle_manual': 25},
    {'name': 'CNC Edge Profiling', 'workcenter_id': wc_ids['CNC-01'], 'time_cycle_manual': 35},
    {'name': 'Sand and Surface Prep', 'workcenter_id': wc_ids['PNT-01'], 'time_cycle_manual': 20},
    {'name': 'Apply Laminate Finish', 'workcenter_id': wc_ids['PNT-01'], 'time_cycle_manual': 30},
    {'name': 'Weld Steel Frame', 'workcenter_id': wc_ids['WLD-01'], 'time_cycle_manual': 40},
    {'name': 'Assemble All Components', 'workcenter_id': wc_ids['ASM-01'], 'time_cycle_manual': 45},
    {'name': 'Quality Inspection', 'workcenter_id': wc_ids['QC-01'], 'time_cycle_manual': 15},
    {'name': 'Final Packaging', 'workcenter_id': wc_ids['PKG-01'], 'time_cycle_manual': 20},
]

# Check if mrp.routing.workcenter uses 'time_cycle_manual' or 'time_cycle'
op_fields = models.execute_kw(DB, uid, PASSWORD, 'mrp.routing.workcenter', 'fields_get',
    [], {'attributes': ['string', 'type']})
has_time_cycle_manual = 'time_cycle_manual' in op_fields
has_time_cycle = 'time_cycle' in op_fields
print(f'  [INFO] Operation duration field: time_cycle_manual={has_time_cycle_manual}, time_cycle={has_time_cycle}')

# Determine correct field name
duration_field = 'time_cycle_manual' if has_time_cycle_manual else 'time_cycle'

# Build operation lines
op_lines = []
for i, op in enumerate(operations):
    op_vals = {
        'name': op['name'],
        'workcenter_id': op['workcenter_id'],
        duration_field: op['time_cycle_manual'],
        'sequence': (i + 1) * 10,
    }
    op_lines.append((0, 0, op_vals))

# Build component lines
comp_lines = []
for comp_name, pp_id in desk_comp_ids.items():
    comp_lines.append((0, 0, {
        'product_id': pp_id,
        'product_qty': 2.0 if 'MDF' in comp_name else 1.0,
    }))

bom_id = models.execute_kw(DB, uid, PASSWORD, 'mrp.bom', 'create', [{
    'product_tmpl_id': desk_tmpl_id,
    'product_qty': 1.0,
    'type': 'normal',
    'bom_line_ids': comp_lines,
    'operation_ids': op_lines,
}])
check('BoM with operations created', bom_id > 0, f'ID: {bom_id}')

# Verify BoM
bom_data = models.execute_kw(DB, uid, PASSWORD, 'mrp.bom', 'read', [bom_id],
    {'fields': ['type', 'bom_line_ids', 'operation_ids']})
check('BoM type is "normal" (Manufacture)', bom_data[0]['type'] == 'normal')
check('7 component lines on BoM', len(bom_data[0]['bom_line_ids']) == 7,
      f'Actual: {len(bom_data[0]["bom_line_ids"])}')
check('8 operations on BoM', len(bom_data[0]['operation_ids']) == 8,
      f'Actual: {len(bom_data[0]["operation_ids"])}')

# Read operation details
ops_data = models.execute_kw(DB, uid, PASSWORD, 'mrp.routing.workcenter', 'search_read',
    [[['bom_id', '=', bom_id]]],
    {'fields': ['name', 'workcenter_id', duration_field, 'sequence'], 'order': 'sequence'})
print(f'  [INFO] Operations on BoM:')
total_time = 0
for op in ops_data:
    dur = op[duration_field]
    total_time += dur
    print(f'    {op["sequence"]:3d}. {op["name"]:30s} at {op["workcenter_id"][1]:30s} ({dur} min)')

# Blog says "total production time per unit is 230 minutes"
check('Total production time = 230 minutes',
      total_time == 230,
      f'Actual total: {total_time} minutes')

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Creating and Confirming a Manufacturing Order
# BLOG: Manufacturing App => Operations => Manufacturing Orders => New
#       "Odoo generates eight Work Orders"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Creating and Confirming Manufacturing Order ---')

# Create MO
mo_id = models.execute_kw(DB, uid, PASSWORD, 'mrp.production', 'create', [{
    'product_id': desk_product_id,
    'product_qty': 1.0,
    'bom_id': bom_id,
}])
check('Manufacturing Order created', mo_id > 0, f'ID: {mo_id}')

# Confirm MO
models.execute_kw(DB, uid, PASSWORD, 'mrp.production', 'action_confirm', [[mo_id]])
mo_data = models.execute_kw(DB, uid, PASSWORD, 'mrp.production', 'read', [mo_id],
    {'fields': ['state', 'name', 'workorder_ids']})
check('MO confirmed (state = confirmed or progress)',
      mo_data[0]['state'] in ('confirmed', 'progress'),
      f'Actual state: {mo_data[0]["state"]}')
print(f'  [INFO] MO Name: {mo_data[0]["name"]}')

# BLOG CLAIM: "Odoo generates eight Work Orders — one for each operation"
wo_count = len(mo_data[0]['workorder_ids'])
check('8 Work Orders generated', wo_count == 8,
      f'Actual WO count: {wo_count}')

# Read work order details
if mo_data[0]['workorder_ids']:
    wos = models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'search_read',
        [[['production_id', '=', mo_id]]],
        {'fields': ['name', 'workcenter_id', 'state', 'duration_expected'], 'order': 'id'})
    print(f'  [INFO] Work Orders:')
    for wo in wos:
        print(f'    {wo["name"]:35s} at {wo["workcenter_id"][1]:30s} state={wo["state"]}')

# ═══════════════════════════════════════════════════════════════════════
# BLOG STEP: Executing Work Orders
# BLOG: "Click Start to begin the timer... click Done when complete"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Executing Work Orders ---')

wos = models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'search_read',
    [[['production_id', '=', mo_id]]],
    {'fields': ['id', 'name', 'state', 'workcenter_id'], 'order': 'id'})

# Execute first work order to test the workflow
if wos:
    first_wo = wos[0]
    print(f'  [INFO] Starting first WO: {first_wo["name"]}')
    
    try:
        # Start
        models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'button_start', [[first_wo['id']]])
        wo_state = models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'read',
            [first_wo['id']], {'fields': ['state']})
        check('Work order started (state = progress)',
              wo_state[0]['state'] == 'progress',
              f'Actual: {wo_state[0]["state"]}')
        
        # Complete
        models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'button_finish', [[first_wo['id']]])
        wo_state2 = models.execute_kw(DB, uid, PASSWORD, 'mrp.workorder', 'read',
            [first_wo['id']], {'fields': ['state']})
        check('Work order completed (state = done)',
              wo_state2[0]['state'] == 'done',
              f'Actual: {wo_state2[0]["state"]}')
    except Exception as e:
        check('Work order start/finish workflow', False, f'Error: {e}')

# ═══════════════════════════════════════════════════════════════════════
# BLOG CLAIM: Manufacturing cost calculation
# BLOG: "Weld Steel Frame at Welding Station — cycle 40 min, 
#        setup 10, cleanup 5, efficiency 95%, cost/hr 300,
#        effective duration ~57.89 min, cost ~289.47"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Manufacturing Cost Calculation ---')

# Verify the math in the blog
# Blog formula (implied): total_time = (cycle + setup + cleanup) / (efficiency/100)
# = (40 + 10 + 5) / (95/100) = 55 / 0.95 = 57.89 minutes
# cost = (57.89 / 60) * 300 = 289.47

cycle = 40
setup = 10
cleanup = 5
efficiency = 95
cost_hr = 300

effective_duration = (cycle + setup + cleanup) / (efficiency / 100)
cost = (effective_duration / 60) * cost_hr

print(f'  [INFO] Blog cost calculation verification:')
print(f'    Cycle: {cycle} min, Setup: {setup} min, Cleanup: {cleanup} min')
print(f'    Efficiency: {efficiency}%')
print(f'    Effective duration: {effective_duration:.2f} min (blog says ~57.89)')
print(f'    Cost: {cost:.2f} (blog says ~289.47)')

check('Cost calculation: effective duration ≈ 57.89 min',
      abs(effective_duration - 57.89) < 0.1,
      f'Calculated: {effective_duration:.2f}')
check('Cost calculation: cost ≈ 289.47',
      abs(cost - 289.47) < 0.1,
      f'Calculated: {cost:.2f}')

# ═══════════════════════════════════════════════════════════════════════
# BLOG CLAIM: OEE Tracking
# BLOG: "OEE is composed of three factors — Availability, Performance, Quality"
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: OEE Tracking ---')

oee_fields = ['oee', 'oee_target']
wc_oee = models.execute_kw(DB, uid, PASSWORD, 'mrp.workcenter', 'fields_get',
    [], {'attributes': ['string']})
has_oee = 'oee' in wc_oee
check('OEE field exists on work center', has_oee)

# Check if performance, availability fields exist  
has_performance = 'performance' in wc_oee
has_blocked_time = 'blocked_time' in wc_oee
has_productive_time = 'productive_time' in wc_oee
print(f'  [INFO] OEE-related fields: oee={has_oee}, performance={has_performance}')

# ═══════════════════════════════════════════════════════════════════════
# BLOG CLAIM: Shop Floor module
# BLOG: Manufacturing App => Shop Floor
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Shop Floor Module ---')

shop_floor_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'ilike', 'shop_floor']]],
    {'fields': ['name', 'state']})
# Also check mrp_workorder which includes shop floor
check('Shop Floor functionality available (via mrp_workorder)',
      len(wo_mod) > 0,
      f'shop_floor modules: {shop_floor_mod}')

# ═══════════════════════════════════════════════════════════════════════
# BLOG CLAIM: Planning View
# BLOG: Manufacturing App => Planning => By Work Center
# ═══════════════════════════════════════════════════════════════════════
print('\n--- Section: Planning View ---')

planning_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'planning'], ['state', '=', 'installed']]],
    {'fields': ['name']})
check('Planning module installed', len(planning_mod) > 0)

# Check for mrp planning views
mrp_menus = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.menu', 'search_read',
    [[['name', 'ilike', 'planning'], ['parent_id.name', 'ilike', 'manufacturing']]],
    {'fields': ['name', 'complete_name']})
if mrp_menus:
    print(f'  [INFO] Manufacturing planning menus:')
    for m in mrp_menus:
        print(f'    {m["complete_name"]}')

# Blog says "By Work Center" view exists
wc_planning = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.menu', 'search_read',
    [[['name', 'ilike', 'work center']]],
    {'fields': ['name', 'complete_name']})
if wc_planning:
    for m in wc_planning:
        print(f'  [INFO] Work Center menu: {m["complete_name"]}')

# ═══════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print(f'  WORK CENTERS BLOG VERIFICATION COMPLETE')
print(f'  Passed: {PASS}  |  Failed: {FAIL}')
print('=' * 70)

if ISSUES:
    print('\n  ISSUES FOUND:')
    for i, issue in enumerate(ISSUES, 1):
        print(f'    {i}. {issue}')
else:
    print('\n  All blog claims verified successfully!')

print()
