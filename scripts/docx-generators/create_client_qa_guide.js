const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak, TabStopType, TabStopPosition
} = require("docx");

// ── Reusable helpers ──
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const thickBorder = { style: BorderStyle.SINGLE, size: 2, color: "2E74B5" };
const thickBorders = { top: thickBorder, bottom: thickBorder, left: thickBorder, right: thickBorder };

const HEADER_BG = "2E74B5";
const ALT_BG = "F2F7FB";
const WHITE = "FFFFFF";
const TIP_BG = "E8F5E9";
const WARN_BG = "FFF3E0";
const NOTE_BG = "E3F2FD";

function headerCell(text, width) {
  return new TableCell({
    borders: thickBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: HEADER_BG, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 22 })] })]
  });
}

function cell(children, width, bg = WHITE) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: bg, type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: Array.isArray(children) ? children : [children]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after || 120, before: opts.before || 0 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: "Arial", size: opts.size || 22, bold: opts.bold || false, color: opts.color || "333333", italics: opts.italic || false })]
  });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    spacing: { before: level === HeadingLevel.HEADING_1 ? 300 : 200, after: 150 },
    children: [new TextRun({ text, font: "Arial" })]
  });
}

function tipBox(label, text, bg) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({ children: [new TableCell({
      borders: { top: { style: BorderStyle.SINGLE, size: 3, color: bg === TIP_BG ? "4CAF50" : bg === WARN_BG ? "FF9800" : "2196F3" }, bottom: border, left: border, right: border },
      width: { size: 9360, type: WidthType.DXA },
      shading: { fill: bg, type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      children: [
        new Paragraph({ children: [new TextRun({ text: label, bold: true, font: "Arial", size: 22, color: bg === TIP_BG ? "2E7D32" : bg === WARN_BG ? "E65100" : "1565C0" })] }),
        new Paragraph({ spacing: { before: 60 }, children: [new TextRun({ text, font: "Arial", size: 20, color: "444444" })] })
      ]
    })] })]
  });
}

function stepsList(steps) {
  const rows = steps.map((s, i) => {
    return new Paragraph({
      spacing: { after: 80 },
      children: [
        new TextRun({ text: `Step ${i + 1}: `, bold: true, font: "Arial", size: 22, color: "2E74B5" }),
        new TextRun({ text: s, font: "Arial", size: 22, color: "333333" })
      ]
    });
  });
  return rows;
}

function spacer() { return new Paragraph({ spacing: { after: 80 } }); }
function pageBreak() { return new Paragraph({ children: [new PageBreak()] }); }

