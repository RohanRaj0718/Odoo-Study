# ODOO BANK RECONCILIATION - COMPLETE GUIDE
## Step-by-Step Instructions from Scratch

---

## TABLE OF CONTENTS

1. [What is Bank Reconciliation?](#what-is-bank-reconciliation)
2. [Getting Started - Prerequisites](#prerequisites)
3. [Method 1: Import Bank Transactions](#method-1-import-transactions)
4. [Method 2: Register Transactions Manually](#method-2-manual-registration)
5. [Method 3: Automatic Bank Synchronization](#method-3-bank-sync)
6. [Reconciling Transactions - Main Process](#reconciling-transactions)
   - [Way 1: Automatic Reconciliation](#way-1-automatic)
   - [Way 2: Match with Existing Items](#way-2-existing-items)
   - [Way 3: Set Account Manually](#way-3-set-account)
   - [Way 4: Using Reconciliation Models](#way-4-reconciliation-models)
7. [Advanced Scenarios](#advanced-scenarios)
8. [Common Use Cases](#common-use-cases)
9. [Tips for Your Manager Presentation](#presentation-tips)

---

## <a id="what-is-bank-reconciliation"></a>1. WHAT IS BANK RECONCILIATION?

**Definition:** Bank reconciliation is the process of matching your bank statement transactions with your accounting records (invoices, bills, payments) to ensure everything is accurate.

**Why It's Important:**
- ✅ Ensures financial accuracy
- ✅ Detects fraudulent activities
- ✅ Manages cash flow effectively
- ✅ Required for most businesses

**The Process:**
- Bank transactions come into Odoo (imported/synced/manual)
- You match them with invoices, bills, or payments
- Unmatched items are written off to appropriate accounts
- Once matched, the transaction is "reconciled"

---

## <a id="prerequisites"></a>2. GETTING STARTED - PREREQUISITES

### STEP 1: Verify Accounting App is Installed

**Where to Click:**
1. Click **Apps** (grid icon with 9 squares) in the main menu
2. Search for "Accounting"
3. If you see "Install" button, click it
4. If you see "Open" or already installed, you're good to go

**Result:** Accounting app is installed and ready.

---

### STEP 2: Access Accounting Dashboard

**Where to Click:**
1. Click **Accounting** in the main menu (left sidebar)
2. You'll see the Accounting Dashboard with your journals

**What You'll See:**
- Bank Journal card(s)
- Cash Journal card(s)
- Sales, Purchase journals
- Each journal shows summary info

**Result:** You're now on the Accounting Dashboard.

---

### STEP 3: Verify Bank Journal Exists

**Where to Look:**
- On the Accounting Dashboard, look for a card labeled **"Bank"** or your bank's name
- It shows:
  - Journal name
  - Current balance
  - Number of transactions to reconcile (e.g., "5 to reconcile")
  - Buttons: Transactions, Upload, etc.

**If No Bank Journal Exists:**
1. Click **Configuration** (top menu)
2. Click **Journals**
3. Click **Create**
4. Fill in:
   - **Type:** Bank
   - **Bank Account Number:** Your actual bank account number
   - **Bank:** Select or create your bank
   - **Currency:** Your currency (USD, EUR, etc.)
5. Click **Save**

**Result:** Bank journal is ready for transactions.

---

## <a id="method-1-import-transactions"></a>3. METHOD 1: IMPORT BANK TRANSACTIONS

This is the most common method - you download a file from your bank and import it into Odoo.

### STEP 1: Download Bank Statement from Your Bank

**What to Do:**
1. Log into your bank's online banking portal
2. Navigate to "Statements" or "Download Transactions"
3. Select date range
4. Download file in one of these formats:
   - **CSV** (Comma-Separated Values)
   - **XLSX** (Excel)
   - **OFX** (Open Financial Exchange)
   - **QIF** (Quicken Interchange Format)
   - **CAMT.053** (SEPA format)
   - **CODA** (Belgium only)
5. Save the file to your computer

**Result:** You have a bank statement file ready to import.

---

### STEP 2: Import File into Odoo

**Where to Click - Option A (From Dashboard):**
1. Go to **Accounting Dashboard**
2. Find your **Bank** journal card
3. Click the **⋮** (three vertical dots) icon at top right of the card
4. Select **Import file**
5. Click **Choose File** or drag and drop your file
6. Click **Import**

**Where to Click - Option B (Drag & Drop):**
1. Go to **Accounting Dashboard**
2. Simply **drag and drop** your bank statement file directly onto the Bank journal card

**Where to Click - Option C (From Bank Matching View):**
1. Go to **Accounting Dashboard**
2. Click on the **Bank** journal name (or **Transactions** button)
3. Click **Upload** button (top left)
4. Choose your file and import

**Result:** Import dialog opens.

---

### STEP 3: Map Columns (For CSV/XLSX Files Only)

**What Happens:**
- For CSV/XLSX files, Odoo needs to know which column is what
- Other formats (OFX, QIF, CAMT) map automatically

**Where to Click:**
1. A mapping screen appears
2. For each column in your file, select the matching Odoo field:
   - **Date** → Date column from your file
   - **Label/Description** → Transaction description
   - **Amount** → Transaction amount
   - **Partner** (optional) → Customer/vendor name
   - **Reference** (optional) → Check number or reference
3. Review the preview at the bottom
4. Click **Test** to verify
5. If no errors, click **Import**

**Important Settings:**
- **Separator:** Usually comma (,) for CSV
- **Encoding:** Usually UTF-8
- **Date Format:** Match your bank's format (MM/DD/YYYY or DD/MM/YYYY)

**Result:** Transactions are imported and appear in Bank Matching view.

---

## <a id="method-2-manual-registration"></a>4. METHOD 2: REGISTER TRANSACTIONS MANUALLY

Use this when you have just a few transactions or no file to import.

### STEP 1: Access Bank Journal

**Where to Click:**
1. Go to **Accounting Dashboard**
2. Click on your **Bank** journal name (the journal name itself, not buttons)
3. This opens the **Bank Matching** view

**Result:** You see the list of bank transactions.

---

### STEP 2: Create New Transaction

**Where to Click:**
1. In the Bank Matching view, click **New** (top left button)
2. A form appears for the transaction

**Result:** Transaction form opens.

---

### STEP 3: Fill Transaction Details

**What to Enter:**
- **Date:** *(Required)* Select the transaction date
- **Label:** *(Required)* Description (e.g., "Payment from Customer ABC")
- **Partner:** *(Optional but recommended)* Select customer or vendor
- **Amount:** Transaction amount
  - Positive for money coming IN (customer payments, deposits)
  - Negative for money going OUT (vendor payments, fees)

**Where to Click:**
1. Fill all fields
2. Click **Save** (top left)

**Result:** Transaction is created and appears in the list, ready to reconcile.

---

## <a id="method-3-bank-sync"></a>5. METHOD 3: AUTOMATIC BANK SYNCHRONIZATION

This automatically imports transactions from your bank daily.

### STEP 1: Check if Your Bank is Supported

**Where to Click:**
1. Go to **Accounting** → **Configuration** → **Settings**
2. Scroll to **Bank Synchronization** section
3. Check if your bank is listed in supported banks
4. If supported, enable **Online Synchronization**
5. Click **Save**

**Result:** Bank sync feature is enabled.

---

### STEP 2: Connect Your Bank Account

**Where to Click:**
1. Go to **Accounting Dashboard**
2. On your Bank journal, click **⋮** (three dots)
3. Select **Online Sync**
4. Follow the wizard:
   - Select your bank from the list
   - Enter your bank credentials
   - Authorize Odoo to access your transactions
   - Select which accounts to sync
5. Click **Confirm**

**Result:** Your bank is connected and will sync automatically.

---

### STEP 3: Manual Sync (When Needed)

**Where to Click:**
1. Go to **Accounting Dashboard**
2. Click **⋮** on Bank journal
3. Click **Synchronize Now**

**Result:** Latest transactions are imported immediately.

---

## <a id="reconciling-transactions"></a>6. RECONCILING TRANSACTIONS - MAIN PROCESS

Now that transactions are in Odoo, you need to match them with your accounting records.

### Access Bank Matching View

**Where to Click:**
1. Go to **Accounting Dashboard**
2. Either:
   - Click **"X to reconcile"** button (shows only unreconciled), OR
   - Click **Bank** journal name (shows all transactions)

**What You'll See:**
- List of transactions with newest first
- Each line shows:
  - Date
  - Label (description)
  - Partner (if set)
  - Suggested action buttons
  - Amount

**Result:** You're in the Bank Matching view, ready to reconcile.

---

## <a id="way-1-automatic"></a>WAY 1: AUTOMATIC RECONCILIATION

Odoo automatically suggests matches based on rules.

### How Automatic Matching Works

**Matching Rules (Applied in Order):**

1. **When NO partner is set:**
   - Odoo compares transaction label with invoice numbers, payment references

2. **When partner IS set:**
   - **Exact match:** Amount matches exactly
   - **Discounted match:** For early payment discounts
   - **Tolerance match:** Within 3% (for fees, rounding)
   - **Currency match:** Different currency with 3% tolerance
   - **Amount in label:** Invoice amount appears in transaction label

### STEP 1: Review Auto-Matched Transactions

**What to Look For:**
- Transactions with green checkmark or matched status
- Action button shows "Reconcile" or the matched item name

**Where to Click:**
1. Look at each transaction
2. If the suggested match looks correct, click the suggested button
3. Transaction is automatically validated

**Result:** Transaction is reconciled automatically.

---

### STEP 2: Handle Partially Matched Transactions

**When Amount Doesn't Match Exactly:**

**Transaction LESS than Invoice:**
- Transaction reconciles fully
- Invoice remains partially open
- You can mark invoice as "fully paid" if difference is negligible

**Transaction MORE than Invoice:**
- Transaction reconciles partially
- Remaining balance stays unreconciled
- Reconcile the remainder separately

**Result:** Partial reconciliation is recorded.

---

## <a id="way-2-existing-items"></a>WAY 2: MATCH WITH EXISTING ITEMS (MANUAL)

When automatic matching doesn't work, match manually with invoices, bills, or payments.

### STEP 1: Expand the Transaction

**Where to Click:**
1. Find the unreconciled transaction in the list
2. Click on the transaction line to expand it

**What You'll See:**
- Full details of the transaction
- All available action buttons
- Partner information

**Result:** Transaction is expanded, showing all options.

---

### STEP 2: Click "Reconcile" Button

**Where to Click:**
1. In the expanded transaction, click **Reconcile** button
2. A popup appears: "Search: Journal Items to Match"

**What Happens:**
- If partner is set, list is filtered to that partner
- Shows all open invoices, bills, payments

**Result:** Search window opens with matching items.

---

### STEP 3: Select Matching Items

**Where to Click:**
1. Browse the list of journal items (invoices, bills, payments)
2. Use search bar to find specific items
3. **Check the box** next to the matching item(s)
4. You can select multiple items if needed
5. Click **Select** button at bottom

**Example Items You'll See:**
- Customer Invoice INV/2024/0001 - $500.00
- Vendor Bill BILL/2024/0010 - $200.00
- Payment Reference PMT/123 - $100.00

**Result:** Selected items are added as counterpart entries.

---

### STEP 4: Verify Balance

**What to Check:**
- Look at the transaction line
- Check if debits = credits (balanced)
- If balanced: Green checkmark appears
- If not balanced: Remaining balance shows

**If FULLY Balanced:**
- Click **Validate** or the line auto-validates
- Transaction is reconciled

**If NOT Balanced:**
- Add more counterpart items, OR
- Use "Set Account" for remaining balance

**Result:** Transaction is matched with existing items.

---

## <a id="way-3-set-account"></a>WAY 3: SET ACCOUNT MANUALLY (WRITE-OFF)

Use this for transactions with no matching invoice/bill, like bank fees, interest, etc.

### STEP 1: Expand the Transaction

**Where to Click:**
1. Click on the unreconciled transaction to expand it

**Result:** Transaction details are visible.

---

### STEP 2: Click "Set Account" Button

**Where to Click:**
1. Look for the **Set Account** button in the action buttons
2. Click **Set Account**
3. A dropdown menu or search appears

**Result:** Account selection opens.

---

### STEP 3: Select Appropriate Account

**Where to Click:**
1. Search for the account name or number
2. Common accounts to use:
   - **Bank Fees:** "Bank Charges" or "Bank Fees" account
   - **Interest Earned:** "Interest Income" account
   - **Bank Service Charges:** "Administrative Expenses"
   - **Undeposited Funds:** "Suspense" or "Clearing" account
3. Click the account to select it

**Account Examples:**
- 611010 - Bank Fees
- 721000 - Interest Income
- 640000 - Administrative Expenses

**Result:** Account is selected.

---

### STEP 4: Adjust Amount if Needed

**When to Edit:**
- If only part of the transaction should go to this account
- If splitting between multiple accounts

**Where to Click:**
1. Click the **pencil icon** (edit) next to the line
2. Edit the **Amount** field
3. Click **Save**

**Result:** Amount is adjusted.

---

### STEP 5: Add More Lines if Needed

**If Transaction Splits Across Multiple Accounts:**
1. Click **Add a line** or **Set Account** again
2. Select different account
3. Set the amount
4. Repeat until balanced

**Result:** Multiple accounting lines are created.

---

### STEP 6: Validate the Transaction

**Where to Click:**
1. Verify the transaction is balanced (debits = credits)
2. Click **Validate** or it auto-validates

**Result:** Transaction is written off to selected account(s).

---

## <a id="way-4-reconciliation-models"></a>WAY 4: USING RECONCILIATION MODELS

Reconciliation models are pre-configured rules for recurring transactions.

### Understanding Reconciliation Models

**What They Do:**
- Automate common reconciliations
- Create counterpart entries automatically
- Save time on repetitive transactions

**Two Types:**
1. **Automatic Models:** Apply automatically when conditions match
2. **Manual Models:** Appear as action buttons, you click to apply

---

### STEP 1: Access Reconciliation Models

**Where to Click:**
1. Go to **Accounting Dashboard**
2. Click **⋮** (three dots) on Bank journal
3. Select **Models** (under Reconciliation section)

**Result:** List of reconciliation models appears.

---

### STEP 2: Review Default Models

**Common Default Models:**

1. **Internal Transfers**
   - Use: When transferring between your own bank accounts
   - Moves balance to internal transfer account

2. **Bank Fees**
   - Use: For bank charges, fees
   - Matches when label contains "Bank Fees"
   - Writes off to bank fees expense account

3. **Cash Discount**
   - Use: Early payment discounts
   - Writes off small differences to discount account

**Result:** You understand available models.

---

### STEP 3: Create Custom Reconciliation Model

**Where to Click:**
1. In Models list, click **New**
2. A form appears

**Result:** New model form opens.

---

### STEP 4: Configure Model Basic Settings

**What to Fill:**

**Model Name:** Give it a descriptive name (e.g., "Monthly Software Subscription")

**Type:** Choose one:
- **Manual:** You click a button to apply it
- **Automatic:** Applies automatically when conditions match

**Result:** Basic settings configured.

---

### STEP 5: Set Matching Conditions

**Where to Fill:**
These determine WHEN the model applies.

**Journals:** (Optional)
- Leave blank for all journals, OR
- Select specific bank journals

**Partners:** (Optional)
- Leave blank for all partners, OR
- Select specific vendors/customers

**Amount:** (Optional)
- Set if amount must be within range
- Choose: "Is lower than", "Is greater than", "Is between"
- Enter amount(s)

**Label:** (Optional but powerful)
- **Contains:** Transaction label must contain this text
- **Not Contains:** Transaction label must NOT contain this
- **Match Regex:** Use regular expressions for complex patterns

**Example Conditions:**
- Label contains: "Subscription"
- Amount is between: $45 - $55
- Partner is: Software Vendor Inc.

**Result:** Conditions are set.

---

### STEP 6: Create Counterpart Items

**Where to Click:**
1. Click on **Counterpart Items** tab
2. Click **Add a line**

**What to Fill for Each Line:**

**Partner:** (Optional)
- Select partner if needed

**Account:** (Required)
- Select the account to write off to
- Example: "Software Expenses" account

**Amount Type:** Choose one:
- **Fixed:** Exact amount (e.g., $50)
- **Percentage of balance:** % of remaining transaction balance
- **Percentage of statement line:** % of original transaction
- **From label:** Extract amount from label using regex

**Amount:**
- Enter the amount or percentage

**Label:** (Optional)
- Custom label for the counterpart line

**Example Counterpart:**
- Partner: Software Vendor Inc.
- Account: 640100 - Software Subscriptions
- Amount Type: Percentage of balance
- Amount: 100% (full amount)
- Label: Monthly Software Fee

**Result:** Counterpart entries are defined.

---

### STEP 7: Save and Test the Model

**Where to Click:**
1. Click **Save**
2. Return to **Bank Matching** view
3. Find a transaction that matches your conditions
4. Expand the transaction

**What You'll See:**
- If **Manual models:** Button with your model name appears
- If **Automatic:** Model applies automatically

**Where to Click:**
1. Click the model button
2. Counterpart entries are created
3. Validate the transaction

**Result:** Reconciliation model is working.

---

## <a id="advanced-scenarios"></a>7. ADVANCED SCENARIOS

### SCENARIO 1: Partial Payment - Mark Invoice Fully Paid

**Situation:** Customer paid $95 instead of $100 (small discount agreed).

**Where to Click:**
1. Expand the transaction
2. Click **Reconcile**
3. Select the $100 invoice
4. Click **Select**
5. A $5 difference remains

**Now Mark as Fully Paid:**
1. Click the **pencil icon** (edit) on the invoice line
2. In the edit window, click **fully paid**
3. Click **Save**

**Result:** Invoice marked as fully paid, $5 written off.

---

### SCENARIO 2: Netting (AP/AR Offsetting)

**Situation:** Customer owes you $500, but you also owe them $300. They paid net $200.

**Method A: With Bank Transaction**

**Where to Click:**
1. Find the $200 bank transaction
2. Click **Reconcile**
3. Select BOTH:
   - Customer invoice for $500 (receivable)
   - Vendor bill for $300 (payable)
4. Click **Select**
5. Everything balances: $200 = $500 - $300
6. Validate

**Result:** Both invoice and bill are partially reconciled.

---

**Method B: Without Bank Transaction**

**Where to Click:**
1. Go to **Accounting** → **Accounting** → **Reconcile**
2. Select the partner whose accounts you want to net
3. Find the receivable and payable entries
4. **Check the boxes** next to both items
5. Click **Reconcile** button (top)
6. If amounts don't match exactly:
   - Choose to **Allow partials**, OR
   - Write off the difference to an account
7. Click **Reconcile**

**Result:** Debts are netted, partner ledger is clean.

---

### SCENARIO 3: Multiple Invoices, One Payment

**Situation:** Customer paid $1,500 covering 3 invoices.

**Where to Click:**
1. Expand the $1,500 transaction
2. Click **Reconcile**
3. Select all 3 invoices:
   - ☑ Invoice #001 - $500
   - ☑ Invoice #002 - $600
   - ☑ Invoice #003 - $400
4. Click **Select**
5. Total matches: $1,500
6. Validate

**Result:** One transaction reconciles three invoices.

---

### SCENARIO 4: Bank Transfer Between Own Accounts

**Situation:** You transferred $1,000 from Bank A to Bank B.

**Transaction appears in BOTH journals:**
- Bank A: -$1,000 (outgoing)
- Bank B: +$1,000 (incoming)

**Step 1: Create Internal Transfer Account First**

**Where to Click:**
1. Go to **Accounting** → **Configuration** → **Chart of Accounts**
2. Click **New**
3. Fill in:
   - **Code:** 102000
   - **Account Name:** "Internal Transfers"
   - **Type:** Current Assets
4. Click **Save**

**Step 2: Reconcile in Bank A (Outgoing)**

**Where to Click:**
1. Go to Bank A's **Bank Matching** view
2. Expand the -$1,000 transaction
3. Look for **Internal Transfers** button (default reconciliation model)
4. Click **Internal Transfers**
5. This writes to 102000 - Internal Transfers account
6. Validate

**Step 3: Reconcile in Bank B (Incoming)**

**Where to Click:**
1. Go to Bank B's **Bank Matching** view
2. Expand the +$1,000 transaction
3. Click **Internal Transfers** button
4. This also writes to 102000 - Internal Transfers account
5. Validate

**Result:** Both sides reconciled, Internal Transfers account is balanced (±$1,000 nets to zero).

---

### SCENARIO 5: Bank Fees Deducted from Payment

**Situation:** Customer paid $1,000, but bank fee was $3, so you received $997.

**Where to Click:**
1. Expand the $997 transaction
2. Click **Reconcile**
3. Select the $1,000 invoice
4. Click **Select**
5. $3 difference remains
6. Two options now:

**Option A: Use Bank Fees Model**
1. Click **Bank Fees** button (if available)
2. $3 written off to bank fees expense
3. Validate

**Option B: Manual Write-Off**
1. Click **Set Account**
2. Search for "Bank Fees" or "Bank Charges"
3. Select the account
4. $3 is written off
5. Validate

**Result:** Payment matched, bank fee expensed.

---

## <a id="common-use-cases"></a>8. COMMON USE CASES WITH STEP-BY-STEP

### USE CASE 1: Customer Payment Received

**Details:** Customer ABC paid invoice INV/0001 for $750.

**Steps:**
1. **Import or manually enter** the $750 transaction
2. Go to **Bank Matching** view
3. Expand the transaction
4. If partner "Customer ABC" not set:
   - Click **Set Partner**
   - Search and select "Customer ABC"
5. Odoo may auto-suggest the invoice
6. Click **Reconcile** button
7. Find invoice INV/0001
8. Check the box
9. Click **Select**
10. Verify balance is zero
11. **Validate**

**Result:** Payment applied to invoice, both are reconciled.

---

### USE CASE 2: Vendor Bill Payment Made

**Details:** You paid Vendor XYZ's bill BILL/0050 for $1,200.

**Steps:**
1. **Import or enter** the -$1,200 transaction (negative = outgoing)
2. Go to **Bank Matching** view
3. Expand the transaction
4. Set partner to "Vendor XYZ" if not set
5. Click **Reconcile**
6. Find bill BILL/0050
7. Check the box
8. Click **Select**
9. Validate

**Result:** Bill payment is matched and reconciled.

---

### USE CASE 3: Monthly Subscription Fee (Recurring)

**Details:** Every month, $49.99 for "Cloud Services LLC" subscription.

**Setup Reconciliation Model:**
1. Go to **Accounting Dashboard** → **Bank** → **⋮** → **Models**
2. Click **New**
3. Name: "Cloud Services Subscription"
4. Type: **Automatic**
5. Conditions:
   - Label **Contains**: "Cloud Services"
   - Amount **Is between**: $45 - $55
6. Counterpart Items:
   - Partner: Cloud Services LLC
   - Account: "640200 - Cloud Subscriptions"
   - Amount Type: Percentage of balance
   - Amount: 100%
7. Click **Save**

**Now Every Month:**
1. Import transactions
2. Cloud Services charge appears
3. Model applies **automatically**
4. Transaction is reconciled without manual work!

**Result:** Automated reconciliation for recurring expenses.

---

### USE CASE 4: Check Payment (With Check Number)

**Details:** You wrote check #1234 to pay Vendor ABC $500.

**Steps:**
1. When registering transaction, enter:
   - Label: "Check #1234 to Vendor ABC"
   - Amount: -$500
   - Partner: Vendor ABC
2. Go to **Bank Matching** view when check clears
3. Expand transaction
4. Click **Reconcile**
5. Find the vendor bill
6. Check the box
7. Click **Select**
8. Validate

**Result:** Check payment matched to bill.

---

### USE CASE 5: Bank Interest Earned

**Details:** Bank credited $12.50 interest.

**Steps:**
1. Transaction appears: $12.50
2. Expand transaction
3. Click **Set Account**
4. Search for "Interest Income" or "721000"
5. Select the account
6. Transaction auto-balances
7. Validate

**Result:** Interest income recorded.

---

### USE CASE 6: Returned Payment / Bounced Check

**Details:** Customer payment $500 bounced, bank charged $25 fee.

**Transaction 1: Reverse the Payment**
1. Find original $500 payment (already reconciled)
2. Click to expand
3. Click **trash icon** to unreconcile
4. This opens the invoice again

**Transaction 2: Bank Fee**
1. Import the -$25 fee transaction
2. Expand it
3. Click **Set Account**
4. Select "Bank Fees" or "Bank Charges"
5. Validate

**Result:** Payment unreconciled, invoice reopens, fee expensed.

---

## <a id="presentation-tips"></a>9. TIPS FOR YOUR MANAGER PRESENTATION

### Structure Your Demo

**1. Start with the Big Picture**
- Show the Accounting Dashboard
- Explain: "These are all our accounting journals"
- Point to Bank journal card: "This shows we have X transactions to reconcile"

**2. Explain the Three Methods**
- "We can get transactions into Odoo three ways:"
  - Import files from bank
  - Enter manually
  - Automatic sync (if available)
- Demo the import process

**3. Show the Bank Matching View**
- "This is where we reconcile everything"
- Explain each column
- Show expanded vs collapsed views

**4. Demo Each Reconciliation Method**

**Simple Case:**
- "Here's a customer payment matching an invoice"
- Show how Odoo suggests it automatically
- Click Reconcile, Select, Validate
- "Done in 3 clicks!"

**Manual Case:**
- "Here's a bank fee with no invoice"
- Show Set Account method
- Select expense account
- Validate

**Recurring Case:**
- "For recurring items, we set up models"
- Show a reconciliation model
- Demo how it works automatically
- "This saves hours every month!"

**5. Show Reporting**
- Go to **Accounting** → **Reporting**
- Show **Bank Reconciliation Report**
- Highlight matched vs unmatched

### Key Points to Emphasize

✅ **Speed:** "Most transactions reconcile automatically or in 2-3 clicks"

✅ **Accuracy:** "Everything is matched to source documents"

✅ **Audit Trail:** "Every transaction links back to invoices, bills, bank statements"

✅ **Time Savings:** "Reconciliation models handle recurring items automatically"

✅ **Real-Time:** "We can see our true cash position at any moment"

### Common Questions & Answers

**Q: How long does reconciliation take?**
A: "With automatic matching and models, typically 10-15 minutes daily for small business, versus hours manually."

**Q: What if we make a mistake?**
A: "We can unreconcile any transaction and redo it. There's full audit history."

**Q: Can we reconcile multiple bank accounts?**
A: "Yes, each bank account has its own journal and reconciliation view."

**Q: What about credit cards?**
A: "Same process! Create a credit card journal and reconcile the same way."

**Q: How do we handle foreign currency?**
A: "Odoo has built-in rules for currency matching with tolerance for exchange rate differences."

---

## RECONCILIATION WORKFLOW SUMMARY

```
1. GET TRANSACTIONS INTO ODOO
   ├── Import from bank (most common)
   ├── Manual entry (occasional)
   └── Automatic sync (best, if available)
   
2. ACCESS BANK MATCHING VIEW
   └── Accounting Dashboard → Bank → "X to reconcile"
   
3. RECONCILE EACH TRANSACTION (Choose method)
   ├── Way 1: Auto-matched (Odoo suggests)
   ├── Way 2: Match with Existing Items (invoices/bills)
   ├── Way 3: Set Account (manual write-off)
   └── Way 4: Reconciliation Model (automated rules)
   
4. VALIDATE & VERIFY
   ├── Check all transactions are balanced
   ├── Review reconciliation report
   └── Done!
```

---

## QUICK REFERENCE - KEY SCREENS

### Accounting Dashboard
**Path:** Accounting (main menu)
**Purpose:** Overview of all journals
**Key Actions:** Access bank journal, see items to reconcile

### Bank Matching View
**Path:** Accounting Dashboard → Bank journal name
**Purpose:** Main reconciliation workspace
**Key Actions:** Expand transactions, reconcile, validate

### Reconciliation Models
**Path:** Accounting Dashboard → Bank → ⋮ → Models
**Purpose:** Create automation rules
**Key Actions:** Create models, set conditions, define counterparts

### Manual Reconciliation Tool
**Path:** Accounting → Accounting → Reconcile
**Purpose:** Reconcile items without bank transactions (netting)
**Key Actions:** Select multiple items, reconcile, handle partials

### Chart of Accounts
**Path:** Accounting → Configuration → Chart of Accounts
**Purpose:** View and manage accounts
**Key Actions:** Find account codes, create new accounts

---

## BEST PRACTICES

✅ **DO:**
- Reconcile daily or weekly (don't let it pile up)
- Use reconciliation models for recurring items
- Set partners on transactions for better matching
- Review and test models before using automatic type
- Keep account names clear and consistent
- Document unusual reconciliations in the chatter

❌ **DON'T:**
- Don't force reconciliation if amounts don't match (investigate first)
- Don't ignore unbalanced transactions
- Don't create duplicate transactions
- Don't delete transactions without investigating
- Don't skip verification after reconciliation

---

## NEXT STEPS AFTER MASTERING BASICS

1. **Set Up Reconciliation Models** for all recurring items
2. **Configure Bank Sync** if your bank supports it
3. **Train Team** on daily reconciliation workflow
4. **Review Reports** weekly for accuracy
5. **Optimize** - refine models based on what you learn

---

## TROUBLESHOOTING COMMON ISSUES

### Issue: Transaction Not Matching Invoice
**Solution:**
- Check partner is set correctly
- Verify amount matches (within 3% tolerance)
- Check invoice is posted (not draft)
- Try searching manually in Reconcile button

### Issue: Can't Find Correct Account
**Solution:**
- Go to Chart of Accounts
- Search by name or number
- Create new account if needed
- Use search bar with partial names

### Issue: Reconciliation Model Not Applying
**Solution:**
- Check model type is correct (Auto vs Manual)
- Verify matching conditions are met
- Check model sequence order
- Test with manual button first

### Issue: Transaction Imported Twice
**Solution:**
- Go to Bank Matching view
- Click Actions → Find Duplicate Transactions
- Select duplicates
- Delete unnecessary ones

---

**END OF GUIDE**

---

This guide covers everything you need to demonstrate bank reconciliation to your manager. Practice each method a few times before your presentation, and you'll be confident showing how efficient Odoo's reconciliation process is!

Good luck with your presentation! 🎉
