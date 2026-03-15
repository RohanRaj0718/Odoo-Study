# ODOO MANUFACTURING (MRP) - COMPLETE WORKFLOW
# From Setup to Delivery - Step-by-Step Guide
================================================================================

This document provides a complete, practical workflow for manufacturing in Odoo,
from initial setup through product delivery. Follow these steps in sequence to
implement a full manufacturing process.

================================================================================
## PHASE 1: INITIAL SETUP & CONFIGURATION
================================================================================

### STEP 1: INSTALL AND ACTIVATE MANUFACTURING MODULE
--------------------------------------------------------------------------------
1. Go to Apps
2. Search for "Manufacturing"
3. Click "Install"
4. Wait for installation to complete
5. Refresh browser

Result: Manufacturing module is now active in your Odoo instance.


### STEP 2: CONFIGURE COMPANY SETTINGS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Configuration → Settings

Enable Required Features:
□ Work Orders - For detailed routing and work center management
□ Maintenance - For equipment tracking and preventative tasks
□ Quality Control - For quality checkpoints in production
□ Product Lifecycle Management (PLM) - For version control of BoMs
□ Subcontracting - If using external manufacturers
□ Barcode Support - For mobile operations

Save Settings.


### STEP 3: SET UP WORK CENTERS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Configuration → Work Centers

For Each Work Center:
1. Click "Create"
2. Enter Work Center Name (e.g., "Assembly Station 1", "CNC Machine")
3. Configure:
   - Working Schedule: Set operating hours
   - Time Efficiency: Default 100%
   - Capacity: Number of products per cycle
   - Time Before Production: Setup time in minutes
   - Time After Production: Cleanup time in minutes
   - Cost per Hour: Labor/equipment cost rate
   
4. (Optional) Define Alternative Work Centers for flexibility
5. Click "Save"

Repeat for all production stations in your facility.


### STEP 4: CREATE PRODUCT CATEGORIES
--------------------------------------------------------------------------------
Navigation: Inventory → Configuration → Product Categories

1. Click "Create"
2. Enter Category Name (e.g., "Manufactured Products", "Raw Materials")
3. Set Costing Method:
   - FIFO (First In, First Out) - Best for most manufacturers
   - AVCO (Average Cost) - Good for stable pricing
   - Standard Price - For cost control environments
4. Set Inventory Valuation: Automated (perpetual)
5. Click "Save"


### STEP 5: CREATE RAW MATERIAL PRODUCTS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Products → Products

For Each Raw Material:
1. Click "Create"
2. Fill in:
   - Product Name
   - Can be Sold: ☐ Unchecked
   - Can be Purchased: ☑ Checked
   - Product Type: Storable Product
   - Product Category: Raw Materials
   - Unit of Measure: (Pieces, Kg, Meters, etc.)
   - Cost: Purchase price
   
3. Go to "Inventory" tab:
   - Set reordering rules if needed
   
4. Go to "Purchase" tab:
   - Add vendor information
   - Set vendor lead time
   
5. Click "Save"

Repeat for all components needed in manufacturing.


### STEP 6: CREATE FINISHED PRODUCT
--------------------------------------------------------------------------------
Navigation: Manufacturing → Products → Products

1. Click "Create"
2. Fill in:
   - Product Name
   - Can be Sold: ☑ Checked
   - Can be Purchased: ☐ Unchecked (unless also bought)
   - Product Type: Storable Product
   - Product Category: Manufactured Products
   - Sales Price: Customer-facing price
   
3. Go to "Inventory" tab:
   - Routes: Select "Manufacture"
   - Customer Lead Time: Days from order to delivery
   - Manufacturing Lead Time: Days to produce
   
4. Click "Save"


================================================================================
## PHASE 2: BILL OF MATERIALS (BOM) CREATION
================================================================================

### STEP 7: CREATE BILL OF MATERIALS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Products → Bill of Materials

1. Click "Create"
2. Fill in Header:
   - Product: Select your finished product
   - BoM Reference: Optional internal code
   - BoM Type: "Manufacture this product"
   - Quantity: Usually 1 (quantity of finished product produced)
   
3. ADD COMPONENTS (Components Tab):
   Click "Add a line" for each raw material:
   - Component: Select raw material product
   - Quantity: Amount needed per finished product
   - Unit of Measure: Must match component UoM
   
   Repeat for all components needed.
   