// ── Q&A Data ──
const qas = [
  {
    category: "Getting Started & Navigation",
    questions: [
      {
        q: "I have 4 companies/branches. How do I switch between them to see their individual data?",
        realLife: "You're sitting at your office in Pathanamthitta and want to check what's happening at your Kochi showroom (KDESIGN INTERIOR).",
        steps: [
          "Log in to Odoo at your URL (e.g., client-cient.odoo.com)",
          "Look at the TOP-RIGHT corner of the screen — you'll see a company name (e.g., \"Krishnadas Group\")",
          "Click on it → a dropdown shows all your companies/branches",
          "UNCHECK all companies except the one you want (e.g., check only \"KDESIGN INTERIOR\")",
          "The page refreshes — now ALL data you see (sales, purchases, reports) belongs ONLY to KDESIGN INTERIOR",
          "To go back to parent view, check \"Krishnadas Group\" again"
        ],
        tip: "CRITICAL: Always check which company is selected before looking at any report. If you see combined data, it means multiple companies are selected."
      },
      {
        q: "What is the difference between Krishnadas Group, Devika Furniture, KDESIGN INTERIOR, and KDESIGN INTERIOR FURNISHING?",
        realLife: "You want to understand the legal structure set up in Odoo.",
        steps: [
          "Go to Settings → Companies to see all companies",
          "Krishnadas Group (Parent) — GSTIN 32AABFK5678M1ZQ, Pathanamthitta. This is the parent/holding entity",
          "Devika Furniture (Branch of KG) — Same GSTIN, Pathanamthitta. Branch under Krishnadas Group",
          "KDESIGN INTERIOR (Branch of KG) — Same GSTIN, Kochi. Branch under Krishnadas Group",
          "KDESIGN INTERIOR FURNISHING — GSTIN 32AAKCK2345R1Z5, Pathanamthitta. This is a SEPARATE legal entity with its own GSTIN"
        ],
        tip: "Branches (Devika, KDESIGN) share the parent's GSTIN. KDESIGN INT. FURNISHING has its own GSTIN — so it files GST separately."
      },
      {
        q: "Where do I find the main menu? I don't know where anything is.",
        realLife: "First time logging in, feeling overwhelmed by the interface.",
        steps: [
          "After login, you see the HOME SCREEN with app icons (like apps on a phone)",
          "Key apps you'll use daily: Sales, Purchase, Invoicing/Accounting, Inventory",
          "Click any app icon to enter that module",
          "Inside each module, the LEFT sidebar or TOP menu bar shows sub-sections",
          "To go back to home, click the grid icon (⊞) at the top-left corner",
          "Use the SEARCH BAR at the top of any list to filter records"
        ],
        tip: "Think of Odoo like a smartphone — each app (Sales, Purchase, Accounting) is like an app on your phone. Click to open, use the home button to go back."
      }
    ]
  },
  {
    category: "Sales & Invoicing",
    questions: [
      {
        q: "A customer just called and wants to buy some recliners. How do I create a sales order?",
        realLife: "Varghese & Sons calls and wants 3 Las Vegas Recliners for their new project.",
        steps: [
          "First, switch to the correct branch (e.g., Devika Furniture) using Company Selector (top-right)",
          "Go to Sales app → Orders → click CREATE button",
          "In the \"Customer\" field, start typing \"Varghese\" — select from dropdown",
          "In the \"Order Lines\" section, click \"Add a line\"",
          "Type the product name (e.g., \"Las Vegas Recliner\") — select it",
          "Enter Quantity: 3. The price fills automatically from the product",
          "Click CONFIRM to confirm the quotation → it becomes a Sales Order",
          "The order is now confirmed but NOT yet invoiced"
        ],
        tip: "A Sales Order is NOT an invoice. The customer doesn't owe money until you create an invoice from this order."
      },
      {
        q: "The customer received the goods. Now how do I create an invoice and send it?",
        realLife: "The delivery is done, now you need to bill the customer.",
        steps: [
          "Go to Sales → Orders → find the confirmed Sales Order",
          "Open the Sales Order — you'll see a \"CREATE INVOICE\" button at the top",
          "Click CREATE INVOICE → a popup appears",
          "Select \"Regular Invoice\" (most common) → click CREATE AND VIEW INVOICE",
          "Review the invoice — check amounts, taxes (GST), and customer details",
          "Click CONFIRM to post the invoice (it gets a number like INV/25-26/0001)",
          "Click SEND & PRINT to email the invoice to the customer as PDF",
          "The invoice now appears in Accounting → Customer Invoices"
        ],
        tip: "Once an invoice is CONFIRMED (posted), it cannot be deleted — only reversed with a Credit Note. So always review before confirming."
      },
      {
        q: "A customer made a payment. How do I record it?",
        realLife: "Rajan Pillai transferred ₹41,000 to your bank account against his invoice.",
        steps: [
          "Go to Accounting → Customer Invoices → open the unpaid invoice",
          "Click REGISTER PAYMENT button at the top",
          "Select Journal: choose the correct bank (e.g., \"Bank Federal 3185\" for KG)",
          "Amount: auto-fills with invoice total. Change if partial payment (e.g., ₹25,000 out of ₹43,050)",
          "Payment Date: enter the date the money was received",
          "Memo: optionally add reference (e.g., \"NEFT Ref: UTR123456\")",
          "Click CREATE PAYMENT",
          "The invoice status changes to \"In Payment\" or \"Paid\""
        ],
        tip: "If the customer pays LESS than the full amount, Odoo marks it as \"Partial\" — the remaining balance stays open. You'll see it in Aged Receivables."
      },
      {
        q: "A customer is unhappy and returned some items. How do I handle the refund?",
        realLife: "Anoop Krishnan returned 5 wallpaper rolls (out of 10 ordered) because of color mismatch.",
        steps: [
          "Go to Accounting → Customer Invoices → open the original invoice",
          "Click ADD CREDIT NOTE button",
          "Select reason: \"Goods Returned\" or type your own reason",
          "Choose \"Partial Refund\" — this creates a new credit note you can edit",
          "In the credit note, adjust quantities to only the returned items (e.g., 5 rolls instead of 10)",
          "Click CONFIRM to post the credit note",
          "The original invoice balance is automatically reduced",
          "If customer already paid, you can refund the money or keep it as credit for next purchase"
        ],
        tip: "Credit Notes are the legal way to reverse an invoice. Never delete a posted invoice — always use a Credit Note."
      },
      {
        q: "How do I check which customers haven't paid yet?",
        realLife: "End of month — you want to follow up on unpaid invoices.",
        steps: [
          "Switch to the specific branch first (or stay on parent to see all)",
          "Go to Accounting → Reporting → Partner Reports → Aged Receivable",
          "This shows ALL customers with outstanding balances, grouped by how late they are",
          "Columns: Not Due, 0-30 days, 30-60 days, 60-90 days, 90-120 days, Older",
          "Click on any customer row to drill down into their individual invoices",
          "You can also filter by specific date or partner"
        ],
        tip: "Run this report EVERY WEEK. Customers with amounts in 60-90 day columns need immediate follow-up calls."
      }
    ]
  },
  {
    category: "Purchasing & Vendor Bills",
    questions: [
      {
        q: "I need to order raw materials from a supplier. How do I create a purchase order?",
        realLife: "You need 50 Roller Blind Clutches from Malabar Furnishing Suppliers for the KDESIGN branch.",
        steps: [
          "Switch to KDESIGN INTERIOR using Company Selector",
          "Go to Purchase app → Orders → click CREATE",
          "In \"Vendor\" field, type \"Malabar\" — select Malabar Furnishing Suppliers",
          "Click \"Add a line\" → search for \"Roller Blind Clutch\" → select it",
          "Enter Quantity: 50. Price auto-fills from product or last purchase price",
          "Check the Delivery Date (when you expect the goods)",
          "Click CONFIRM ORDER → the PO gets a number (e.g., PO00029)",
          "The vendor is now notified (if email is configured), and you wait for delivery"
        ],
        tip: "A confirmed PO doesn't create a bill. The bill comes AFTER you receive the goods and the vendor sends their invoice."
      },
      {
        q: "The supplier sent the goods and their invoice. How do I enter the bill?",
        realLife: "Southern Mattress Factory delivered recliners and sent a bill for ₹78,750.",
        steps: [
          "Go to Purchase → open the confirmed Purchase Order",
          "Click RECEIVE PRODUCTS first (to record that goods arrived)",
          "After receiving, go back to the PO → click CREATE BILL",
          "The bill auto-fills with PO details (products, quantities, prices)",
          "Enter the Vendor's Bill Number (printed on their invoice, e.g., \"SMF/2026/0342\")",
          "Enter the Bill Date (from the vendor's invoice)",
          "Click CONFIRM to post the bill",
          "Now go to REGISTER PAYMENT to pay the vendor"
        ],
        tip: "Always enter the Vendor Bill Reference — this is THEIR invoice number. It helps during reconciliation and avoids duplicate bill entries."
      },
      {
        q: "How do I check which vendors I need to pay?",
        realLife: "End of week — your accountant asks which vendor payments are due.",
        steps: [
          "Switch to the correct branch",
          "Go to Accounting → Reporting → Partner Reports → Aged Payable",
          "This shows ALL vendors with unpaid bills, grouped by due date",
          "Columns show: Not Due, 0-30 days overdue, 30-60 days, etc.",
          "Click any vendor to see their individual bills",
          "Use this to prioritize payments — pay the oldest dues first"
        ],
        tip: "Compare this with your bank balance before making payments. You can also use Accounting → Vendors → Bills and filter by \"Not Paid\" status."
      },
      {
        q: "I placed an order but the supplier can't deliver. How do I cancel the PO?",
        realLife: "Travancore Wood Works says the Wall Art is out of stock for 3 months.",
        steps: [
          "Open the Purchase Order",
          "If it's still in DRAFT, simply click CANCEL",
          "If already CONFIRMED, click CANCEL — Odoo may ask for confirmation",
          "If goods were already PARTIALLY received, you can only cancel the remaining quantity",
          "Cancelled POs are kept for records but don't affect accounting"
        ],
        tip: "Don't delete POs — cancel them instead. This maintains an audit trail. You can always create a new PO for a different supplier."
      }
    ]
  },
  {
    category: "Reports & Branch-Wise Data",
    questions: [
      {
        q: "I want to see total sales for only my Kochi branch this month. How?",
        realLife: "Monthly review meeting — need Kochi branch (KDESIGN) sales figure.",
        steps: [
          "Switch to KDESIGN INTERIOR using Company Selector (top-right)",
          "Go to Accounting → Reporting → Profit & Loss",
          "The report shows ONLY KDESIGN data",
          "Set the date filter to \"This Month\" or custom range",
          "Look at \"Income\" section for total sales revenue",
          "Click on the amount to drill down into individual journal entries",
          "To export: click the download icon → choose PDF or Excel"
        ],
        tip: "ALL reports in Odoo respect the Company Selector. Switch company FIRST, then open the report."
      },
      {
        q: "How do I compare branch performance — which branch sold more?",
        realLife: "Quarterly review — you want to know if Devika or KDESIGN performed better.",
        steps: [
          "Switch to Devika Furniture → Go to Accounting → Profit & Loss → Note the total income figure",
          "Switch to KDESIGN INTERIOR → same report → Note the total income",
          "Compare the two numbers",
          "For a combined view: select ALL companies in Company Selector",
          "The Profit & Loss will show combined figures",
          "Alternatively, use Sales → Reporting → Sales Analysis for a graphical comparison"
        ],
        tip: "Odoo doesn't have a single \"Branch Comparison\" report out of the box. You need to check each branch individually or export data to Excel for a side-by-side comparison."
      },
      {
        q: "How do I see the balance sheet for my company?",
        realLife: "Bank requested the balance sheet for a loan application.",
        steps: [
          "Select the company (e.g., Krishnadas Group) in Company Selector",
          "Go to Accounting → Reporting → Balance Sheet",
          "Set the date to the period needed (e.g., as of 31-Mar-2026)",
          "The report shows: Assets, Liabilities, and Equity",
          "Click any line item to drill down into individual entries",
          "To export for the bank: click the download/print icon → PDF",
          "For formal submission, download as Excel and format with your letterhead"
        ],
        tip: "Make sure all invoices and bills are posted before generating the balance sheet. Draft entries are NOT included."
      },
      {
        q: "How do I see all transactions of a specific customer across all branches?",
        realLife: "Varghese & Sons has transactions with multiple branches. You want the complete picture.",
        steps: [
          "Select ALL companies in Company Selector (check all boxes)",
          "Go to Accounting → Reporting → Partner Reports → Partner Ledger",
          "Search or filter by \"Varghese & Sons Builders\"",
          "The report shows ALL invoices, payments, and credit notes across all companies",
          "Each entry shows which company/branch it belongs to",
          "To see branch-specific: switch to that branch first, then check Partner Ledger"
        ],
        tip: "Partner Ledger is your most powerful tool for customer follow-ups. It shows everything — invoices, payments, credit notes — in chronological order."
      },
      {
        q: "My accountant asked for the General Ledger. Where is it?",
        realLife: "Preparing for audit — CA needs the general ledger for FY 2025-26.",
        steps: [
          "Switch to the required company",
          "Go to Accounting → Reporting → General Ledger",
          "Set date range: 01-Apr-2025 to 31-Mar-2026",
          "The report lists every account with all journal entries",
          "Expand any account (click ▶) to see individual entries",
          "Use filters to narrow down to specific accounts (e.g., only Bank accounts)",
          "Export to Excel using the download icon for your CA"
        ],
        tip: "The General Ledger is the foundation of all accounting. If your CA asks for it, always generate it per company (branch), not the combined view."
      }
    ]
  },
  {
    category: "GST & Tax Compliance (India)",
    questions: [
      {
        q: "How does GST work in Odoo? Do I need to calculate it manually?",
        realLife: "You wonder if you need to add 9% SGST + 9% CGST to every invoice yourself.",
        steps: [
          "NO — GST is automatic in Odoo",
          "Each product has a default tax assigned (e.g., 5% GST which splits into 2.5% SGST + 2.5% CGST)",
          "When you create a Sales Order or Invoice, the tax is auto-applied based on the product",
          "Intra-state sales (within Kerala): SGST + CGST are applied",
          "Inter-state sales (to other states): IGST is applied instead",
          "You can see the tax breakdown on every invoice in the \"Tax Summary\" section at the bottom"
        ],
        tip: "If a product shows wrong tax, go to the product → Accounting tab → change the \"Customer Taxes\" field. Don't change tax on individual invoices."
      },
      {
        q: "How do I generate my GSTR-1 or GST return data from Odoo?",
        realLife: "Monthly GST filing deadline is approaching and your CA needs the data.",
        steps: [
          "Switch to the correct company",
          "Go to Accounting → Reporting → India GST Reports (if available in your edition)",
          "Or: Go to Accounting → Reporting → Tax Report",
          "Set the period (e.g., March 2026)",
          "The report shows total taxable value, SGST, CGST, IGST amounts",
          "Export the data in Excel format",
          "Share with your CA/Tax consultant for filing on the GST portal",
          "For GSTR-1 specifically: invoice-wise data with customer GSTIN is needed — your CA will map it"
        ],
        tip: "Odoo generates TAX data, but actual GST filing happens on the GST portal (gst.gov.in). Odoo provides the numbers, your CA files the return."
      },
      {
        q: "One of my branches has a different GSTIN. Does that matter?",
        realLife: "KDESIGN INTERIOR FURNISHING has its own GSTIN (32AAKCK2345R1Z5) unlike the branches.",
        steps: [
          "Yes, it matters significantly!",
          "Branches sharing the SAME GSTIN (KG, Devika, KDESIGN) → file ONE consolidated GST return",
          "KDESIGN INT. FURNISHING has its OWN GSTIN → files a SEPARATE GST return",
          "In Odoo, each company's GSTIN is set in Settings → Companies → (select company) → GSTIN field",
          "Transactions between same-GSTIN branches are internal (not GST-applicable)",
          "Transactions between different-GSTIN entities are treated as separate legal entities (GST applies)"
        ],
        tip: "When transferring goods between KG branches (same GSTIN) → use Stock Transfer (no GST). When selling to KDESIGN INTERIOR FURNISHING → treat as inter-company sale (GST applies)."
      }
    ]
  },
  {
    category: "Payments & Banking",
    questions: [
      {
        q: "I received money in my bank. How do I update it in Odoo?",
        realLife: "You check your Federal Bank 3185 statement and see 3 credits from different customers.",
        steps: [
          "Go to Accounting → Bank → select the bank journal (e.g., Bank Federal 3185)",
          "Odoo shows a bank reconciliation view",
          "Option A — Manual: Click \"+ New\" for each transaction. Enter date, label, amount, and partner",
          "Option B — Import: If your bank provides CSV/OFX statements, click \"Import\" → upload the file",
          "For each bank transaction, Odoo tries to MATCH it with open invoices/bills automatically",
          "Click VALIDATE on each matched pair to reconcile",
          "Unmatched transactions stay for later — you can match them when the corresponding invoice is created"
        ],
        tip: "Reconciliation is the KEY to accurate books. Do it daily or weekly. Unreconciled items mean your Odoo balance doesn't match your bank balance."
      },
      {
        q: "Can I pay a vendor directly from Odoo or do I use my bank's net banking?",
        realLife: "You want to know if Odoo does actual bank transfers.",
        steps: [
          "Odoo does NOT make actual bank transfers — you still use your bank's net banking or UPI",
          "In Odoo, you RECORD the payment to keep your books accurate",
          "Process: 1) Pay the vendor via your bank, 2) Come to Odoo, 3) Register the payment against the bill",
          "When you import your bank statement, the payment you made will show up",
          "You reconcile the bank statement line with the Odoo payment entry",
          "Then everything matches: your bank statement = Odoo records"
        ],
        tip: "Odoo is your accounting record-keeper, not a bank. Make payments through your bank, then record them in Odoo."
      },
      {
        q: "Each branch has its own bank account. How do I manage them?",
        realLife: "Devika has Bank Devika 4501, KDESIGN has Bank KDESIGN 7802, KG has Federal 3185 and SIB 0388.",
        steps: [
          "Each bank account is set up as a separate \"Journal\" in Odoo",
          "Switch to the correct branch → Go to Accounting → Configuration → Journals",
          "Each branch sees only ITS OWN bank journals",
          "KG: Federal Bank 3185, SIB 0388, Cash",
          "Devika: Bank Devika 4501, Cash Devika",
          "KDESIGN: Bank KDESIGN 7802, Cash KDESIGN",
          "KFURN: Its own bank journal",
          "When registering payments, always select the correct bank journal for that branch"
        ],
        tip: "Never record a Devika branch payment against KG's bank journal. Always match the company and its bank."
      }
    ]
  },
  {
    category: "Inventory & Stock",
    questions: [
      {
        q: "How do I check the current stock of a product?",
        realLife: "Customer asks if you have 5 Las Vegas Recliners in stock at the KDESIGN showroom.",
        steps: [
          "Switch to KDESIGN INTERIOR",
          "Go to Inventory app → Products → search for \"Las Vegas Recliner\"",
          "Open the product → you'll see \"On Hand\" quantity (what's physically in warehouse)",
          "\"Forecasted\" shows what will be available (considering incoming POs and outgoing SOs)",
          "Click on the quantity number to see detailed stock by warehouse/location",
          "For all products at once: Inventory → Reporting → Inventory Report"
        ],
        tip: "\"On Hand\" = what you have RIGHT NOW. \"Forecasted\" = On Hand + Incoming - Outgoing. Always check Forecasted before promising delivery."
      },
      {
        q: "I want to move products from Devika's warehouse to KDESIGN in Kochi. How?",
        realLife: "Kochi showroom is running low on recliners but Devika has extra stock.",
        steps: [
          "Since Devika and KDESIGN are branches of the SAME company (KG), this is an internal transfer",
          "Go to Inventory → Operations → Transfers → click CREATE",
          "Operation Type: select \"Internal Transfer\"",
          "Source Location: Devika's warehouse",
          "Destination Location: KDESIGN's warehouse",
          "Add products and quantities to transfer",
          "Click CONFIRM → then VALIDATE when goods are physically shipped",
          "Stock automatically moves in Odoo's records"
        ],
        tip: "Internal transfers between same-company branches don't have GST implications. For transfers to KDESIGN INT. FURNISHING (different GSTIN), you'd need a proper sale/purchase transaction."
      },
      {
        q: "How do I know if I need to reorder something? Does Odoo alert me?",
        realLife: "You keep running out of Roller Blind Clutches and want automatic ordering.",
        steps: [
          "Open the product → go to the \"Reordering Rules\" tab (or Inventory tab)",
          "Click \"Create a reordering rule\"",
          "Set Minimum Quantity (e.g., 20) — when stock drops below this, Odoo alerts",
          "Set Maximum Quantity (e.g., 100) — Odoo will order up to this",
          "Set Route: \"Buy\" (for purchase) or \"Manufacture\" (if you make it)",
          "Odoo's scheduler runs automatically and creates Draft POs when stock is low",
          "You review and confirm the auto-generated POs"
        ],
        tip: "Set reordering rules for your fast-moving products. This prevents stockouts and removes manual monitoring."
      }
    ]
  },
  {
    category: "Day-to-Day Operations",
    questions: [
      {
        q: "How do I add a new customer or vendor?",
        realLife: "A new interior designer wants to buy products from you regularly.",
        steps: [
          "Go to Sales → Customers (for customer) OR Purchase → Vendors (for vendor)",
          "Click CREATE",
          "Enter: Name, Phone, Email, Address",
          "For GST: Enter their GSTIN in the Tax ID field (if they have one)",
          "Set the payment terms (e.g., \"30 Days\" or \"Immediate Payment\")",
          "Click SAVE",
          "The partner is now available when creating Sales Orders or Purchase Orders"
        ],
        tip: "If someone is BOTH a customer and vendor (they buy from you AND you buy from them), create them once and check both \"Customer\" and \"Vendor\" options."
      },
      {
        q: "How do I add a new product?",
        realLife: "You're starting to sell a new line of smart curtain motors.",
        steps: [
          "Go to Inventory → Products → click CREATE",
          "Enter: Product Name, Internal Reference (SKU), Sales Price, Cost Price",
          "Product Type: \"Goods\" (if you track inventory) or \"Service\" (if not)",
          "Under Sales tab: set \"Customer Taxes\" (e.g., 18% GST S)",
          "Under Purchase tab: set \"Vendor Taxes\" (e.g., 18% GST P)",
          "Add a product image (optional but recommended)",
          "Click SAVE",
          "The product is now available in Sales Orders and Purchase Orders"
        ],
        tip: "Always set BOTH sales tax and purchase tax on a product. Missing tax = incorrect GST on invoices/bills."
      },
      {
        q: "Can my staff access Odoo? How do I control what they can see?",
        realLife: "Your sales person should be able to create quotations but NOT see vendor bills or bank balances.",
        steps: [
          "Go to Settings → Users & Companies → Users",
          "Click CREATE to add a new user, enter name and email",
          "Under \"Access Rights\", set permissions per module:",
          "Sales: \"User: Own Documents\" (they see only their own quotations)",
          "Purchase: \"None\" (they can't access purchase at all)",
          "Accounting: \"None\" (they can't see financial data)",
          "Inventory: \"User\" (they can check stock but not modify settings)",
          "Set the correct company — they'll only see data from their assigned company/branch"
        ],
        tip: "Give minimum access needed. Your accountant needs Accounting access, your sales team needs Sales access — never give everyone full admin rights."
      },
      {
        q: "I created something wrong (wrong invoice, wrong amount). How do I fix it?",
        realLife: "You accidentally invoiced ₹39,000 instead of ₹29,000 for a recliner.",
        steps: [
          "If the document is still in DRAFT: Simply edit and fix it directly",
          "If the invoice is already POSTED (confirmed):",
          "DO NOT try to delete it — posted documents can't be deleted",
          "Click ADD CREDIT NOTE on the invoice → reverse the full amount",
          "Then create a new, correct invoice",
          "For Posted Bills (vendor): same process — Reverse Entry → create new bill",
          "For Confirmed Sales Orders: click CANCEL, then create a new one",
          "Always add a note explaining why the correction was made"
        ],
        tip: "This is standard accounting practice — errors are corrected with reversals, not deletions. This keeps your audit trail clean."
      }
    ]
  },
  {
    category: "Advanced Scenarios",
    questions: [
      {
        q: "I want to create a delivery challan for goods being transported between branches. Does Odoo support this?",
        realLife: "Transporting furniture from Pathanamthitta to Kochi requires a delivery challan for roadside checking.",
        steps: [
          "Odoo 19 supports E-Way Bill generation for India through the l10n_in_ewaybill_stock module",
          "Install the module: Settings → Apps → search \"E-Way Bill\"",
          "Configure your E-Way Bill credentials in Settings → Indian Localization",
          "When creating delivery orders (DO), the E-Way Bill option becomes available",
          "For goods value > ₹50,000: E-Way Bill is MANDATORY as per GST rules",
          "Odoo generates the E-Way Bill and links it to the delivery order",
          "You can print the E-Way Bill to accompany the shipment"
        ],
        tip: "E-Way Bill is required for transporting goods >₹50,000. Even for intra-state transfers between your own branches, if the value exceeds the threshold, generate an E-Way Bill."
      },
      {
        q: "Can one branch automatically order from another branch when stock is low?",
        realLife: "KDESIGN Kochi runs out of stock — can it auto-pull from Devika's warehouse?",
        steps: [
          "Odoo's \"Resupply From\" feature works ONLY within the same company",
          "For branches under the same company: Go to Inventory → Configuration → Warehouses",
          "Open KDESIGN's warehouse → check \"Resupply From\" → select Devika's warehouse",
          "This creates an automatic route: when KDESIGN runs low, it pulls from Devika",
          "For KDESIGN INT. FURNISHING (different company): this feature does NOT work",
          "Workaround for different companies: create an inter-company PO/SO manually",
          "Set up reordering rules at each warehouse for the auto-trigger"
        ],
        tip: "Auto-resupply between branches is a powerful feature but only works within the same legal entity. For cross-company transfers, you need manual inter-company transactions."
      },
      {
        q: "Two customers paid the same amount on the same day. How do I know which payment is for which invoice?",
        realLife: "Both Rajan Pillai and Anoop paid ₹5,000 into your bank on 3rd March.",
        steps: [
          "Go to Accounting → Bank → open the bank journal",
          "You'll see both ₹5,000 entries in the bank statement",
          "For each entry, check the UTR/reference number from your bank statement",
          "Match each bank entry to the correct customer:",
          "Click the bank statement line → Odoo suggests matching invoices",
          "Select the correct customer invoice → click VALIDATE",
          "If Odoo suggests the wrong match, manually search for the correct invoice using the Partner filter",
          "After reconciling both, each payment is linked to the correct customer"
        ],
        tip: "Always ask customers to include their invoice number as payment reference. This makes reconciliation much faster."
      },
      {
        q: "How do I close the financial year at the end of March?",
        realLife: "It's April 2026 — your CA says you need to close FY 2025-26 books.",
        steps: [
          "IMPORTANT: Odoo does NOT require mandatory year-end closing like some software",
          "Profit & Loss automatically resets for the new fiscal year",
          "Balance Sheet carries forward all balances automatically",
          "To prevent changes to closed period: Go to Accounting → Configuration → Settings",
          "Set \"Lock Date\" to 31-Mar-2026 — this prevents anyone from posting entries in the old year",
          "Also set \"Tax Lock Date\" to 31-Mar-2026 to prevent tax-related entries",
          "Your CA can still make adjusting entries if you create a special \"Advisors\" lock date"
        ],
        tip: "Set the Lock Date immediately after your CA confirms the final year-end entries. This protects historical data from accidental changes."
      }
    ]
  }
];

