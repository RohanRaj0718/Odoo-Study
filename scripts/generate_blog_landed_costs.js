const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat, ExternalHyperlink
} = require("docx");

// ─── Shared style config ───
const FONT = "Arial";
const PAGE_WIDTH = 12240;
const MARGINS = { top: 1440, right: 1440, bottom: 1440, left: 1440 };
const CONTENT_WIDTH = PAGE_WIDTH - MARGINS.left - MARGINS.right;
const BRAND_COLOR = "1B4F72";
const ACCENT_COLOR = "D5E8F0";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function makeDoc(title, author, date, sections) {
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 22 } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, font: FONT, color: BRAND_COLOR },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: FONT, color: BRAND_COLOR },
          paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: "2C3E50" },
          paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
        },
      ]
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        },
        {
          reference: "numbers",
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        },
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: 15840 },
          margin: MARGINS
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "Infintor Solutions", font: FONT, size: 18, color: "888888", italics: true })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: FONT, size: 18, color: "888888" }),
              new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" }),
            ]
          })]
        })
      },
      children: [
        new Paragraph({
          spacing: { after: 80 },
          children: [new TextRun({ text: title, bold: true, size: 36, font: FONT, color: BRAND_COLOR })]
        }),
        new Paragraph({
          spacing: { after: 400 },
          children: [new TextRun({ text: `${author}  |  ${date}`, size: 20, font: FONT, color: "666666" })]
        }),
        ...sections
      ]
    }]
  });
}

function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}

function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] });
}

function p(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ spacing: { after: 160 }, children: runs });
}

function bullet(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: runs });
}

function numItem(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 }, children: runs });
}

function nav(text) {
  return new Paragraph({
    spacing: { after: 120 },
    shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: FONT, size: 22, italics: true })]
  });
}

function imgPlaceholder(desc) {
  return new Paragraph({
    spacing: { before: 120, after: 200 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `[Image: ${desc}]`, font: FONT, size: 20, color: "999999", italics: true })]
  });
}

function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerCells = headers.map((h, i) => new TableCell({
    borders,
    width: { size: colWidths[i], type: WidthType.DXA },
    shading: { fill: BRAND_COLOR, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, font: FONT, size: 20, color: "FFFFFF" })] })]
  }));
  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: cell, font: FONT, size: 20 })] })]
    }))
  }));
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [new TableRow({ children: headerCells }), ...dataRows]
  });
}

function spacer() {
  return new Paragraph({ spacing: { after: 80 }, children: [] });
}

function faqItem(num, question, answer) {
  return [
    new Paragraph({
      spacing: { before: 200, after: 80 },
      children: [new TextRun({ text: `${num}. ${question}`, bold: true, font: FONT, size: 22 })]
    }),
    p(answer)
  ];
}

function cta(text) {
  return new Paragraph({
    spacing: { before: 300, after: 200 },
    shading: { fill: ACCENT_COLOR, type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: FONT, size: 22, italics: true, color: BRAND_COLOR })]
  });
}

// ═══════════════════════════════════════════════════════════════
// BLOG: Landed Cost Calculation in Odoo 19
// ═══════════════════════════════════════════════════════════════

// SEO Metadata (for reference):
// SEO Title: Landed Cost Calculation in Odoo 19 — Full Guide
// Meta Description: Learn how to calculate and allocate landed costs in Odoo 19. Step-by-step guide covering setup, split methods, AVCO, FIFO, and vendor bill integration.
// URL Slug: landed-cost-calculation-odoo-19
// Primary Keyword: landed cost calculation in Odoo 19
// Supporting Keywords: Odoo inventory valuation, AVCO costing Odoo, FIFO inventory Odoo, Odoo vendor bill landed cost, Odoo import duty calculation, Odoo 19 costing methods, Odoo landed cost split method, Odoo ERP inventory management India