4. ADD OPERATIONS (Operations Tab):
   Click "Add a line" for each production step:
   - Operation: Name the step (e.g., "Assembly", "Quality Check")
   - Work Center: Select where operation occurs
   - Default Duration: Expected time in minutes
   - (Optional) Sequence: Order of operations
   
   Repeat for all production steps.
   
5. (Optional) BY-PRODUCTS Tab:
   Add any secondary products created during manufacturing
   
6. (Optional) MISCELLANEOUS Tab:
   - Set specific routing if needed
   - Configure consumption settings

7. Click "Save"

Result: Complete BoM defining how to manufacture your product.


### STEP 8: TEST THE BOM (Optional but Recommended)
--------------------------------------------------------------------------------
1. Open the BoM you just created
2. Click "Structure & Cost" button (top right)
3. Review:
   - Component list with quantities
   - Operations with time estimates
   - Cost breakdown (materials + labor + overhead)
   - Total manufacturing cost
   
4. Verify accuracy
5. Make corrections if needed


================================================================================
## PHASE 3: PROCUREMENT & INVENTORY SETUP
================================================================================

### STEP 9: SET UP VENDORS (If Not Already Done)
--------------------------------------------------------------------------------
Navigation: Purchase → Orders → Vendors

1. Click "Create"
2. Enter:
   - Vendor Name
   - Address
   - Contact Information
   - Payment Terms
   - Currency
   
3. Click "Save"


### STEP 10: CREATE PURCHASE ORDER FOR RAW MATERIALS
--------------------------------------------------------------------------------
Navigation: Purchase → Orders → Purchase Orders

1. Click "Create"
2. Fill in:
   - Vendor: Select supplier
   - Order Date: Today
   
3. Click "Add a product" in Order Lines:
   - Product: Select raw material
   - Quantity: Amount to purchase
   - Unit Price: Cost per unit
   
4. Repeat for all materials needed
5. Review Total
6. Click "Confirm Order"
7. Note the "Receipt" smart button appears

Result: Purchase Order is confirmed, waiting for goods receipt.


### STEP 11: RECEIVE MATERIALS (Warehouse Receipt)
--------------------------------------------------------------------------------
Navigation: From PO, click "Receipt" smart button 
OR: Inventory → Operations → Receipts

1. Open the receipt linked to your PO
2. For each product line:
   - Verify Quantity
   - (If using) Scan barcode
   - (If tracking) Enter lot/serial numbers
   
3. (Optional) Set destination location
4. Click "Validate"

Result: Materials are now in inventory and available for manufacturing.


### STEP 12: VERIFY INVENTORY LEVELS
--------------------------------------------------------------------------------
Navigation: Inventory → Products → Products

1. Find your raw material products
2. Check "Quantity On Hand" column
3. Verify sufficient quantities for production

Alternatively:
Navigation: Inventory → Reporting → Locations

View inventory across all locations.


================================================================================
## PHASE 4: MANUFACTURING ORDER CREATION & PLANNING
================================================================================

### STEP 13: CREATE MANUFACTURING ORDER (Manual)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Operations → Manufacturing Orders

1. Click "Create"
2. Fill in:
   - Product: Select product to manufacture
   - Quantity to Produce: Enter amount
   - Bill of Material: Auto-selected (verify correct one)
   - Scheduled Date: When production should start
   
3. Review "Components" tab:
   - All components from BoM are listed
   - Quantities calculated automatically
   
4. Review "Work Orders" tab:
   - All operations from BoM routing are listed
   - Work centers assigned
   
5. Click "Confirm"

Result: Manufacturing Order is confirmed. Components are reserved.

Status Changes: Draft → Confirmed


### STEP 14 (ALTERNATIVE): CREATE MO FROM SALES ORDER (Make-to-Order)
--------------------------------------------------------------------------------
Prerequisites: Product → Inventory tab → Routes → "Manufacture" + "Make to Order"

Navigation: Sales → Orders → Quotations

1. Click "Create"
2. Fill in:
   - Customer
   - Product with MTO + Manufacture routes
   - Quantity
   
3. Click "Confirm Sale"

Result: System automatically creates Manufacturing Order linked to sales order.