// ── Build document ──
const children = [];

// Title page
children.push(new Paragraph({ spacing: { before: 3000, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "CLIENT Q&A GUIDE", font: "Arial", size: 52, bold: true, color: "2E74B5" })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "Multi-Company & Multi-Branch Setup in Odoo 19", font: "Arial", size: 32, color: "555555" })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "Krishnadas Group — Devika Furniture — KDESIGN INTERIOR — KDESIGN INT. FURNISHING", font: "Arial", size: 24, color: "777777" })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Real-Life Scenarios with Step-by-Step Solutions", font: "Arial", size: 26, italics: true, color: "888888" })] }));

// Info table
children.push(new Table({
  width: { size: 6000, type: WidthType.DXA },
  columnWidths: [2400, 3600],
  rows: [
    new TableRow({ children: [
      cell(para("Prepared By", { bold: true, size: 20 }), 2400, ALT_BG),
      cell(para("Rohan Raj, Business Analyst", { size: 20 }), 3600)
    ]}),
    new TableRow({ children: [
      cell(para("Company", { bold: true, size: 20 }), 2400, ALT_BG),
      cell(para("Infintor Solutions", { size: 20 }), 3600)
    ]}),
    new TableRow({ children: [
      cell(para("Date", { bold: true, size: 20 }), 2400, ALT_BG),
      cell(para("March 3, 2026", { size: 20 }), 3600)
    ]}),
    new TableRow({ children: [
      cell(para("Odoo Version", { bold: true, size: 20 }), 2400, ALT_BG),
      cell(para("19 (Enterprise)", { size: 20 }), 3600)
    ]}),
    new TableRow({ children: [
      cell(para("Total Questions", { bold: true, size: 20 }), 2400, ALT_BG),
      cell(para(`${qas.reduce((s, c) => s + c.questions.length, 0)} common scenarios`, { size: 20 }), 3600)
    ]})
  ]
}));