const landedCostSections = [

  // ── Introduction ──
  p("Every product your business imports or procures carries more than just a purchase price. Freight charges, customs duties, insurance premiums, port handling fees, and inland transportation costs are all part of the true cost of getting a product onto your warehouse shelf. Businesses that ignore these additional expenses miscalculate their product costs, understate inventory value, and erode profit margins without understanding why."),
  p("This is precisely where **landed cost calculation in Odoo 19** becomes essential. The Landed Costs feature in Odoo allows businesses to integrate all post-purchase expenses directly into the inventory valuation of received goods. Rather than treating freight or customs duty as a separate overhead entry, Odoo calculates exactly how much of that cost belongs to each product in a shipment and updates the inventory value accordingly."),
  p("For businesses operating in India, where import duty structures, GST, and freight costs significantly affect product profitability, accurate landed cost allocation is not a luxury — it is a compliance and business intelligence requirement. This guide walks through the complete landed cost configuration and workflow in Odoo 19, from initial setup to the journal entry that confirms the cost has been posted to accounting."),

  // ── What Are Landed Costs ──
  h2("What Are Landed Costs? Understanding the Business Problem"),
  p("A **landed cost** is any expense incurred to bring a product from the supplier's location to your warehouse or point of use, beyond the agreed purchase price. These costs do not directly appear on the supplier's product invoice but are incurred during the logistics chain and must be absorbed into the product's total cost."),
  p("Common landed cost components include:"),
  bullet("**Freight charges**: Ocean freight, air freight, or road transport fees"),
  bullet("**Customs and import duties**: Tariffs levied by the government on imported goods"),
  bullet("**Insurance**: Coverage for goods during transit"),
  bullet("**Port and handling fees**: Charges at the port of entry or destination warehouse"),
  bullet("**Inspection and compliance costs**: Mandatory inspections or certifications required at customs"),
  p("When these costs are not allocated to the products they apply to, several problems emerge: inventory is undervalued on the balance sheet, cost of goods sold is understated, and gross margin calculations are misleading. Businesses end up pricing products based on incorrect costs, leading to margin erosion over time."),
  p("Odoo 19 solves this by allowing businesses to create landed cost records linked to validated incoming receipts. Once validated, Odoo automatically distributes the additional cost across all products in the shipment using a configurable split method and updates the inventory valuation in real time."),

  // ── Configuration ──
  h2("Step 1: Enabling the Landed Costs Feature in Odoo 19"),
  p("The Landed Costs feature is not enabled by default. It must be activated in the Inventory application settings before it can be used."),
  nav("Inventory app \u2192 Configuration \u2192 Settings \u2192 Valuation section"),
  numItem("Navigate to **Inventory app \u2192 Configuration \u2192 Settings**"),
  numItem("Scroll to the **Valuation** section"),
  numItem("Tick the checkbox next to **Landed Costs**"),
  numItem("Click **Save**"),
  p("Once the page refreshes, a new **Default Journal** field appears directly below the Landed Costs option. Click the dropdown and select the accounting journal where all landed cost entries should be recorded. This is typically a dedicated freight or import expense journal, though the Stock Valuation journal is also commonly used."),
  imgPlaceholder("Inventory Settings page showing the Landed Costs checkbox enabled and Default Journal field visible"),

  h3("Prerequisite: Correct Costing Method"),
  p("Landed costs in Odoo 19 are only compatible with products configured for automated inventory valuation using either the **Average Cost (AVCO)** or **First In First Out (FIFO)** costing method. Standard costing does not support landed costs because costs are set manually rather than derived from actual purchases."),
  p("To verify or configure the costing method, navigate to the product category:"),
  nav("Inventory app \u2192 Configuration \u2192 Product Categories"),
  p("Select the relevant category and set **Costing Method** to AVCO or FIFO, and **Inventory Valuation** to Automated. This configuration is a mandatory prerequisite before landed costs can be applied to any product in that category."),

  // ── Create Landed Cost Product ──
  h2("Step 2: Creating a Landed Cost Product"),
  p("For recurring charges such as a regular freight provider or a fixed customs brokerage fee, Odoo recommends creating dedicated **landed cost products**. These are service-type products that represent the additional cost. Once configured, they can be quickly added to vendor bills or request for quotations (RfQs) without manual entry every time."),
  nav("Inventory app \u2192 Products \u2192 Products \u2192 New"),
  numItem("Enter a descriptive **Product Name** (e.g., \u201cInternational Freight\u201d or \u201cCustoms Duty\u201d)"),
  numItem("Set **Product Type** to **Service** \u2014 this is mandatory. Landed cost products must be service type"),
  numItem("Click the **Purchase** tab"),
  numItem("Tick the checkbox next to **Is a Landed Cost** in the Vendor Bills section"),
  numItem("Select a **Default Split Method** from the dropdown"),
  numItem("Save the product"),
  imgPlaceholder("Product form showing Service type selected and Is a Landed Cost checkbox ticked in the Purchase tab"),

  h3("Understanding the Five Split Methods"),
  p("The split method determines how the landed cost is distributed across the products in the incoming shipment. Odoo 19 offers five allocation methods:"),
  spacer(),
  makeTable(
    ["Split Method", "How Cost Is Distributed", "Best Used When"],
    [
      ["Equal", "Cost is divided equally among all distinct products in the receipt, regardless of quantity", "All items in the shipment have similar size and value"],
      ["By Quantity", "Cost is divided based on the total number of units of each product", "Freight is typically volume or count-based"],
      ["By Current Cost", "Cost is allocated proportionally to each product\u2019s existing unit cost", "Higher-value items should absorb more of the cost"],
      ["By Weight", "Cost is distributed based on the weight of products in the receipt", "Freight is weight-based (e.g., ocean or air freight per kg)"],
      ["By Volume", "Cost is distributed based on the volume of products", "Freight is charged by cubic meter or dimensional weight"],
    ],
    [2340, 3900, 3120]
  ),
  spacer(),
  p("Selecting the right split method is critical to producing accurate product cost calculations. For most import scenarios, **By Weight** or **By Quantity** are the most defensible methods for freight allocation, while **By Current Cost** is appropriate for insurance or duty calculations that are often proportional to declared value."),
  p("The default split method set on the landed cost product serves as the starting point, but it can be changed on each individual landed cost record before validation."),

  // ── Purchase Order ──
  h2("Step 3: Creating and Receiving a Purchase Order"),
  p("Landed costs are applied to validated incoming transfers \u2014 goods that have already been received into the warehouse. The process therefore begins with a standard purchase order."),
  nav("Purchase app \u2192 New"),
  numItem("Select the **Vendor** and add the products to be ordered under the **Products** tab"),
  numItem("Click **Confirm Order** to convert the RfQ into a confirmed Purchase Order"),
  numItem("When goods arrive, click **Receive Products**"),
  numItem("On the receipt form, verify quantities and click **Validate**"),
  p("Once the receipt is validated, it becomes an eligible transfer for landed cost application. Only validated transfers can be linked to a landed cost record. If the receipt has not been validated, it will not appear in the Transfers dropdown on the landed cost form."),

  // ── Vendor Bill ──
  h2("Step 4: Adding Landed Costs on a Vendor Bill"),
  p("When the freight forwarder, customs broker, or logistics provider sends their invoice, Odoo allows the landed cost to be recorded directly on the vendor bill and linked to the incoming shipment in a single workflow."),

  h3("Creating the Vendor Bill"),
  numItem("Navigate to the confirmed Purchase Order in the **Purchase app**"),
  numItem("Click **Bill Matching** or upload the vendor\u2019s invoice to create a draft Vendor Bill"),
  numItem("Set the **Bill Date** using the calendar picker"),
  numItem("Click **Add a line** and add the landed cost product (e.g., \u201cInternational Freight\u201d)"),
  numItem("Click the **Save** icon to save the draft bill"),
  p("In the invoice line table, observe the **Landed Costs** column. The regular product line from the PO will have its checkbox unchecked, while the landed cost product line will have its checkbox automatically ticked. This distinction tells Odoo which lines should be treated as landed costs and which are standard product invoices."),
  imgPlaceholder("Vendor bill showing two lines: product line with Landed Costs checkbox unchecked, freight line with checkbox ticked"),

  h3("Creating the Landed Cost Record from the Bill"),
  p("With the landed cost product line saved on the vendor bill, a **Create Landed Costs** button appears at the top of the bill form. Clicking this button automatically generates a landed cost record, pre-filled with the freight product and amount from the bill. This eliminates duplicate data entry and ensures the landed cost amount matches the vendor invoice exactly."),
  imgPlaceholder("Create Landed Costs button highlighted at the top of the vendor bill form"),

  // ── Apply Landed Cost ──
  h2("Step 5: Applying and Validating the Landed Cost"),
  p("After clicking **Create Landed Costs**, Odoo opens the landed cost form. This is where the shipment is linked and the cost distribution is computed."),
  nav("Inventory app \u2192 Operations \u2192 Landed Costs (alternative path to create manually)"),

  h3("Linking the Transfer"),
  numItem("On the Landed Cost form, click the **Transfers** dropdown"),
  numItem("Select the validated incoming shipment receipt that this cost applies to"),
  p("Only validated receipts are selectable from this dropdown. If the wrong receipt is linked, the landed cost will be applied to the wrong batch of goods, distorting inventory valuation."),
  imgPlaceholder("Landed Cost form with the Transfers field showing a selected validated receipt"),

  h3("Computing the Distribution"),
  numItem("Review the landed cost product and amount in the **Additional Costs** tab"),
  numItem("Confirm or change the **Split Method** if needed"),
  numItem("Click **Compute** at the bottom of the form"),
  p("Clicking Compute triggers Odoo to calculate how the landed cost will be distributed across all products in the receipt. The **Valuation Adjustments** tab becomes populated with three key columns:"),
  bullet("**Original Value**: The cost of the product as recorded at the time of receipt"),
  bullet("**Additional Landed Cost**: The portion of the total landed cost allocated to this product line"),
  bullet("**New Value**: The sum of the original value and the additional landed cost, representing the updated inventory valuation"),
  imgPlaceholder("Valuation Adjustments tab showing Original Value, Additional Landed Cost, and New Value columns for each product"),
  p("Review the Valuation Adjustments tab carefully before validating. This is the final checkpoint to ensure the distribution looks correct before the entry is posted to accounting."),

  numItem("Once satisfied, click **Validate** to post the landed cost entry to the accounting journal"),
  p("Upon validation, Odoo creates a journal entry in the configured Default Journal. The entry debits the product\u2019s inventory account and credits the freight or expense account, reflecting the transfer of the landed cost into inventory value."),

  // ── View Journal Entry ──
  h2("Step 6: Reviewing the Accounting Journal Entry"),
  p("Every validated landed cost creates a corresponding journal entry in Odoo\u2019s Accounting module. This entry can be reviewed to confirm that the valuation adjustment has been correctly posted."),
  nav("Accounting app \u2192 Accounting \u2192 Journal Entries"),
  p("Locate the journal entry by its reference number (e.g., STJ/2025/XXXXX). Click into the entry to view the **Journal Items**, which will show the debit to the inventory account (increasing product value) and the credit to the freight or expense account (clearing the cost from the expense ledger into inventory)."),
  p("This audit trail is important for financial reconciliation, statutory audits, and month-end closing procedures. In India, where import duty and freight are treated differently for GST purposes, this journal entry also provides the supporting documentation required for tax compliance."),
  imgPlaceholder("Journal entry for landed cost showing debit to inventory account and credit to freight expense account"),

  // ── Odoo 19 Specific ──
  h2("Odoo 19 Behavior: Landed Costs and Partially Sold Stock"),
  p("One important behavior to understand in Odoo 19 is how the system handles landed cost application when some of the received goods have already been sold before the landed cost is posted. This is a common scenario in import businesses where the freight invoice arrives weeks after the goods have been received and partially dispatched."),
  p("In Odoo 19 with the **AVCO costing method**, when a landed cost is applied after some units have already been delivered to customers, Odoo allocates the landed cost only to the remaining units currently in stock. The portion of the landed cost that relates to already-sold units is not automatically transferred to the Cost of Goods Sold (COGS) account \u2014 it remains in the expense account until a manual journal adjustment is made."),
  p("The practical impact of this behavior is a temporary overstatement of gross profit on the Profit and Loss statement for the period in which goods were sold. To correct this, businesses have two options:"),
  bullet("**Operational control**: Apply all landed costs before releasing goods to sales orders. This is the cleanest approach but not always feasible in real-world import scenarios."),
  bullet("**Manual journal adjustment**: Post a manual entry to reclassify the expense portion attributed to delivered goods from the freight account to COGS. This maintains P&L accuracy without requiring system customisation."),
  p("For **FIFO costing**, a related challenge exists in multi-warehouse environments. If a lot is split across multiple warehouses and a landed cost is applied to a receipt in one warehouse, Odoo may update the valuation of the entire lot globally rather than isolating the cost to the specific warehouse where it was incurred. Businesses with complex warehouse structures should validate this behaviour in a test environment before going live."),

  // ── Comparison Table ──
  h2("Split Method Comparison: Choosing the Right Allocation"),
  spacer(),
  makeTable(
    ["Business Scenario", "Recommended Split Method", "Reason"],
    [
      ["Ocean freight invoice by weight (e.g., \u20b95,000 for 200 kg shipment)", "By Weight", "Cost is directly proportional to product weight"],
      ["Air freight invoice charged per unit carton", "By Quantity", "Each carton unit bears equal freight cost"],
      ["Insurance premium based on CIF value of goods", "By Current Cost", "Higher-value items carry higher insurance exposure"],
      ["Customs duty applied uniformly across product types", "Equal", "When duty rate is flat and product differentiation is minimal"],
      ["Freight charged by cubic meter (LCL shipment)", "By Volume", "Cost reflects dimensional volume, not weight or value"],
    ],
    [3744, 2496, 3120]
  ),
  spacer(),

  // ── Conclusion ──
  h2("Conclusion"),
  p("**Landed cost calculation in Odoo 19** transforms how businesses account for the true cost of their products. By allocating freight, customs duty, insurance, and handling fees directly to inventory valuation rather than treating them as generic overhead, businesses gain accurate product costs, reliable profit margin reporting, and defensible financial statements."),
  p("The key steps are straightforward: enable the Landed Costs feature in Inventory settings, configure a landed cost product with the appropriate split method, receive goods through a validated purchase order receipt, apply the landed cost through a vendor bill or manual record, compute the distribution, and validate to post the journal entry. Each step is designed to create a clean, auditable trail from purchase to valuation."),
  p("For businesses in India managing import-heavy supply chains, this feature directly addresses the challenge of integrating customs duty, port charges, and CHA fees into product cost without manual spreadsheet calculations or end-of-period adjustments. With Odoo 19, landed cost management becomes part of the standard procurement workflow rather than an afterthought."),

  // ── FAQs ──
  h2("Frequently Asked Questions"),
  ...faqItem(1, "Can landed costs be applied to products using Standard (fixed) costing in Odoo 19?", "No. Landed costs in Odoo 19 are only compatible with the Average Cost (AVCO) and First In First Out (FIFO) costing methods. Products in a category configured with Standard costing cannot have landed costs applied. The product category must have its Costing Method set to AVCO or FIFO, and Inventory Valuation set to Automated, before landed costs can be used."),
  ...faqItem(2, "What happens if I apply a landed cost after some products have already been sold (AVCO)?", "In Odoo 19 with AVCO costing, the landed cost is applied only to the quantity currently on hand. The portion of the cost that relates to units already sold and delivered is not automatically moved to Cost of Goods Sold (COGS). It remains in the freight or expense account. To correct this, a manual journal entry must be posted to reclassify the relevant expense portion to COGS, ensuring accurate Profit and Loss reporting."),
  ...faqItem(3, "Can I apply one landed cost record to multiple incoming shipments?", "Yes. On the Landed Cost form, the Transfers dropdown accepts multiple validated receipts. When multiple transfers are selected, Odoo distributes the landed cost across all products from all linked receipts based on the chosen split method. This is useful when a single freight invoice covers several separate incoming shipments from the same supplier."),
  ...faqItem(4, "Do I need to create a separate vendor bill for the freight provider to apply landed costs?", "Not necessarily. You can create a landed cost record independently by navigating to Inventory app \u2192 Operations \u2192 Landed Costs and clicking New. This allows you to enter the cost amount, select the split method, and link the transfer without creating a vendor bill. However, creating from a vendor bill is recommended because it maintains a direct financial link between the vendor's invoice and the inventory adjustment, which is important for accounts payable reconciliation and audits."),
  ...faqItem(5, "Can the split method be changed after the landed cost has been validated?", "No. Once a landed cost record is validated, it cannot be edited. If the wrong split method was used or an incorrect amount was entered, the standard correction procedure is to create a new landed cost record with a negative amount (using the same split method) to reverse the original entry, and then create a corrected landed cost record with the right details. Odoo 19 supports this reversal workflow to maintain audit-safe accounting."),
  ...faqItem(6, "Is the landed cost feature available in Odoo 19 Community Edition?", "Yes. The Landed Costs feature is available in both Odoo 19 Community and Enterprise editions. However, some advanced inventory valuation features \u2014 such as the real-time automated FIFO journal entries and certain reporting capabilities \u2014 are more comprehensive in the Enterprise edition. For businesses with complex costing requirements, Enterprise is recommended to access the full range of valuation and reporting tools."),

  cta("Infintor Solutions is an Official Odoo Partner in India, with expertise in Odoo ERP implementation across manufacturing, trading, and import businesses. If your business manages complex landed costs, multi-currency procurement, or import-heavy supply chains, our Odoo consultants can configure a costing setup that gives you accurate product costs and clean financial reporting from day one. \u2192 Contact us at infintor.com/contactus"),
];

// ═══════════════════════════════════════════
// Generate DOCX
// ═══════════════════════════════════════════
const OUT_DIR = "My learnings/Blogs InDevelopment";

async function main() {
  // Ensure output directory exists
  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  const doc = makeDoc(
    "Landed Cost Calculation in Odoo 19: A Complete Implementation Guide",
    "Rohan Raj  |  Infintor Solutions",
    "Mar 16, 2026",
    landedCostSections
  );

  const buf = await Packer.toBuffer(doc);
  const outFile = `${OUT_DIR}/BLOG_Landed_Cost_Calculation_Odoo_19.docx`;
  fs.writeFileSync(outFile, buf);
  console.log(`Created: ${outFile}  (${(buf.length / 1024).toFixed(0)} KB)`);
}

main().catch(err => { console.error(err); process.exit(1); });