Check: Manufacturing → Operations → Manufacturing Orders
You'll see new MO with reference to the sales order.


### STEP 15: CHECK COMPONENT AVAILABILITY
--------------------------------------------------------------------------------
From Manufacturing Order:

1. Open the confirmed MO
2. Look at Components tab
3. Check status indicators:
   - ✓ Green: Component available
   - ⚠ Orange: Component partially available
   - ✗ Red: Component not available
   
If components unavailable:
- Click "Replenish" button (if configured)
- OR manually create Purchase Orders
- OR adjust MO quantity
- OR delay MO scheduled date


### STEP 16: PLAN PRODUCTION (Review Capacity)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Planning → Manufacturing Orders

View Options:
- List View: All MOs with status
- Calendar View: Scheduled production timeline
- Kanban View: Grouped by status

For Each MO:
1. Verify Scheduled Date feasible
2. Check work center capacity
3. Adjust if overloaded

Advanced:
Navigation: Manufacturing → Planning → Schedule

Drag-and-drop interface for rescheduling work orders across work centers.


================================================================================
## PHASE 5: PRODUCTION EXECUTION (SHOP FLOOR)
================================================================================

### STEP 17: CHECK COMPONENTS (Pre-Production)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Operations → Manufacturing Orders

1. Open the MO ready to produce
2. Click "Check Availability" button
3. Verify all components show as available
4. If not available, system shows what's missing

When all components available:
Status: "Components Available"


### STEP 18: RESERVE COMPONENTS
--------------------------------------------------------------------------------
System automatically reserves components when MO is confirmed.

To verify:
1. Open MO
2. Components tab shows "Reserved" quantities
3. Inventory → Reporting → Stock Moves
4. See reservation details

Components are now allocated to this specific MO.


### STEP 19: START PRODUCTION (Mark as In Progress)
--------------------------------------------------------------------------------
From Manufacturing Order:

1. Open confirmed MO
2. Click "Mark as Todo" button (if needed)
3. Click "Produce" button

Alternative - From Work Order:
1. Go to work orders tab
2. Click on first work order
3. Click "Start" button

Status Changes: Confirmed → In Progress

Operators can now work on this MO.


### STEP 20: WORK ON OPERATIONS (Work Order Execution)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Operations → Work Orders
OR use Shop Floor tablet interface

For Each Operation:

A) DESKTOP VIEW:
1. Open work order
2. Click "Start"  
   - Timer begins tracking duration
   
3. Perform the work as described

4. If needed, click "Pause" (break, issue, etc.)
   - Timer stops
   
5. When finished, click "Done"
   - Records actual time
   - Work order marked complete

B) TABLET/SHOP FLOOR VIEW:
Navigation: Manufacturing → Shop Floor

1. Select your work center
2. See list of work orders assigned
3. Tap work order to open
4. Tap "Start" button
5. Follow instructions displayed
6. Tap "Done" when complete

System tracks:
- Start time
- End time  
- Duration
- Operator (if logged in)
- Actual time vs planned time


### STEP 21: CONSUME COMPONENTS (Automatic or Manual)
--------------------------------------------------------------------------------
Components can be consumed:
- Automatically when MO marked as done
- During production (component by component)

MANUAL CONSUMPTION DURING PRODUCTION:
1. From MO, go to Components tab
2. Click on component line
3. Click "Consume"
4. Adjust quantity if needed
5. (If tracked) Enter lot/serial numbers
6. Click "Confirm"

BARCODE CONSUMPTION:
1. Open Barcode app on mobile/tablet
2. Scan MO barcode
3. Scan component barcodes
4. System records consumption
5. Real-time inventory update


### STEP 22: QUALITY CHECKS (If Configured)
--------------------------------------------------------------------------------
If Quality Control Points are set up:

During Production:
1. Quality check popup appears at configured step
2. Operator performs inspection
3. Records Pass/Fail
4. If fail: Alert triggered, MO may be blocked
5. If pass: Production continues

Types of Checks:
- Component inspection at receipt
- In-process quality checks
- Final product inspection before stock


### STEP 23: RECORD ACTUAL PRODUCTION TIME
--------------------------------------------------------------------------------
From Work Order:

1. Actual time recorded automatically when using Start/Done buttons
2. Manual adjustment possible:
   - Open completed work order
   - Edit "Duration" field
   - Save