children.push(pageBreak());

// Table of contents header
children.push(heading("TABLE OF CONTENTS", HeadingLevel.HEADING_1));
children.push(spacer());

let qNum = 0;
qas.forEach((cat, ci) => {
  children.push(new Paragraph({
    spacing: { after: 80, before: 120 },
    children: [new TextRun({ text: `Section ${ci + 1}:  ${cat.category}`, font: "Arial", size: 24, bold: true, color: "2E74B5" })]
  }));
  cat.questions.forEach(q => {
    qNum++;
    children.push(new Paragraph({
      spacing: { after: 40 },
      indent: { left: 450 },
      children: [
        new TextRun({ text: `Q${qNum}. `, font: "Arial", size: 20, bold: true, color: "555555" }),
        new TextRun({ text: q.q, font: "Arial", size: 20, color: "555555" })
      ]
    }));
  });
});

children.push(pageBreak());

// ── Each category ──
qNum = 0;
qas.forEach((cat, ci) => {
  if (ci > 0) children.push(pageBreak());

  // Category heading
  children.push(new Paragraph({
    spacing: { before: 200, after: 200 },
    children: [
      new TextRun({ text: `SECTION ${ci + 1}`, font: "Arial", size: 22, color: "2E74B5", bold: true }),
    ]
  }));
  children.push(heading(cat.category, HeadingLevel.HEADING_1));

  cat.questions.forEach((q, qi) => {
    qNum++;
    if (qi > 0) children.push(spacer());

    // Question box
    children.push(new Table({
      width: { size: 9360, type: WidthType.DXA },
      columnWidths: [9360],
      rows: [new TableRow({ children: [new TableCell({
        borders: { top: { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" }, bottom: border, left: border, right: border },
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: "EAF0F7", type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 150, right: 150 },
        children: [
          new Paragraph({ children: [
            new TextRun({ text: `Q${qNum}. `, font: "Arial", size: 24, bold: true, color: "2E74B5" }),
            new TextRun({ text: q.q, font: "Arial", size: 24, bold: true, color: "333333" })
          ]}),
        ]
      })] })]
    }));

    // Real-life scenario
    children.push(spacer());
    children.push(new Paragraph({
      spacing: { after: 60 },
      children: [
        new TextRun({ text: "📋 Real-Life Scenario:  ", font: "Arial", size: 22, bold: true, color: "6A1B9A" }),
        new TextRun({ text: q.realLife, font: "Arial", size: 22, italics: true, color: "555555" })
      ]
    }));

    // Steps
    children.push(new Paragraph({
      spacing: { before: 120, after: 80 },
      children: [new TextRun({ text: "How to do it in Odoo:", font: "Arial", size: 22, bold: true, color: "1B5E20" })]
    }));

    q.steps.forEach((s, si) => {
      children.push(new Paragraph({
        spacing: { after: 60 },
        indent: { left: 360 },
        children: [
          new TextRun({ text: `${si + 1}.  `, font: "Arial", size: 22, bold: true, color: "2E74B5" }),
          new TextRun({ text: s, font: "Arial", size: 22, color: "333333" })
        ]
      }));
    });

    // Tip box
    if (q.tip) {
      children.push(spacer());
      children.push(tipBox("💡 Pro Tip:", q.tip, TIP_BG));
    }

    children.push(spacer());
    // Separator line
    children.push(new Paragraph({
      spacing: { before: 100, after: 100 },
      borders: { bottom: { style: BorderStyle.SINGLE, size: 1, color: "DDDDDD" } },
      children: []
    }));
  });
});

// ── Quick Reference Card (last page) ──
children.push(pageBreak());
children.push(heading("QUICK REFERENCE CARD", HeadingLevel.HEADING_1));
children.push(para("Pin this page near your workstation for daily use.", { italic: true, color: "777777" }));
children.push(spacer());

const refData = [
  ["Switch Branch", "Click company name (top-right) → uncheck all → check only the branch you want"],
  ["Create Sale Order", "Sales → Orders → Create → Add customer & products → Confirm"],
  ["Create Invoice from SO", "Open confirmed SO → Create Invoice → Confirm"],
  ["Record Customer Payment", "Open invoice → Register Payment → Select bank → Create Payment"],
  ["Create Purchase Order", "Purchase → Orders → Create → Add vendor & products → Confirm"],
  ["Enter Vendor Bill", "Open confirmed PO → Create Bill → Enter vendor's bill number → Confirm"],
  ["Pay Vendor", "Open posted bill → Register Payment → Select bank → Create Payment"],
  ["Check Unpaid Invoices", "Accounting → Reporting → Aged Receivable"],
  ["Check Unpaid Bills", "Accounting → Reporting → Aged Payable"],
  ["View Branch P&L", "Switch to branch → Accounting → Reporting → Profit & Loss"],
  ["Check Stock", "Inventory → Products → search product → see On Hand qty"],
  ["Add New Customer", "Sales → Customers → Create → Fill details → Save"],
  ["Reconcile Bank", "Accounting → Bank → Select journal → Match & Validate entries"],
  ["Lock Financial Year", "Accounting → Settings → Lock Date → set to 31-Mar"],
  ["Credit Note (Refund)", "Open posted invoice → Add Credit Note → Confirm"],
];

const refRows = [
  new TableRow({ children: [
    headerCell("ACTION", 3000),
    headerCell("STEPS IN ODOO", 6360),
  ]})
];
refData.forEach((r, i) => {
  const bg = i % 2 === 0 ? WHITE : ALT_BG;
  refRows.push(new TableRow({ children: [
    cell(para(r[0], { bold: true, size: 20 }), 3000, bg),
    cell(para(r[1], { size: 20 }), 6360, bg),
  ]}));
});

children.push(new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3000, 6360],
  rows: refRows
}));

