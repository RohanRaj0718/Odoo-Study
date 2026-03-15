# Manufacturing App - Integrated Workflows Guide
**Complete Step-by-Step Guide with Quality, Maintenance, Repair, and Project Apps**

---

## Table of Contents
1. [Engineering-to-Order (ETO) Workflow with Project Integration](#eto-workflow)
2. [Quality Control Integration with Manufacturing](#quality-integration)
3. [Maintenance Integration with Manufacturing](#maintenance-integration)
4. [Repair Integration with Manufacturing](#repair-integration)

---

## <a id="eto-workflow"></a>1. ENGINEERING-TO-ORDER (ETO) WORKFLOW WITH PROJECT INTEGRATION

### What is ETO?
**Engineering-to-Order (ETO)** is a workflow where you design and manufacture custom products that you don't normally sell. The customer wants a product made to their exact specifications. You work with them to create a unique product through design, engineering, and manufacturing.

### When to Use ETO?
- Customer wants a custom product not in your catalog
- Product needs to be designed from scratch
- Manufacturing only happens after customer orders and design is approved
- You need to track design hours and engineering time

---

### COMPLETE ETO WORKFLOW - STEP BY STEP

#### **PHASE 1: Initial Configuration**

##### **Step 1.1: Enable MTO (Make-to-Order) Route**

**What:** MTO route automatically creates manufacturing/purchase orders only after a sales order is confirmed.

**Where to Click:**
1. Open **Odoo Dashboard**
2. Click on **Inventory** app (9-square grid icon)
3. Go to **Configuration** → **Settings**
4. Scroll down to **Warehouse** section
5. Check the box: ☑ **Multi-Step Routes**
6. Click **Save** (top left corner)
7. Now go to **Configuration** → **Routes** (this option appears after enabling multi-step routes)
8. Click **Filters** button (top right)
9. Select **Archived**
10. Find "**Replenish on Order (MTO)**" in the list
11. Check the box next to it
12. Click **Actions** button (top center)
13. Select **Unarchive**
14. Remove the filter to see all active routes

**Result:** MTO route is now active and can be used for products.

---

##### **Step 1.2: Create Engineering-to-Order Project**

**What:** A project to track all ETO orders through design stages.

**Where to Click:**
1. Click **Apps** menu (9-square grid)
2. Open **Project** app
3. Click **New** button (top left)
4. Enter Project Name: **"Engineering to Order"**
5. Click **Create**
6. You'll see the project with a **Kanban view**
7. Create stages by clicking **+ Stage** at the top right:
   - Stage 1: Type **"Waiting"** → Press Enter
   - Stage 2: Type **"Design"** → Press Enter
   - Stage 3: Type **"Review"** → Press Enter
   - Stage 4: Type **"Finished"** → Press Enter

**Result:** Project created with 4 stages to track ETO workflow.

---

##### **Step 1.3: Create ETO Service Product**

**What:** This product represents the design/engineering hours you'll charge the customer.

**Where to Click:**
1. Go to **Sales** app
2. Click **Products** → **Products**
3. Click **New** button
4. Fill in the form:
   - **Product Name:** "ETO Service" or "Engineering Design Service"
   - **Product Type:** Select **Service** (dropdown)
   - **Unit of Measure:** Select **Hours**
   - **Sales Price:** Enter **100.00** (or your hourly rate)
5. Scroll down to **Sales** tab
6. Find **Service Invoicing** section
7. In **Create on Order** field: Select **Task**
8. In **Project** field: Select **Engineering to Order** (the project you created)
9. Click **Save**

**Result:** ETO Service product created that will auto-create project tasks.

---

##### **Step 1.4: Create Generic ETO Product (Physical Product)**

**What:** A placeholder product that will be customized later.

**Where to Click:**
1. Still in **Sales** → **Products** → **Products**
2. Click **New** button
3. Fill in the form:
   - **Product Name:** "ETO Product - Custom"
   - **Product Type:** Select **Storable Product**
   - **Sales Price:** Enter **1.00** (placeholder - will update after design)
4. Click on **Inventory** tab
5. In **Routes** section, check both boxes:
   - ☑ **Replenish on Order (MTO)**
   - ☑ **Manufacture**
6. Click **Save**
7. Now click **Bill of Materials** smart button at the top (shows "0")
8. Click **New** to create a template BoM
9. Fill in:
   - **Product:** Should auto-fill with "ETO Product - Custom"
   - **Reference:** Type **"TEMPLATE"**
   - Leave **Components** tab EMPTY
   - Leave **Operations** tab EMPTY
10. Click **Save**

**Result:** Generic product with blank template BoM ready to customize per order.

---

#### **PHASE 2: Process Customer Order**

##### **Step 2.1: Create Sales Order**

**Where to Click:**
1. Go to **Sales** app
2. Click **Orders** → **Quotations**
3. Click **New** button
4. Fill in the quotation:
   - **Customer:** Select your customer (e.g., "Corner Furniture Co.")
   - Click **Add a product** in the order lines
5. Add first product line:
   - **Product:** Select **"ETO Service"**
   - **Quantity:** Enter **10** (estimated design hours)
   - Unit Price should show **100.00**
6. Add second product line:
   - Click **Add a product** again
   - **Product:** Select **"ETO Product - Custom"**
   - **Description:** Type **"Custom Dining Table"** (or customer's specific request)
   - **Quantity:** Enter **1**
   - **Unit Price:** Leave at **1.00** (will update after design)
7. Click **Confirm** button (top left)

**Result:** Sales order confirmed. Smart buttons appear showing Project, Task, and Manufacturing Order links.

---

##### **Step 2.2: Verify Auto-Created Records**

**Where to Click:**
1. On the same Sales Order form, look at smart buttons at top:
   - **Tasks** button should show **"1"**
   - **Manufacturing** button should show **"1"**
2. Click **Tasks** smart button
3. You'll see a task like "SO019 - Design Service" or similar
4. Note the task is in **"Engineering to Order"** project
5. Click back arrow or breadcrumb to return to Sales Order
6. Click **Manufacturing** smart button
7. You'll see a Manufacturing Order (MO) in **Draft** state
8. Note the BoM is the **TEMPLATE** (we'll configure this later)
9. Return to Sales Order using breadcrumbs

**Result:** Verified that project task and MO were automatically created.

---

#### **PHASE 3: Design and Engineering Process**

##### **Step 3.1: Start Design Work**

**Where to Click:**
1. Go to **Project** app
2. Click on **"Engineering to Order"** project
3. You'll see the task in **"Waiting"** stage (Kanban card)
4. Click on the **task card** to open it
5. In the task form:
   - **Assignees:** Add your design team members
     - Click the **Assignees** field
     - Type and select **"Donald Johnson"** (Designer)
     - Type and select **"Robert Smith"** (Engineer)
6. Drag the task card to the **"Design"** stage (or use the dropdown at top)
7. Click **Save**

**Result:** Task assigned to design team and moved to Design stage.

---

##### **Step 3.2: Log Design Hours**

**What:** Designer works with customer and logs time.

**Where to Click:**
1. Still in the task form
2. Click on **Timesheets** tab (at bottom)
3. Click **Add a line**
4. Fill in the timesheet entry:
   - **Employee:** Select **"Donald Johnson"**
   - **Description:** Type **"Designing custom dining table"**
   - **Hours Spent:** Enter **12.00**
   - **Date:** Today's date (auto-filled)
5. Click outside the row to save it
6. Move task to **"Review"** stage
   - Drag the card or use stage dropdown

**Result:** 12 design hours logged to the project task.

---

##### **Step 3.3: Log Engineering Review Hours**

**What:** Engineer reviews the design and determines specifications and cost.

**Where to Click:**
1. Still in the task
2. In **Timesheets** tab, click **Add a line** again
3. Fill in:
   - **Employee:** Select **"Robert Smith"**
   - **Description:** Type **"Reviewing design and calculating cost"**
   - **Hours Spent:** Enter **4.00**
4. Click outside to save
5. **Check the "Remaining Hours on SO" field** at the top of timesheets
   - It shows **-6.00** (because you used 16 hours but allocated only 10)
   - This tells you to bill customer for 6 extra hours
6. Move task to **"Finished"** stage
7. Click **Save**

**Result:** Engineering review complete. Total: 16 hours logged (10 estimated + 6 additional).

---

##### **Step 3.4: Update Sales Order Pricing**

**What:** Update the sales order with actual hours and final product price.

**Where to Click:**
1. From the task, click **Sales Order** smart button (or navigate via breadcrumbs)
2. In the Sales Order, look at the order lines:
   - **ETO Service** line:
     - **Delivered** column shows **16.00** (auto-updated from timesheets)
     - Change **Quantity** to **16.00** (to match delivered)
     - Total price updates to **$1,600.00**
   - **ETO Product - Custom** line:
     - Change **Unit Price** from **1.00** to **1000.00** (engineer determined cost)
     - Total now shows **$1,000.00**
3. **Total Sales Order:** $1,600 (service) + $1,000 (product) = **$2,600**
4. Click **Save**

**Result:** Sales order updated with actual costs and pricing.

---

#### **PHASE 4: Configure BoM and Manufacturing**

##### **Step 4.1: Access Manufacturing Order**

**Where to Click:**
1. From Sales Order, click **Manufacturing** smart button
2. You'll see the Manufacturing Order (MO) in **Draft** state
3. Note the **Bill of Materials** field shows **"TEMPLATE"**
4. Click the **internal link icon** (↗) next to the BoM field

**Result:** Opens the template BoM form.

---

##### **Step 4.2: Duplicate Template BoM**

**What:** Create a copy to configure without destroying the template.

**Where to Click:**
1. In the BoM form, click **Action** button (top center)
2. Select **Duplicate**
3. A new BoM form opens with "(copy)" in the reference
4. Update the **Reference** field:
   - Delete "TEMPLATE (copy)"
   - Enter your **Sales Order number** (e.g., "SO019")
5. Click **Save**

**Result:** New BoM created for this specific custom order.

---

##### **Step 4.3: Add Components to BoM**

**What:** Add the materials needed to manufacture the custom product.

**Where to Click:**
1. Still in the BoM form, go to **Components** tab
2. Click **Add a line**
3. Add first component:
   - **Product:** Type and select **"Table Top"** (or create if doesn't exist)
   - **Quantity:** Enter **1**
4. Click **Add a line** again for next component:
   - **Product:** Select **"Table Leg"**
   - **Quantity:** Enter **6**
5. Click **Add a line** for third component:
   - **Product:** Select **"Screws"**
   - **Quantity:** Enter **12**
6. Click **Save**

**Result:** Components added to the custom BoM.

---

##### **Step 4.4: Add Operations to BoM**

**What:** Define the manufacturing steps/work centers.

**Where to Click:**
1. Still in BoM form, click **Operations** tab
2. Click **Add a line**
3. Add first operation:
   - **Operation:** Type **"Cut"**
   - **Work Center:** Select **"Saw Station"** (or create new)
   - **Default Duration:** Enter **30** (minutes)
4. Click **Add a line** for second operation:
   - **Operation:** Type **"Assemble"**
   - **Work Center:** Select **"Assembly Station"**
   - **Default Duration:** Enter **60**
5. Click **Save**
6. Use **breadcrumbs** to go back to the **Manufacturing Order**

**Result:** Operations defined for the manufacturing process.

---

##### **Step 4.5: Update MO with Configured BoM**

**Where to Click:**
1. Back in the Manufacturing Order form
2. In **Bill of Materials** field, click the dropdown
3. Select the BoM with your Sales Order reference (e.g., "SO019")
4. Notice:
   - **Components** tab now shows Table Top, Table Legs, Screws
   - **Work Orders** tab now shows Cut and Assemble operations
5. Click **Confirm** button (top left)
6. MO status changes to **Confirmed**

**Result:** Manufacturing Order configured and ready to produce.

---

#### **PHASE 5: Manufacturing Execution**

##### **Step 5.1: Process Work Orders**

**Where to Click:**
1. In the Manufacturing Order, click **Work Orders** tab
2. You'll see two work orders: **Cut** and **Assemble**
3. For each work order:
   - Click **Start** button (changes to green timer)
   - Wait a moment (simulating work)
   - Click **Done** button
4. Repeat for all work orders
5. Once all work orders are **Done**, go back to the main MO form

**Alternative - Tablet View:**
1. Go to **Manufacturing** app dashboard
2. Click **Shop Floor** button
3. Select **Work Center** (e.g., Saw Station)
4. Click on the work order card
5. Click **Start** → **Done**
6. Move to next work center and repeat

**Result:** All work completed.

---

##### **Step 5.2: Mark Manufacturing Complete**

**Where to Click:**
1. Return to Manufacturing Order form
2. All work orders should show **Done** status
3. Click **Produce All** button (top left)
4. Confirm the production quantity
5. Click **Validate** or **Mark as Done**
6. MO status changes to **Done**

**Result:** Product manufactured successfully.

---

#### **PHASE 6: Invoicing and Delivery**

##### **Step 6.1: Create Invoice**

**Where to Click:**
1. Go back to **Sales Order** (via breadcrumbs or Sales app → Orders → Orders)
2. Click **Create Invoice** button (top right)
3. A popup appears:
   - Select **Regular Invoice** (radio button)
   - Click **Create and View Invoice**
4. Invoice form opens showing:
   - ETO Service: 16 Hours × $100 = $1,600
   - Custom Dining Table: 1 × $1,000 = $1,000
   - **Total:** $2,600
5. Review the invoice
6. Click **Confirm** button

**Result:** Invoice created and confirmed.

---

##### **Step 6.2: Register Payment**

**Where to Click:**
1. Still in the invoice form
2. Click **Register Payment** button (top center)
3. A payment popup appears:
   - **Journal:** Select **Bank** or **Cash**
   - **Payment Method:** Select appropriate method
   - **Amount:** Should show $2,600.00
   - **Memo:** Auto-filled with invoice number
4. Click **Create Payment**
5. Invoice status changes to **Paid** with green banner

**Result:** Payment recorded.

---

##### **Step 6.3: Process Delivery**

**Where to Click:**
1. Return to **Sales Order**
2. Click **Delivery** smart button (shows "1 delivery")
3. Delivery Order form opens
4. Verify the product line shows:
   - Custom Dining Table × 1
   - **Demand** and **Quantity** columns
5. Click **Validate** button
6. A popup may appear asking to process reserved quantities
7. Click **Apply** or **Validate**
8. Delivery status changes to **Done**

**Result:** Product shipped to customer. ETO workflow complete!

---

### ETO WORKFLOW SUMMARY

**Complete Process Flow:**
1. ✅ Configure MTO route, Project, ETO Service, ETO Product with Template BoM
2. ✅ Create Sales Order with ETO Service (hours) + ETO Product (custom item)
3. ✅ Auto-creates Project Task and Draft Manufacturing Order
4. ✅ Designer works and logs hours in Project app
5. ✅ Engineer reviews, logs hours, determines final cost
6. ✅ Update Sales Order with actual hours and product price
7. ✅ Duplicate Template BoM and configure with actual components & operations
8. ✅ Update MO to use configured BoM
9. ✅ Execute Work Orders and complete manufacturing
10. ✅ Invoice customer for services and product
11. ✅ Register payment
12. ✅ Deliver finished product

---

## <a id="quality-integration"></a>2. QUALITY CONTROL INTEGRATION WITH MANUFACTURING

### What is Quality Control in Manufacturing?
Quality Control ensures products meet specifications before, during, and after manufacturing. Quality checks can be automatic at specific points in the production process.

### Key Concepts:
- **Quality Control Points (QCP):** Automated triggers that create quality checks
- **Quality Checks:** Actual inspections performed by quality team
- **Quality Alerts:** Issues raised when quality problems are found

---

### QUALITY CONTROL WORKFLOW - STEP BY STEP

#### **PHASE 1: Setup Quality Control**

##### **Step 1.1: Install Quality App**

**Where to Click:**
1. Go to **Apps** menu (9-square grid)
2. Search for **"Quality"**
3. Click **Activate** button
4. Wait for installation

**Result:** Quality app installed and accessible.

---

##### **Step 1.2: Create Quality Team**

**Where to Click:**
1. Open **Quality** app
2. Go to **Configuration** → **Quality Teams**
3. Click **New**
4. Fill in:
   - **Team Name:** "Quality Control Team"
   - **Company:** Select your company
5. Click **Save**

**Result:** Quality team created.

---

##### **Step 1.3: Create Quality Control Point**

**What:** Set up automatic quality checks during manufacturing.

**Where to Click:**
1. In **Quality** app, go to **Quality Control** → **Control Points**
2. Click **New**
3. Fill in the form:
   - **Title:** "Final Product Inspection"
   - **Products:** Select the product to inspect (e.g., "Dining Table")
   - OR **Product Categories:** Select a category to apply to all products
   - **Operations:** Select **Manufacturing**
   - **Work Order Operation:** Select specific operation like **"Assembly"** (optional)
   - **Control Per:** Select **Operation** (one check per manufacturing order)
   - **Control Frequency:** Select **All** (check every time)
   - **Type:** Select **Pass - Fail** (or choose from):
     - **Instructions:** Step-by-step guide
     - **Take a Picture:** Require photo
     - **Pass - Fail:** Simple pass/fail check
     - **Measure:** Take measurements
     - **Register Production:** Confirm quantity
     - **Worksheet/Spreadsheet:** Fill out forms
   - **Team:** Select "Quality Control Team"
4. Go to **Instructions** tab at bottom
5. Type instructions: "Inspect final product for defects, proper assembly, and finish quality"
6. Go to **Message if Failure** tab
7. Type: "Create quality alert and notify production manager"
8. Click **Save**

**Result:** Quality control point active. Will auto-create quality checks.

---

#### **PHASE 2: Execute Quality Checks During Manufacturing**

##### **Step 2.1: Start Manufacturing Order**

**Where to Click:**
1. Go to **Manufacturing** app
2. Click **Operations** → **Manufacturing Orders**
3. Click **New** or select existing MO
4. Fill in:
   - **Product:** Select product with quality control
   - **Quantity:** Enter amount to produce
5. Click **Confirm**

**Result:** MO confirmed, quality check automatically created (if QCP configured).

---

##### **Step 2.2: View Quality Check**

**Where to Click:**
1. In the Manufacturing Order form
2. Look for **Quality Checks** smart button at top (or **Quality Check** tab)
3. Click the smart button
4. You'll see the quality check in **To Do** state
5. Click on the quality check to open it

**Result:** Quality check form opened.

---

##### **Step 2.3: Process Quality Check**

**Where to Click:**
1. In Quality Check form, you'll see:
   - **Product:** The product being checked
   - **Manufacturing Order:** Link to the MO
   - **Quality Team:** Assigned team
   - **Type:** Pass - Fail (or whatever you configured)
   - **Instructions:** The instructions you wrote
2. To pass the check:
   - Click **Pass** button (green checkmark)
3. To fail the check:
   - Click **Fail** button (red X)
   - Add notes in the **chatter** about the issue
4. If check passes, MO can continue
5. If check fails, MO may be blocked or require review

**Result:** Quality check completed.

---

##### **Step 2.4: Handle Failed Quality Check**

**Where to Click (if check fails):**
1. In the failed quality check form
2. Click **Create Alert** button (if available) or:
3. Go to **Quality** app → **Quality Control** → **Quality Alerts**
4. Click **New**
5. Fill in:
   - **Title:** "Defect found in Dining Table assembly"
   - **Product:** Select the product
   - **Manufacturing Order:** Link the MO
   - **Quality Check:** Link the failed check
   - **Description:** Describe the issue in detail
   - **Root Cause:** Analyze what went wrong
   - **Corrective Action:** Describe how to fix
   - **Preventive Action:** How to prevent in future
   - **Responsible:** Assign to production manager
6. Click **Save**
7. Update the MO to address the issue

**Result:** Quality alert created and tracked.

---

### QUALITY CONTROL EXAMPLES

#### **Example 1: Measure Type Check**
- **Use Case:** Check diameter of machined part
- **Configuration:** Type = Measure, Norm = 50mm, Tolerance = ±0.5mm
- **Execution:** Operator measures 49.8mm → enters value → check passes

#### **Example 2: Take Picture Check**
- **Use Case:** Document welding quality
- **Configuration:** Type = Take a Picture
- **Execution:** Operator takes photo → uploads → quality team reviews later

#### **Example 3: Worksheet Check**
- **Use Case:** Multi-point inspection checklist
- **Configuration:** Type = Worksheet, attach checklist template
- **Execution:** Operator fills out checklist → submits → check completes

---

## <a id="maintenance-integration"></a>3. MAINTENANCE INTEGRATION WITH MANUFACTURING

### What is Maintenance in Manufacturing?
Maintenance ensures manufacturing equipment stays functional. Two types:
- **Preventive Maintenance:** Scheduled regular maintenance to prevent breakdowns
- **Corrective Maintenance:** Repairs after equipment breaks

### Key Concepts:
- **Equipment:** Machines and tools used in manufacturing
- **Work Centers:** Locations where equipment is used
- **Maintenance Requests:** Tasks to maintain or repair equipment
- **Maintenance Teams:** People responsible for maintenance

---

### MAINTENANCE WORKFLOW - STEP BY STEP

#### **PHASE 1: Setup Maintenance System**

##### **Step 1.1: Install Maintenance App**

**Where to Click:**
1. Go to **Apps** menu
2. Search for **"Maintenance"**
3. Click **Activate**
4. Wait for installation

**Result:** Maintenance app installed.

---

##### **Step 1.2: Create Maintenance Team**

**Where to Click:**
1. Open **Maintenance** app
2. Go to **Configuration** → **Maintenance Teams**
3. Click **New**
4. Fill in:
   - **Team Name:** "Internal Maintenance Team"
   - **Team Members:** Select maintenance technicians (use + icon)
   - Click **Search More** if needed to find all users
   - **Company:** Select your company
5. Click **Save**

**Result:** Maintenance team created with assigned members.

---

##### **Step 1.3: Create Equipment Category**

**Where to Click:**
1. In **Maintenance** app, go to **Configuration** → **Equipment Categories**
2. Click **New**
3. Fill in:
   - **Category Name:** "Manufacturing Machines"
   - **Responsible:** Select manager
   - **Company:** Select your company
   - **Email Alias:** (optional) maintenance.machines@yourcompany.com
   - **Comments:** (optional) Notes about this category
4. Click **Save**

**Result:** Equipment category created.

---

##### **Step 1.4: Add Equipment (Machine)**

**Where to Click:**
1. In **Maintenance** app, go to **Equipment** → **Machines & Tools**
2. Click **New**
3. Fill in LEFT side:
   - **Name:** "CNC Milling Machine #1"
   - **Equipment Category:** Select "Manufacturing Machines"
   - **Company:** Select your company
   - **Used By:** Select **Work Center** (radio button)
   - **Work Center:** Select the work center (e.g., "Machining Station")
   - **Maintenance Team:** Select "Internal Maintenance Team"
   - **Technician:** Select specific technician
4. Fill in RIGHT side (scroll down):
   - **Location:** Enter physical location (e.g., "Building A, Bay 3")
   - **Description:** Describe the equipment
5. Click **Product Information** tab:
   - **Vendor:** Select equipment supplier
   - **Model:** Enter model number
   - **Serial Number:** Enter serial #
   - **Warranty Expiration Date:** Select date from calendar
6. Click **Maintenance** tab:
   - **Preventive Maintenance Frequency:** Enter **30** Days (or desired interval)
   - **Maintenance Duration:** Enter **2** Hours
   - **Expected MTBF:** Enter **120** Days (Mean Time Between Failure)
   - Other fields auto-calculate based on historical data
7. Click **Save**

**Result:** Equipment added to system with maintenance schedule.

---

#### **PHASE 2: Preventive Maintenance**

##### **Step 2.1: Automatic Maintenance Request Generation**

**What:** Odoo automatically generates maintenance requests based on the frequency you set.

**Where it happens:**
1. Odoo runs a scheduled action **once per day**
2. Checks all equipment with preventive maintenance frequency
3. Creates maintenance requests automatically
4. You'll see them in **Maintenance** app → **Maintenance** → **Maintenance Requests**

**To view:**
1. Go to **Maintenance** app
2. Click **Maintenance** → **Maintenance Requests**
3. You'll see auto-generated requests like "Preventive Maintenance - CNC Milling Machine #1"
4. Status will be **New** or **In Progress**

**Result:** System auto-creates preventive maintenance tasks.

---

##### **Step 2.2: Process Maintenance Request**

**Where to Click:**
1. In **Maintenance** app, go to **Maintenance** → **Maintenance Requests**
2. Click on a maintenance request
3. Review the form:
   - **Maintenance Request:** Title/name
   - **Created By:** Who created it (system or user)
   - **For:** Equipment or Work Center
   - **Equipment/Work Center:** Shows which machine
4. **Assign the request:**
   - **Maintenance Team:** Should be pre-filled
   - **Technician:** Select who will do the work
5. **Schedule it:**
   - **Request Date:** When requested
   - **Scheduled Date:** When to perform (click calendar icon)
6. **Track work:**
   - Click **In Progress** button when technician starts
7. **Log time:**
   - Add a **Timesheet** entry (if timesheet tracking enabled)
   - Or add notes in **Description** field
8. **Complete:**
   - Click **Done** button when maintenance finished
9. Click **Save**

**Result:** Maintenance completed and tracked.

---

#### **PHASE 3: Corrective Maintenance (Equipment Breakdown)**

##### **Step 3.1: Create Maintenance Request from Manufacturing**

**Scenario:** Machine breaks during production.

**Method A: From Manufacturing Order**

**Where to Click:**
1. Go to **Manufacturing** app
2. Click **Operations** → **Manufacturing Orders**
3. Open the MO with equipment issue
4. Click **Maintenance Request** smart button at top (or button on form)
5. A new maintenance request form appears
6. Fill in:
   - **Name:** "Saw Station - No Power"
   - **Created By:** Auto-filled with your name
   - **For:** Select **Work Center** (radio button)
   - **Work Center:** Select "Saw Station"
   - **Request Date:** Today (auto-filled)
   - **Maintenance Team:** Select team
   - **Priority:** Select stars (★★★ = High)
7. In **Description** field, type: "Power stopped working at Saw Station during MO123"
8. Click **Save and Close** or **Save**

**Result:** Maintenance request created and linked to MO.

---

**Method B: From Shop Floor App**

**Where to Click:**
1. Go to **Shop Floor** app (or Manufacturing → Shop Floor button)
2. Select the **Work Center** with the issue
3. Click on the **Work Order** card
4. Click the **gear icon** ⚙ at bottom right of screen
5. Click **Request Maintenance** from popup
6. Maintenance request form appears
7. Fill in details (similar to Method A)
8. Click **Save**

**Result:** Maintenance request created from shop floor.

---

**Method C: From Maintenance App**

**Where to Click:**
1. Go to **Maintenance** app
2. Click **Maintenance** → **Maintenance Requests**
3. Click **New**
4. Fill in:
   - **Name:** Describe the issue
   - **For:** Equipment or Work Center
   - **Equipment/Work Center:** Select from dropdown
   - **Maintenance Team:** Select team
   - **Technician:** Select technician
   - **Request Date:** Today
   - **Scheduled Date:** When to fix
   - **Priority:** Set urgency
   - **Description:** Detailed description
5. Click **Save**

**Result:** Maintenance request created directly.

---

##### **Step 3.2: Process Corrective Maintenance**

**Where to Click:**
1. Technician opens **Maintenance** app
2. Goes to **Maintenance** → **Maintenance Requests**
3. Opens the request (e.g., "Saw Station - No Power")
4. Reviews the issue in **Description**
5. Clicks **In Progress** button
6. Performs the repair
7. Adds notes in **Description** about what was fixed
8. If parts were used, can link to inventory scrap/usage
9. Clicks **Done** button
10. (Optional) If recurring issue, can create **Preventive Maintenance** schedule
11. Click **Save**

**Result:** Equipment repaired and ready for production.

---

##### **Step 3.3: Update Manufacturing Order**

**Where to Click:**
1. Go back to **Manufacturing** app
2. Find the MO that was blocked by equipment issue
3. Open the MO
4. Resume production by:
   - Starting work orders again
   - Or rescheduling if needed
5. Complete the MO normally

**Result:** Production resumed after maintenance.

---

#### **PHASE 4: Maintenance Calendar and Planning**

##### **Step 4.1: View Maintenance Calendar**

**Where to Click:**
1. Go to **Maintenance** app
2. Click **Maintenance** → **Maintenance Calendar**
3. You'll see a **calendar view** with all maintenance requests
4. Color-coded by team or status
5. At the right side, you'll see:
   - **Mini calendar** with today's date
   - **Technicians** list showing who has open requests
6. Click on any request to see popup with details
7. Can drag and drop to reschedule

**Result:** Visual view of all maintenance activities.

---

### MAINTENANCE METRICS EXPLAINED

**MTBF (Mean Time Between Failure):**
- Average time between equipment breakdowns
- **Expected MTBF:** Your estimate (e.g., 120 days)
- **Real MTBF:** Calculated by Odoo from actual failures
- Higher is better

**MTTR (Mean Time To Repair):**
- Average time to fix equipment
- Auto-calculated from maintenance request duration
- Lower is better

**Latest Failure:**
- Date of most recent breakdown
- Helps track equipment health

**Estimated Next Failure:**
- Odoo predicts when next failure might occur
- Based on MTBF and historical data

---

## <a id="repair-integration"></a>4. REPAIR INTEGRATION WITH MANUFACTURING

### What is Repair App?
The Repair app handles repairs for products returned by customers. Integrates with Sales, Inventory, Helpdesk, and Manufacturing.

### When to Use Repairs?
- Customer returns damaged product
- Product breaks under warranty
- Product needs repair and re-delivery
- Processing RMA (Return Merchandise Authorization)

---

### REPAIR WORKFLOW - STEP BY STEP

#### **PHASE 1: Setup for Repairs**

##### **Step 1.1: Install Required Apps**

**Where to Click:**
1. Go to **Apps** menu
2. Install **Repairs** app → Activate
3. Install **Helpdesk** app → Activate (if not already installed)
4. Ensure **Sales** and **Inventory** apps are installed

**Result:** All required apps activated.

---

##### **Step 1.2: Configure Product for Tracking**

**What:** Product must have serial number tracking to process repairs.

**Where to Click:**
1. Go to **Inventory** app
2. Go to **Configuration** → **Settings**
3. In **Traceability** section, enable:
   - ☑ **Lots & Serial Numbers**
4. Click **Save**
5. Now go to **Products** → **Products**
6. Select the product that may need repairs (e.g., "Custom Desk")
7. Click **Inventory** tab
8. In **Traceability** section:
   - **Tracking:** Select **By Unique Serial Number**
9. Click **Save**

**Result:** Product can now be tracked by serial numbers.

---

##### **Step 1.3: Configure Helpdesk Team for Repairs**

**Where to Click:**
1. Go to **Helpdesk** app
2. You'll see helpdesk teams in Kanban view
3. On your team card (e.g., "Customer Care"), click **⋮** (three dots) at top right
4. Select **Settings**
5. Scroll down to **After-Sales** section
6. Enable:
   - ☑ **Returns**
   - ☑ **Repairs**
7. Click **Save**

**Result:** Helpdesk team can now process returns and repairs.

---

#### **PHASE 2: Sell and Deliver Product**

##### **Step 2.1: Create and Confirm Sales Order**

**Where to Click:**
1. Go to **Sales** app
2. Click **Orders** → **Quotations**
3. Click **New**
4. Fill in:
   - **Customer:** Select customer (e.g., "Joey")
   - Add product line:
     - **Product:** "Custom Desk" (the one with serial tracking)
     - **Quantity:** 1
     - **Unit Price:** Enter price
5. (Optional) Add warranty product on separate line
6. Click **Confirm**

**Result:** Sales order confirmed.

---

##### **Step 2.2: Deliver Product with Serial Number**

**Where to Click:**
1. From Sales Order, click **Delivery** smart button
2. Delivery Order opens
3. In the product line, look for **Serial Numbers** column
4. Click the **📋** icon or field
5. A popup appears to assign serial number
6. Options:
   - **Create New:** Click to generate new serial (e.g., "SN001234")
   - **Select Existing:** Choose from available stock
7. Serial number assigned
8. Click **Validate** button
9. Click **Apply** to confirm delivery
10. **Remember this serial number!** (You'll need it for the return)

**Result:** Product delivered with tracked serial number.

---

#### **PHASE 3: Process Product Return**

##### **Step 3.1: Create Helpdesk Ticket**

**Scenario:** Customer reports issue with product.

**Where to Click:**
1. Go to **Helpdesk** app
2. Click on your team (e.g., "Customer Care")
3. Click **New** (or a ticket auto-created from website form)
4. Fill in:
   - **Subject:** "Issue with Custom Desk - Repair Needed"
   - **Customer:** Select customer (e.g., "Joey")
   - **Assigned To:** Select team member
   - **Priority:** Select stars (e.g., ★★★)
   - **Type:** Select "Issue"
   - **Tags:** Add relevant tags (e.g., "Website", "Repair")
5. In **Description** field, add customer's complaint
6. Click **Save**

**Result:** Helpdesk ticket created.

---

##### **Step 3.2: Initiate Return from Ticket**

**Where to Click:**
1. Still in the helpdesk ticket
2. Click **Return** button (top left)
3. A **Return** popup appears
4. You'll see:
   - **Customer:** Pre-filled
   - **Sales Order:** Select the original SO
   - **Product line:** Shows the product sold
   - **Quantity:** Change if needed (default is full quantity)
5. Click **Return** to confirm
6. A **reverse transfer** (return order) is created

**Result:** Return initiated, linked to ticket.

---

##### **Step 3.3: Specify Serial Number**

**Where to Click:**
1. Still in the ticket, look at the product line
2. In **Serial Numbers** column, click the **Details** icon (ℹ️ or 📋)
3. A popup shows serial numbers available to return
4. You'll see the serial number from the original delivery (e.g., "SN001234")
5. Verify this matches customer's return
6. Click **Save & Close**

**Result:** Serial number verified for return.

---

##### **Step 3.4: Check Warranty Status (Optional)**

**Where to Click:**
1. From the ticket, click customer name to open profile
2. Click **Sales & Purchases** smart button
3. Look at the original Sales Order
4. Check if **warranty product** was included in order lines
5. If warranty was NOT purchased, you'll need to charge for repair
6. Note this information
7. Return to ticket via breadcrumbs

**Result:** Warranty status determined.

---

##### **Step 3.5: Communicate with Customer**

**Where to Click:**
1. In the helpdesk ticket
2. Scroll down to **Chatter** (communication section)
3. Click **Send message**
4. Type: **:** (colon) to see canned responses
5. Select a template like "No Warranty - Charge for Repair"
6. Customize message if needed
7. Click **Send**
8. Customer receives notification

**Result:** Customer informed about repair costs.

---

##### **Step 3.6: Validate Return Receipt**

**What:** Confirm product physically returned to warehouse.

**Where to Click:**
1. In the helpdesk ticket, click **Return** smart button
2. Opens the **Reverse Transfer** (return receipt)
3. Verify:
   - **Product:** Custom Desk
   - **Quantity:** 1
   - **Serial Number:** SN001234 (the one customer is returning)
4. Once product arrives, click **Validate**
5. Click **Mark All Done** or **Apply
**
6. Status changes to **Done**

**Result:** Return receipt validated. Product back in warehouse.

---

#### **PHASE 4: Create and Process Repair Order**

##### **Step 4.1: Create Repair Order**

**Where to Click:**
1. Go to **Repairs** app
2. Click **New** button
3. Fill in LEFT side:
   - **Customer:** Select customer (e.g., "Joey")
   - **Product to Repair:** Select "Custom Desk"
   - **Product Quantity:** Enter **1.00**
   - **Unit of Measure:** Should auto-fill
   - **Return:** Select the return order from dropdown
   - ☐ **Under Warranty:** Check this box if warranty applies
     - If checked: Customer not charged for parts
     - If unchecked: Customer charged for parts
4. Fill in RIGHT side:
   - **Scheduled Date:** Click to select repair date
   - **Responsible:** Select repair technician
   - **Company:** Select your company
   - **Tags:** Add tags (e.g., "Furniture", "Urgent")
5. Click **Save**

**Result:** Repair order created.

---

##### **Step 4.2: Add Parts to Repair**

**What:** Specify parts needed for repair.

**Where to Click:**
1. In Repair Order, go to **Parts** tab
2. Click **Add a line**
3. Fill in the columns:
   - **Type:** Select from:
     - **Add:** Parts to add/use in repair
     - **Remove:** Parts to remove from product
     - **Recycle:** Parts to repurpose
   - **Product:** Select component (e.g., "Glass Top Replacement")
   - **Demand:** Enter quantity needed (e.g., 1)
   - **Unit of Measure:** Auto-filled
   - **Done:** Leave at 0 (technician updates this)
   - **Used:** ☐ Unchecked initially (check when used)
4. Add more lines for other parts (e.g., "Wood Frame Brace")
5. Click **Save**

**Result:** Parts list added to repair order.

---

##### **Step 4.3: Add Operations (Labor)**

**What:** Document labor/work to be done.

**Where to Click:**
1. In Repair Order, go to **Operations** tab
2. Click **Add a line**
3. Fill in:
   - **Type:** Select **Add** (adding labor)
   - **Product:** Select a service product like "Repair Labor"
     - If doesn't exist, create a service product for labor
   - **Demand:** Enter hours (e.g., 2.00 hours)
   - **Done:** Leave at 0 initially
   - **Used:** ☐ Unchecked
4. Click **Save**

**Result:** Labor operations added.

---

##### **Step 4.4: Confirm Repair Order**

**Where to Click:**
1. At top left of Repair Order
2. Click **Confirm Repair** button
3. Status changes from **Draft** to **Confirmed**
4. **Start Repair** button appears

**Result:** Repair order confirmed, ready to execute.

---

##### **Step 4.5: Execute Repair**

**Where to Click:**
1. Click **Start Repair** button
2. Status changes to **Under Repair**
3. Technician performs the repair
4. As work progresses, update the **Parts** tab:
   - Change **Done** column to actual quantity used
   - Check the **Used** checkbox for parts actually used
5. Update **Operations** tab:
   - Change **Done** column to actual hours worked
   - Check **Used** checkbox
6. Once complete, click **End Repair** button
7. Status changes to **Repaired**

**Result:** Repair work completed.

---

##### **Step 4.6: Invoice Customer (if not under warranty)**

**Where to Click:**
1. After repair ended, click **Create Invoice** button
2. Invoice popup appears
3. Review invoice lines:
   - Parts used (only those marked **Used**)
   - Labor hours
   - Total amount
4. Click **Create Invoice**
5. Invoice form opens
6. Review and click **Confirm**
7. Register payment if received

**Result:** Customer invoiced for repair.

---

#### **PHASE 5: Return Repaired Product**

##### **Step 5.1: Create Return Delivery**

**Where to Click:**
1. In the Repair Order form
2. Look for **Return** button or **Create Delivery** option
3. OR go to **Inventory** app → **Operations** → **Delivery Orders**
4. Click **New**
5. Fill in:
   - **Customer:** Select customer
   - **Source Location:** Your warehouse stock
   - **Destination Location:** Customer location
6. Add product line:
   - **Product:** Custom Desk (repaired)
   - **Quantity:** 1
   - **Serial Number:** SN001234 (same serial as returned)
7. Click **Validate**
8. Click **Apply**

**Result:** Repaired product returned to customer.

---

##### **Step 5.2: Close Helpdesk Ticket**

**Where to Click:**
1. Go back to **Helpdesk** app
2. Open the original ticket
3. Review the **chatter** to see all logged activities:
   - Return validated
   - Repair order completed
   - Delivery completed
4. Add final message: "Repair completed, product returned to customer"
5. Move ticket to **Solved** or **Closed** stage (drag in Kanban view)
6. Or click **Close** button if available

**Result:** Helpdesk ticket closed. Repair process complete!

---

### REPAIR WORKFLOW SUMMARY

**Complete Process:**
1. ✅ Configure product with serial number tracking
2. ✅ Configure Helpdesk team for returns/repairs
3. ✅ Sell and deliver product with serial number
4. ✅ Customer reports issue → Create Helpdesk ticket
5. ✅ Initiate return from ticket
6. ✅ Verify serial number
7. ✅ Check warranty status
8. ✅ Communicate with customer about charges
9. ✅ Validate return receipt (product arrives)
10. ✅ Create Repair Order in Repairs app
11. ✅ Add parts and operations (labor)
12. ✅ Confirm and execute repair
13. ✅ Invoice customer (if no warranty)
14. ✅ Return repaired product to customer
15. ✅ Close Helpdesk ticket

---

## INTEGRATION SUMMARY - ALL APPS TOGETHER

### How Apps Work Together in Manufacturing:

```
SALES ORDER (Custom Product)
    ↓
PROJECT TASK (ETO Design)
    ↓
MANUFACTURING ORDER
    ↓
QUALITY CHECKS (Before/During/After Production)
    ↓
WORK CENTER (Uses Equipment)
    ↓
MAINTENANCE REQUEST (If Equipment Breaks)
    ↓
FINISHED PRODUCT
    ↓
DELIVERY to Customer
    ↓
HELPDESK TICKET (If Issue Reported)
    ↓
RETURN ORDER (Product Comes Back)
    ↓
REPAIR ORDER (Fix the Product)
    ↓
RETURN DELIVERY (Send Back Fixed Product)
```

### Real-World Scenario - All Apps Used:

**Scenario:** Custom furniture with quality checks, equipment maintenance, and repair

1. **Sales + Project:** Customer orders custom dining table → ETO project task created
2. **Project:** Designer and engineer work on design, log hours
3. **Manufacturing:** Create MO with custom BoM
4. **Quality:** Auto quality check at assembly operation
5. **Maintenance:** Saw equipment breaks → Maintenance request created → Technician repairs
6. **Manufacturing:** Resume production after maintenance
7. **Quality:** Final inspection passes
8. **Delivery:** Ship to customer
9. **Helpdesk:** Customer reports glass top cracked in shipping
10. **Repair:** Create return → Repair order → Replace glass → Return to customer
11. **Complete:** All apps worked together seamlessly!

---

## TIPS AND BEST PRACTICES

### ETO (Engineering-to-Order):
- Always keep Template BoM blank
- Use Action → Duplicate to create custom BoMs
- Name custom BoMs with SO number for easy tracking
- Log all design hours in Project timesheets
- Update sales order pricing after design phase

### Quality Control:
- Create QCPs for critical operations only (don't overdo it)
- Use Pass-Fail type for simple checks
- Use Measure type for precise specifications
- Use Worksheet for complex multi-point inspections
- Train operators on quality check procedures

### Maintenance:
- Set realistic preventive maintenance frequencies
- Track all equipment with serial numbers and models
- Don't ignore MTBF/MTTR metrics - they predict failures
- Create maintenance requests immediately when issues occur
- Use maintenance calendar for planning

### Repairs:
- ALWAYS use serial number tracking for repairable products
- Check warranty status before creating repair order
- Communicate charges to customer before starting repair
- Document all parts used and labor hours
- Link repair orders to original sales orders

### General Integration:
- Keep naming conventions consistent (SO numbers, BoM names)
- Use tags and categories for easy filtering
- Train different departments on their specific apps
- Use chatter/messaging for communication
- Review smart buttons regularly - they show connections between apps

---

## QUICK REFERENCE - WHERE TO CLICK

| **Action** | **App** | **Menu Path** |
|------------|---------|---------------|
| Create QCP | Quality | Quality Control → Control Points → New |
| Create Maintenance Request | Maintenance | Maintenance → Maintenance Requests → New |
| Create Repair Order | Repairs | Repairs → New |
| Create ETO Project | Project | Project → New |
| Enable MTO Route | Inventory | Configuration → Settings → Multi-Step Routes |
| Create BoM | Manufacturing | Products → BoM → New |
| Create Maintenance Team | Maintenance | Configuration → Maintenance Teams → New |
| View Quality Checks | Quality | Quality Control → Quality Checks |
| View Maintenance Calendar | Maintenance | Maintenance → Maintenance Calendar |
| Process Return | Helpdesk | (Open Ticket) → Return button |

---

## CONCLUSION

You now have complete step-by-step workflows for:
- ✅ Engineering-to-Order with Project integration
- ✅ Quality Control during manufacturing
- ✅ Preventive and corrective maintenance
- ✅ Product repairs and returns

All these apps integrate seamlessly in Odoo to create a complete manufacturing ecosystem!

**Next Steps:**
1. Practice each workflow in your Odoo database
2. Configure apps one at a time
3. Create test scenarios for each integration
4. Train your team on their specific modules
5. Customize workflows to match your business processes

Good luck with your Odoo manufacturing implementation! 🎉