This affects:
- Cost calculation
- Efficiency metrics
- Planning for future MOs


### STEP 24: HANDLE PRODUCTION ISSUES
--------------------------------------------------------------------------------
COMPONENT SHORTAGE DURING PRODUCTION:
1. Click "Replenish" on component line
2. Creates purchase order or transfer
3. Wait for arrival
4. Resume production

EQUIPMENT BREAKDOWN:
1. Create maintenance request
2. Pause work order
3. Reschedule to alternative work center (if available)
4. Resume when fixed

PRODUCE LESS THAN PLANNED:
1. Produce available quantity
2. Click "Create Backorder" button
3. System creates new MO for remaining quantity

SCRAP MATERIALS:
1. From MO, click "Scrap" button
2. Select component or product
3. Enter quantity
4. Select scrap reason
5. Confirm
6. Inventory adjusted


================================================================================
## PHASE 6: PRODUCTION COMPLETION
================================================================================

### STEP 25: VERIFY PRODUCTION QUANTITY
--------------------------------------------------------------------------------
Before marking MO complete:

1. Open Manufacturing Order
2. Check "Quantity Producing" field
3. Adjust if actual differs from planned:
   - Increase if produced more
   - Decrease if produced less
   
4. Components automatically calculated based on quantity


### STEP 26: COMPLETE MANUFACTURING ORDER
--------------------------------------------------------------------------------
After all work orders are done:

1. Open Manufacturing Order
2. Verify:
   - All work orders status = "Done"
   - All components consumed
   - Quantity to produce is correct
   
3. Click "Produce" button
4. Review final production popup:
   - Quantity
   - Finished product
   - Serial/lot number (if tracked)
   
5. Click "Validate"

Status Changes: In Progress → Done

Result: Finished products added to inventory.


### STEP 27: VERIFY FINISHED GOODS IN STOCK
--------------------------------------------------------------------------------
Navigation: Inventory → Products → Products

1. Find your finished product
2. Check "Quantity On Hand"
3. Should increase by manufactured quantity

OR

Navigation: Inventory → Reporting → Stock Moves

Filter by product to see production movement.


### STEP 28: REVIEW PRODUCTION COSTS
--------------------------------------------------------------------------------
From completed Manufacturing Order:

1. Click "Cost Analysis" button or tab
2. Review breakdown:
   
   MATERIAL COSTS:
   - Each component with quantity and cost
   - Total material cost
   
   LABOR COSTS:
   - Each work order with actual time
   - Work center hourly rate
   - Total labor cost
   
   OVERHEAD:
   - Work center overhead costs
   - Total overhead
   
   TOTAL COST:
   - Sum of materials + labor + overhead
   - Cost per unit
   
3. Compare to expected cost
4. Analyze variances


================================================================================
## PHASE 7: ORDER FULFILLMENT & DELIVERY
================================================================================

### STEP 29: CREATE SALES ORDER (If Not MTO)
--------------------------------------------------------------------------------
Navigation: Sales → Orders → Quotations

1. Click "Create"
2. Fill in:
   - Customer
   - Add product (manufactured product)
   - Quantity
   - Price
   
3. Click "Confirm Sale"

Result: Sales order confirmed, delivery order created.


### STEP 30: PROCESS DELIVERY ORDER
--------------------------------------------------------------------------------
From Sales Order:
1. Click "Delivery" smart button

OR
Navigation: Inventory → Operations → Transfers

From Delivery Order:
1. Verify customer information
2. Check products and quantities
3. (Optional) Pick products:
   - Scan barcodes
   - Confirm picked quantities
   
4. Click "Validate"

Result: Products leave inventory, delivered to customer.


### STEP 31: INVOICE CUSTOMER (If Applicable)
--------------------------------------------------------------------------------
From Sales Order:

1. Click "Create Invoice" button
2. Review invoice:
   - Products
   - Quantities
   - Prices
   - Taxes
   - Total
   
3. Click "Confirm"
4. Click "Send & Print" to email customer
5. Record payment when received


================================================================================
## PHASE 8: RETURNS & AFTER-SALES
================================================================================

### STEP 32: HANDLE CUSTOMER RETURN (If Needed)
--------------------------------------------------------------------------------
Navigation: Sales → Orders → Sales Order