children.push(spacer());
children.push(tipBox("📌 Remember:", "ALWAYS check the Company Selector (top-right corner) before doing anything in Odoo. The wrong company selected = wrong data shown.", WARN_BG));

// ── Footer section: important contacts ──
children.push(spacer());
children.push(spacer());
children.push(new Paragraph({
  spacing: { before: 200 },
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "— End of Document —", font: "Arial", size: 20, color: "999999", italics: true })]
}));

// ── Create Document ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "2E74B5" },
        paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "333333" },
        paragraph: { spacing: { before: 180, after: 150 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "Client Q&A Guide — Krishnadas Group | Odoo 19", font: "Arial", size: 16, color: "999999", italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          children: [
            new TextRun({ text: "Prepared by Infintor Solutions", font: "Arial", size: 16, color: "999999" }),
            new TextRun({ children: ["\tPage "], font: "Arial", size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" }),
          ]
        })]
      })
    },
    children
  }]
});

const outPath = "My learnings/Rohan_Documentation/Client_QA_Guide_Multi_Company_Odoo19.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log(`✓ Generated: ${outPath} (${(buffer.length / 1024).toFixed(1)} KB)`);
  console.log(`  Total sections: ${qas.length}`);
  console.log(`  Total questions: ${qas.reduce((s, c) => s + c.questions.length, 0)}`);
});
