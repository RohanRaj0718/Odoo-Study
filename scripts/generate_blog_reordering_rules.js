const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat
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
        page: { size: { width: PAGE_WIDTH, height: 15840 }, margin: MARGINS }
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

function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] }); }
function h3(text) { return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] }); }

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
// BLOG CONTENT
// ═══════════════════════════════════════════════════════════════
const blogSections = [
  p("Inventory management is a delicate balancing act. Stock too much, and you tie up valuable working capital in warehouse space. Stock too little, and you face stockouts, delayed sales, and frustrated customers. Finding the middle ground requires intelligent automation rather than manual guesswork."),
  p("This is where **Odoo 19 Reordering Rules** (also known as minimum stock setup) become an invaluable tool for businesses. Whether you are managing raw materials for manufacturing or finished goods for eCommerce, reordering rules ensure that your inventory levels automatically replenish themselves when they dip below a certain threshold. By leveraging this feature, supply chain managers can confidently adopt a \u201cset it and forget it\u201d methodology for their most critical inventory items."),
  p("In this comprehensive guide, we will break down exactly how to configure minimum stock rules in Odoo 19, clarify the important distinction between automatic and manual triggers, and highlight the latest updates from Odoo 19.1 that simplify the replenishment process. Let\u2019s dive into optimizing your warehouse flow with Odoo ERP Implementation Services."),

  h2("What Are Reordering Rules in Odoo 19?"),
  p("A **Reordering Rule** in Odoo is an automated safeguard designed to keep your forecasted stock levels within a target window. It relies on two fundamental metrics:"),
  bullet("**Minimum Quantity (Min):** The lower threshold. When your forecasted stock drops below this number, Odoo recognizes that it is time to order more."),
  bullet("**Maximum Quantity (Max):** The upper threshold. When Odoo triggers a replenishment order, it calculates exactly how many units are needed to bring your stock back up to this maximum limit."),
  p("For example, if you sell office chairs and set your Min to 10 and Max to 50, Odoo will patiently wait. If a customer buys 15 chairs, dropping your forecasted stock to 8 (which is below the Min of 10), Odoo will prompt you to purchase 42 more chairs to hit your Max of 50 perfectly."),

  h2("Understanding Automatic vs. Manual Triggers in Odoo 19"),
  p("One of the most common points of confusion for new Odoo users is wondering why Purchase Orders (POs) aren't generating instantly when stock drops. The answer lies in the **Trigger** setting of the reordering rule."),
  p("In Odoo 19, reordering rules can be executed either automatically by the system scheduler or manually by the purchasing manager. By default, the Trigger column is hidden to keep the interface clean, but you can enable it from the settings icon on the Replenishment dashboard."),

  h3("Automatic Trigger"),
  p("When a rule is set to **Auto**, Odoo operates silently in the background. If a confirmed Sales Order causes your forecasted inventory to dip below the minimum quantity, Odoo will instantly and automatically generate a draft Request for Quotation (RFQ) to your default vendor. Alternatively, if it is a manufactured product, Odoo generates a Manufacturing Order (MO). Auto triggers are perfect for cheap, high-velocity goods where immediate restocking is preferred over manual purchase reviews."),

  h3("Manual Trigger"),
  p("When a rule is set to **Manual**, Odoo does not create a PO or MO automatically. Instead, it places the product onto the centralized **Replenishment Report**. This dashboard acts as a \u201cto-do list\u201d for your procurement team. Managers can review all suggested reorders, consolidate them, adjust quantities, or delay them based on cash flow before clicking the \u201cOrder\u201d button. This is ideal for expensive items or bulk goods where procurement benefits from human oversight."),
  imgPlaceholder("Odoo 19 Replenishment Report showing Manual Reordering Rules waiting for approval"),

  h2("Step-by-Step Configuration of Minimum Stock Rules"),
  p("Setting up an effective Reordering Rule requires configuring the underlying product first. Without the correct prerequisite settings, the rule will silently fail."),

  h3("1. Configuring the Product"),
  numItem("Navigate to the **Inventory** app and open **Products -> Products**."),
  numItem("Select the product you want to automate."),
  numItem("Under the **General Information** tab, set the Product Type to **Goods** (Storable Product)."),
  numItem("Check the **Track Inventory** checkbox so Odoo actively counts the product."),
  numItem("Switch to the **Purchase** tab and add at least one **Vendor**. If Odoo doesn't know who to buy from, it cannot generate an RFQ."),
  p("If the item is manufactured rather than purchased, ensure a valid **Bill of Materials (BoM)** is linked via the top smart button instead of setting a vendor."),

  h3("2. Creating the Reordering Rule"),
  nav("Inventory -> Products -> Products -> [Select Product] -> Reordering Rules Smart Button"),
  p("Once on the Reordering Rules list for the product, click **New** and fill in the following:"),
  bullet("**Location:** Choose the warehouse or specific shelf where the stock will be received."),
  bullet("**Min Quantity:** Enter your reorder point. Consider supplier lead times when setting this (e.g., if it takes 5 days to arrive and you sell 2 a day, your Min should be at least 10)."),
  bullet("**Max Quantity:** Enter the replenishment target."),
  bullet("**Multiple Quantity:** Optional. If your vendor only sells in batches of 12, enter 12 here. Odoo will round up the PO quantity to accommodate this packing constraint."),

  h3("3. Setting the Preferred Replenishment Route"),
  p("Odoo needs to know *how* to acquire this stock. From the Replenishment dashboard, you can reveal the **Route** column by clicking the configuration icon on the far right. Select whether this rule should default to **Buy** (triggering POs) or **Manufacture** (triggering MOs)."),
  imgPlaceholder("Setting the Preferred Route to Buy against the Minimum Quantity of 15"),

  h2("New Update in Odoo 19.1: The Simplified Order Route"),
  p("For businesses using Odoo Support Services to stay updated on the latest sub-versions, Odoo 19.1 introduced a major quality-of-life improvement. Previously, users had to choose between clicking \u201cOrder\u201d or \u201cOrder to Max\u201d on manual rules, which often caused confusion."),
  p("In Odoo 19.1, these options have been merged into a single, intuitive **\u201cOrder\u201d** action. The system now autonomously calculates the required quantity to hit the maximum stock, vastly reducing configuration errors and simplifying procurement training for new staff."),

  h2("How Odoo Calculates Forecasted Stock"),
  p("It's vital for Odoo Consulting Partners to emphasize that Reordering Rules trigger based on **Forecasted Stock**, not just On-Hand stock. The formula is:"),
  p("**Forecasted Stock = On-Hand Stock - Outgoing Deliveries (Reserved) + Incoming Receipts**"),
  p("This mathematical approach prevents duplicate ordering. If you have 5 items on hand, a minimum of 10, but you already placed a PO yesterday for 20 items (Incoming Receipt), Odoo knows your forecasted stock is actually 25. Therefore, it will wisely prevent another reordering rule from triggering."),

  h2("Why Choose Infintor Solutions?"),
  p("Automating procurement is just the beginning. Setting up proper Reordering Rules ensures that your operations scale seamlessly, but getting the nuances right\u2014like Horizon Days, Multiple Quantities, and Procurement Groups\u2014requires expert configuration."),
  p("As an Official Odoo Partner in India, Infintor Solutions provides end-to-end Odoo ERP Customization Services, Implementation, and Training. We help businesses transition away from spreadsheets into fully automated, intelligent supply chains."),

  h2("Conclusion"),
  p("Odoo 19 Reordering Rules serve as the backbone for modern inventory management. By establishing clear minimum and maximum thresholds, designating preferred routes, and leveraging either manual reporting or automatic background triggers, businesses eliminate the risk of stockouts while optimizing their capital. With the updated usability of Odoo 19.1, configuring these rules is easier and more reliable than ever before."),

  h2("Frequently Asked Questions"),
  ...faqItem(1, "Why is my Reordering Rule not creating a Purchase Order?", "The most common reason is missing vendor data. Odoo cannot generate a Purchase Order if there is no Vendor assigned under the Purchase tab of the product. Additionally, ensure the scheduler has run, or the trigger is set to 'Auto' instead of 'Manual'."),
  ...faqItem(2, "What is the difference between Min Quantity and Max Quantity?", "Min Quantity is the baseline trigger. The rule only activates when your forecasted stock falls below this number. Max Quantity is the goal. Odoo calculates how many items to order by subtracting your current stock from the Max Quantity."),
  ...faqItem(3, "Does Odoo look at On-Hand stock or Forecasted stock for reordering?", "Odoo exclusively uses Forecasted Stock. This accounts for unfulfilled sales reservations and incoming shipments, essentially preventing the system from over-ordering goods that are already in transit."),
  ...faqItem(4, "How do I find the 'Trigger' and 'Route' columns in Odoo 19?", "Navigate to Inventory \u2192 Operations \u2192 Replenishment. These columns are hidden by default. Click the 'adjust settings' icon (sliders) on the far-right of the column headers and tick 'Trigger' and 'Route' to reveal them."),
  ...faqItem(5, "Can I set reordering rules for manufactured products?", "Yes. Ensure the product has at least one associated Bill of Materials (BoM). When configuring the reordering rule, set the Route to 'Manufacture', and Odoo will generate Manufacturing Orders instead of Purchase Orders."),
  ...faqItem(6, "What is the 0/0/1 Reordering Rule?", "The 0/0/1 rule sets the Min and Max to 0, and the 'To Order' to 1. This special rule is used to automatically purchase or manufacture a product exactly when a Sales Order is confirmed, akin to Replenish on Order (MTO), but without strictly reserving the incoming stock for that specific order."),

  cta("Ready to automate your supply chain with Odoo 19 Reordering Rules? Connecting with an experienced ERP Implementation Partner ensures your inventory works flawlessly. Reach out to Infintor Solutions today in India, Dubai, or Germany for expert Odoo Development Services. \u2192 infintor.com/contactus")
];

// ═══════════════════════════════════════════
// Generate DOCX
// ═══════════════════════════════════════════
const OUT_DIR = "C:/Odoo Study/My learnings/Blogs InDevelopment";

async function main() {
  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  const blogFile = `${OUT_DIR}/BLOG_Reordering_Rules_Odoo_19.docx`;
  const doc = makeDoc(
    "How to Set Up Reordering Rules & Minimum Stock in Odoo 19", 
    "Rohan Raj  |  Infintor Solutions", 
    "Mar 17, 2026", 
    blogSections
  );
  
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(blogFile, buf);
  console.log(`Successfully generated DOCX: ${blogFile} (${(buf.length / 1024).toFixed(0)} KB)`);
}

main().catch(err => { console.error(err); process.exit(1); });