1. Open original sales order
2. Click "Return" button
3. Select products being returned
4. Specify quantity
5. Click "Return"

Result: Return receipt created.

Process Return:
1. Click return receipt
2. Receive products back into inventory
3. Click "Validate"


### STEP 33: CREATE REPAIR ORDER (If Product Defective)
--------------------------------------------------------------------------------
Prerequisites: Have Repair module installed

Navigation: Repairs → Repair Orders

1. Click "Create"
2. Fill in:
   - Customer
   - Product to repair
   - Problem description
   
3. Add parts needed:
   - Click "Add a line" in Parts
   - Select replacement components
   
4. Add operations:
   - Describe repair work
   - Estimated time
   - Cost
   
5. Click "Confirm Repair"
6. Perform repair
7. Click "Repair Done"
8. Create invoice if chargeable


### STEP 34: UNBUILD DEFECTIVE PRODUCT (If Needed)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Operations → Unbuild Orders

1. Click "Create"
2. Select:
   - Product: Finished good to disassemble
   - Quantity: How many
   - Source Location: Where it currently is
   
3. Click "Unbuild"
4. System reverses manufacturing:
   - Removes finished product from inventory
   - Returns components to inventory
   - Records unbuild cost


================================================================================
## PHASE 9: ANALYSIS & OPTIMIZATION
================================================================================

### STEP 35: REVIEW PRODUCTION ANALYSIS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Reporting → Production Analysis

View and analyze:
- Total production by product
- Production trends over time
- Success rate
- Production by work center
- Efficiency rates

Filter by:
- Date range
- Product
- Work center
- Status


### STEP 36: ANALYZE MANUFACTURING COSTS
--------------------------------------------------------------------------------
Navigation: Manufacturing → Reporting → Cost Analysis

Review:
- Material costs by product
- Labor costs by work center
- Overhead allocation
- Cost variances (actual vs standard)
- Most expensive products
- Cost trends

Use for:
- Identifying cost reduction opportunities
- Pricing decisions
- Process improvement


### STEP 37: TRACK MANUFACTURING EFFICIENCY
--------------------------------------------------------------------------------
Navigation: Manufacturing → Reporting → Manufacturing Efficiency

Metrics Available:
- On-time production rate
- Work center utilization
- Actual vs planned time
- Operator efficiency
- Bottleneck identification

Actions:
- Identify slow work centers
- Training needs
- Process improvements
- Capacity adjustments


### STEP 38: REVIEW OVERALL EQUIPMENT EFFECTIVENESS (OEE)
--------------------------------------------------------------------------------
Navigation: Manufacturing → Reporting → OEE

Three Components:
1. Availability: Uptime / Planned production time
2. Performance: Actual rate / Ideal rate
3. Quality: Good units / Total units

Overall OEE = Availability × Performance × Quality

Target: World-class OEE is 85%+

Use to:
- Track equipment performance
- Schedule maintenance
- Justify new equipment
- Continuous improvement


### STEP 39: ANALYZE COMPONENT ALLOCATION
--------------------------------------------------------------------------------
Navigation: Manufacturing → Reporting → Allocation

View:
- Component availability now and future
- Reserved quantities by MO
- Shortages forecast
- Incoming supply

Use to:
- Prevent production delays
- Optimize inventory levels
- Plan purchases
- Reschedule MOs if needed


### STEP 40: REVIEW MAINTENANCE HISTORY
--------------------------------------------------------------------------------
Navigation: Maintenance → Reporting → Maintenance Analysis

Track:
- Maintenance frequency by equipment
- Cost of maintenance
- Downtime caused by issues
- Preventative vs corrective ratio

Goal: Higher preventative, lower corrective maintenance.


================================================================================
## PHASE 10: CONTINUOUS IMPROVEMENT
================================================================================

### STEP 41: UPDATE BILLS OF MATERIALS
--------------------------------------------------------------------------------
As you learn from production:

1. Adjust component quantities if waste occurs
2. Update operation times based on actuals
3. Add missing steps discovered during production
4. Remove unnecessary steps

Using PLM (Product Lifecycle Management):
1. Create Engineering Change Order (ECO)
2. Propose BoM changes
3. Review and approve
4. System maintains version history
5. New MOs use updated BoM


### STEP 42: OPTIMIZE WORK CENTER CONFIGURATION
--------------------------------------------------------------------------------
Based on actual data:

1. Adjust work center capacity
2. Update time efficiency percentages
3. Reconfigure working schedules
4. Set up more alternative work centers
5. Rebalance workload


### STEP 43: IMPLEMENT QUALITY CONTROL POINTS
--------------------------------------------------------------------------------
Navigation: Quality → Configuration → Control Points

Add checks at critical points:
1. Incoming material inspection
2. In-process checkpoints
3. Final product inspection
4. Pre-ship verification

Define:
- When check occurs (trigger)
- What to check (criteria)
- Pass/fail thresholds
- Actions on failure


### STEP 44: SET UP PREVENTATIVE MAINTENANCE
--------------------------------------------------------------------------------
Navigation: Maintenance → Maintenance → Maintenance

For each equipment/work center:

1. Create maintenance plan
2. Set frequency:
   - Time-based (every X days)
   - Usage-based (every X hours)
   
3. Create checklist:
   - Items to inspect
   - Tasks to perform
   
4. Assign maintenance team
5. System auto-generates requests


### STEP 45: IMPLEMENT ADVANCED PLANNING
--------------------------------------------------------------------------------
Navigation: Manufacturing → Planning → Master Production Schedule

For demand-driven planning:

1. Add products to MPS
2. Enter forecasted demand periods
3. Set safety stock levels
4. System calculates:
   - When to produce
   - How much to produce
   - Component requirements
   
5. Launch MOs directly from MPS


### STEP 46: OPTIMIZE INVENTORY LEVELS
--------------------------------------------------------------------------------
Based on production consumption:

Navigation: Inventory → Configuration → Reordering Rules

For each component:
1. Set Min/Max quantities
2. Set reorder point
3. Configure lead times
4. System auto-creates:
   - Purchase orders for bought items
   - Manufacturing orders for produced items


### STEP 47: IMPLEMENT BARCODE OPERATIONS
--------------------------------------------------------------------------------
For increased speed and accuracy:

1. Print barcodes for all products
2. Print MO barcodes
3. Train operators on barcode app
4. Use Barcode app for:
   - Starting MOs
   - Consuming components
   - Completing work orders
   - Moving inventory
   - Quality checks


### STEP 48: CONFIGURE SUBCONTRACTING (If Needed)
--------------------------------------------------------------------------------
For operations done externally:

1. Create subcontracting BoM:
   - BoM Type: "Subcontracting"
   - Components to send
   
2. Configure vendor as subcontractor
3. Create purchase order to subcontractor
4. System handles:
   - Sending components
   - Receiving finished goods
   - Cost tracking


### STEP 49: TRAIN TEAM ON SHOP FLOOR INTERFACE
--------------------------------------------------------------------------------
Navigation: Manufacturing → Shop Floor

Purpose-built for production operators:
- Large buttons for touch screens
- Tablet-friendly
- Real-time updates
- Simple workflow

Train operators to:
- Select their work center
- Start work orders
- Track time
- Complete operations
- Report issues


### STEP 50: ESTABLISH KPIS AND REGULAR REVIEW
--------------------------------------------------------------------------------
Key Performance Indicators to track:

PRODUCTION:
- Manufacturing orders on time %
- Production volume (units/month)
- Work center utilization %

QUALITY:
- First pass yield rate
- Scrap rate %
- Quality check pass rate

EFFICIENCY:
- Overall Equipment Effectiveness (OEE)
- Actual vs planned time ratio
- Labor efficiency

COST:
- Cost per unit
- Material cost %
- Labor cost %
- Cost variance

Schedule monthly reviews to assess and improve.


================================================================================
## SPECIAL SCENARIOS
================================================================================

### SCENARIO A: MAKE-TO-STOCK PRODUCTION
--------------------------------------------------------------------------------
Maintain finished goods inventory:

1. Set reordering rules on finished product
2. System monitors stock level
3. When below minimum: Auto-creates MO
4. Produce to maximum level
5. Inventory ready for immediate sale


### SCENARIO B: ENGINEER-TO-ORDER
--------------------------------------------------------------------------------
Custom products per customer order:

1. Receive customer requirements
2. Create custom BoM for this order
3. Link BoM to specific sales order
4. Produce one-off product
5. BoM can be reused or archived


### SCENARIO C: MULTI-LEVEL MANUFACTURING (SUB-ASSEMBLIES)
--------------------------------------------------------------------------------
Complex products with components that need manufacturing:

1. Create BoM for sub-assembly:
   - Product: Sub-assembly
   - Components: Raw materials
   
2. Create BoM for final product:
   - Product: Final product
   - Components: Include sub-assembly
   
3. Create MO for final product
4. System auto-generates MO for sub-assembly
5. Produce sub-assembly first
6. Then produce final product


### SCENARIO D: PRODUCTION WITH VARIANTS
--------------------------------------------------------------------------------
Same product in different configurations:

1. Set up product variants:
   - Product Template
   - Attributes (Size, Color, etc.)
   - Values for each attribute
   
2. Create single BoM:
   - Apply to: Product Template
   - Add operations
   
3. Configure variant-specific components:
   - "Apply on Variants" field
   - Component only used for specific variant
   
4. Create MO: Select specific variant
5. System uses correct components


### SCENARIO E: BATCH PRODUCTION
--------------------------------------------------------------------------------
Producing multiple products together:

1. Create separate MOs for each product
2. Group by work center and time
3. Process in batch on shop floor
4. Complete all in one session
5. Efficient use of setup time


### SCENARIO F: PARTIAL PRODUCTION WITH BACKORDERS
--------------------------------------------------------------------------------
Component shortage prevents full production:

1. Start MO as normal
2. Produce available quantity
3. Click "Create Backorder"
4. System creates new MO for remainder
5. Complete backorder when components arrive


### SCENARIO G: RUSH ORDERS
--------------------------------------------------------------------------------
Expedited customer requests:

1. Create MO with immediate scheduled date
2. Set priority to "High"
3. Manually reserve components (override other MOs if needed)
4. Notify shop floor
5. Process before other MOs
6. Use alternative work center if primary busy


### SCENARIO H: PRODUCT RECALL
--------------------------------------------------------------------------------
Track and manage product recalls:

1. Use lot/serial numbers for traceability
2. Identify affected lot/serial
3. Navigation: Inventory → Products → Product
4. Click lot/serial number
5. "Traceability" button shows:
   - Where used
   - MOs produced
   - Sales orders shipped
   - Current locations
   
6. Contact affected customers
7. Process returns
8. Unbuild or scrap affected products


================================================================================
## TROUBLESHOOTING COMMON ISSUES
================================================================================

ISSUE: Components Not Reserving
SOLUTION:
- Check inventory on hand
- Verify product type is "Storable"
- Check locations in multi-warehouse setup
- Look for other MOs reserving same stock

ISSUE: Work Order Not Appearing
SOLUTION:
- Verify BoM has operations defined
- Check work centers are active
- Confirm MO is in "Confirmed" status
- Refresh page

ISSUE: Cannot Complete MO
SOLUTION:
- All work orders must be "Done"
- All components must be consumed
- Check for quality hold
- Verify user permissions

ISSUE: Cost Calculation Wrong
SOLUTION:
- Verify costing method (FIFO/AVCO/Standard)
- Check work center hourly rates
- Confirm actual time recorded on work orders
- Review component costs
- Run cost calculation update

ISSUE: Barcode Not Working
SOLUTION:
- Verify barcode app installed
- Check product has barcode assigned
- Ensure barcode format compatible
- Test with barcode scanner first

ISSUE: Cannot Start Production
SOLUTION:
- Click "Check Availability"
- Verify components in stock
- Check MO status (must be Confirmed)
- Verify work center available
- Check user permissions

ISSUE: MO Stuck in Draft
SOLUTION:
- Verify BoM exists and is valid
- Check all required fields filled
- Click "Confirm" button
- Check for error messages

ISSUE: Delivery Late
SOLUTION:
- Check manufacturing lead time settings
- Review work center capacity
- Identify bottlenecks
- Consider alternative work centers
- Add capacity or resources


================================================================================
## BEST PRACTICES
================================================================================

1. **Start Simple**: Begin with basic 1-step manufacturing before adding 
   complexity like operations, work centers, and quality checks.

2. **Accurate BoMs**: Take time to create accurate BoMs with correct quantities.
   This is the foundation of manufacturing in Odoo.

3. **Track Time**: Use work order time tracking from day one. This data is
   invaluable for planning and costing.

4. **Regular Inventory**: Perform regular inventory counts to ensure system
   matches reality, especially for components.

5. **Use Barcodes**: Implement barcode scanning as soon as possible for speed
   and accuracy improvements.

6. **Preventative Maintenance**: Schedule regular maintenance to minimize
   unplanned downtime.

7. **Quality Early**: Implement quality checks at critical points, not just
   at the end.

8. **Train Everyone**: Ensure all users are trained on their specific roles
   and functions.

9. **Review Reports**: Regularly review production analysis, costs, and
   efficiency metrics.

10. **Continuous Improvement**: Use actual data to continuously refine BoMs,
    work center parameters, and processes.

11. **Document Procedures**: Create standard operating procedures for
    operators, especially for complex products.

12. **Test Changes**: Before rolling out changes, test on a single product
    or work order first.

13. **Backup Data**: Regular backups are critical, especially before major
    configuration changes.

14. **Version Control**: Use PLM and ECOs to manage BoM changes systematically.

15. **Customer Communication**: Keep customers informed of production status,
    especially for MTO and ETO orders.


================================================================================
## INTEGRATION WITH OTHER MODULES
================================================================================

SALES:
- Sales orders trigger MTO manufacturing
- Delivery dates coordinate with production schedule
- Customer portal shows production status

PURCHASE:
- Component shortages auto-generate RFQs
- Vendor lead times factor into MO scheduling
- Subcontracting purchase orders

INVENTORY:
- Real-time inventory consumption and production
- Multi-warehouse manufacturing
- Barcode operations
- Lot and serial number traceability

QUALITY:
- Quality control points in production workflow
- Quality alerts block MOs if needed
- Quality check data for analysis

MAINTENANCE:
- Equipment tracking tied to work centers
- Downtime affects scheduling
- Cost allocation for maintenance

ACCOUNTING:
- Automatic inventory valuation
- Cost of goods sold calculation
- Work in progress tracking
- Manufacturing cost to P&L

PROJECT:
- Project-based manufacturing
- Time tracking integration
- Resource planning

PLM:
- Engineering change orders
- BoM version control
- Document management


================================================================================
## GLOSSARY OF TERMS
================================================================================

BoM: Bill of Materials - Recipe defining how to manufacture a product

MO: Manufacturing Order - Instruction to produce specific quantity of a product

WO: Work Order - Specific operation/step within a manufacturing order

Work Center: Location/machine where operations are performed

Operation: Individual step in the manufacturing process (cutting, assembly, etc.)

Routing: Sequence of operations to manufacture a product

MTO: Make to Order - Produce only when customer orders

MTS: Make to Stock - Produce to maintain inventory

ETO: Engineer to Order - Custom design for each order

Lead Time: Time required to manufacture a product

Component: Raw material or sub-assembly used in manufacturing

By-Product: Secondary product created during manufacturing

Scrap: Wasted or defective material removed from production

Unbuild: Reverse manufacturing to recover components

Backorder: Remaining quantity when partial production completed

Lot: Batch of products produced together

Serial Number: Unique identifier for individual product

QCP: Quality Control Point - Inspection checkpoint in production

OEE: Overall Equipment Effectiveness - Key performance metric

PLM: Product Lifecycle Management - Managing product design changes

ECO: Engineering Change Order - Formal BoM modification process

Subcontracting: Outsourcing production operations to external vendors

Replenishment: Process of restocking inventory (purchase or manufacture)

Reservation: Allocation of inventory to specific manufacturing order


================================================================================
## CONCLUSION
================================================================================

This complete workflow covers the entire manufacturing process in Odoo from
initial setup through production, delivery, and continuous improvement.

Key Success Factors:
1. Proper configuration and setup
2. Accurate Bills of Materials
3. Consistent data entry and tracking
4. Regular analysis and optimization
5. Team training and adoption

By following this guide systematically, you can implement a complete
manufacturing operation in Odoo that provides:
- Complete traceability
- Real-time cost visibility
- Efficient production workflows
- Quality control
- Data-driven decision making

Remember: Start simple, prove the value, then add complexity as needed.

For specific features or advanced scenarios, refer to the individual video
transcripts for detailed step-by-step instructions.


================================================================================
END OF MANUFACTURING WORKFLOW GUIDE
================================================================================
