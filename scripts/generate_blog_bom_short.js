const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat
} = require("docx");

// ─── Shared style config ───
const FONT = "Arial";
const PAGE_WIDTH = 12240;
const MARGINS = { top: 1440, right: 1440, bottom: 1440, left: 1440 };
const BRAND_COLOR = "1B4F72";
const ACCENT_COLOR = "D5E8F0";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function makeDoc(title, author, date, sections) {
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 22 } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: FONT, color: BRAND_COLOR }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: FONT, color: BRAND_COLOR }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: FONT, color: "2C3E50" }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
      ]
    },
    numbering: { config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]},
    sections: [{
      properties: { page: { size: { width: PAGE_WIDTH, height: 15840 }, margin: MARGINS } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Infintor Solutions", font: FONT, size: 18, color: "888888", italics: true })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [ new TextRun({ text: "Page ", font: FONT, size: 18, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" }) ] })] }) },
      children: [
        new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: title, bold: true, size: 36, font: FONT, color: BRAND_COLOR })] }),
        new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: `${author}  |  ${date}`, size: 20, font: FONT, color: "666666" })] }),
        ...sections
      ]
    }]
  });
}

function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] }); }
function p(text) {
  const runs = []; const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) { if (part.startsWith("**") && part.endsWith("**")) { runs.push(new TextRun({ text: part.slice(2,-2), bold: true, font: FONT, size: 22 })); } else { runs.push(new TextRun({ text: part, font: FONT, size: 22 })); } }
  return new Paragraph({ spacing: { after: 160 }, children: runs });
}
function bullet(text) {
  const runs = []; const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) { if (part.startsWith("**") && part.endsWith("**")) { runs.push(new TextRun({ text: part.slice(2,-2), bold: true, font: FONT, size: 22 })); } else { runs.push(new TextRun({ text: part, font: FONT, size: 22 })); } }
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: runs });
}
function numItem(text) {
  const runs = []; const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) { if (part.startsWith("**") && part.endsWith("**")) { runs.push(new TextRun({ text: part.slice(2,-2), bold: true, font: FONT, size: 22 })); } else { runs.push(new TextRun({ text: part, font: FONT, size: 22 })); } }
  return new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 }, children: runs });
}
function nav(t) { return new Paragraph({ spacing: { after: 120 }, shading: { fill: "F5F5F5", type: ShadingType.CLEAR }, children: [new TextRun({ text: t, font: FONT, size: 22, italics: true })] }); }
function imgPlaceholder(d) { return new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: `[Image: ${d}]`, font: FONT, size: 20, color: "999999", italics: true })] }); }
function spacer() { return new Paragraph({ spacing: { after: 80 }, children: [] }); }
function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a,b)=>a+b,0);
  const headerCells = headers.map((h,i)=>new TableCell({ borders, width:{size:colWidths[i],type:WidthType.DXA}, shading:{fill:BRAND_COLOR,type:ShadingType.CLEAR}, margins:{top:80,bottom:80,left:120,right:120}, children:[new Paragraph({children:[new TextRun({text:h,bold:true,font:FONT,size:20,color:"FFFFFF"})]})] }));
  const dataRows = rows.map(row=>new TableRow({ children:row.map((cell,i)=>new TableCell({ borders, width:{size:colWidths[i],type:WidthType.DXA}, margins:{top:60,bottom:60,left:120,right:120}, children:[new Paragraph({children:[new TextRun({text:cell,font:FONT,size:20})]})] })) }));
  return new Table({ width:{size:totalWidth,type:WidthType.DXA}, columnWidths:colWidths, rows:[new TableRow({children:headerCells}),...dataRows] });
}
function faqItem(num, question, answer) {
  return [ new Paragraph({ spacing:{before:200,after:80}, children:[new TextRun({text:`${num}. ${question}`,bold:true,font:FONT,size:22})] }), p(answer) ];
}
function cta(text) { return new Paragraph({ spacing:{before:300,after:200}, shading:{fill:ACCENT_COLOR,type:ShadingType.CLEAR}, children:[new TextRun({text,font:FONT,size:22,italics:true,color:BRAND_COLOR})] }); }


// ═══════════════════════════════════════════════════════════════
// SHORT BOM BLOG
// ═══════════════════════════════════════════════════════════════
const bomShortSections = [
  // SEO Metadata
  p("**SEO Title:** How to Configure Bill of Materials in Odoo 19"),
  p("**Meta Description:** Step-by-step guide to configuring a Bill of Materials (BOM) in Odoo 19 — types, components, operations, kits, and multi-level BOMs."),
  p("**URL Slug:** /configure-bill-of-materials-bom-odoo-19"),
  p("**Primary Keyword:** Bill of Materials in Odoo 19"),
  spacer(),

  // Introduction
  p("In Odoo 19, a **Bill of Materials (BOM)** defines the components, quantities, and operations required to manufacture a product. It is the blueprint that drives manufacturing orders, cost calculations, and procurement. This guide covers the essential steps to configure a BOM correctly."),

  // BOM Types
  h2("BOM Types"),
  p("Odoo 19 offers three BOM types, each serving a different purpose:"),
  bullet("**Manufacture this Product** — the standard type. Triggers a manufacturing order that consumes components and produces the finished goods."),
  bullet("**Kit** — does not trigger any manufacturing. When sold, Odoo breaks the kit into individual components on the delivery order. Useful for bundled or unassembled products."),
  bullet("**Subcontracting** — production is handled by an external vendor. Odoo tracks outgoing components and incoming finished goods."),

  // Creating a BOM
  h2("Creating a BOM"),
  nav("Manufacturing \u2192 Products \u2192 Bills of Materials \u2192 New"),
  p("You can also open any product form and click the **Bill of Materials** smart button. On the BOM form, set the **Product**, **Quantity** (units produced), and **BoM Type**."),
  imgPlaceholder("New BOM form in Odoo 19"),

  // Components
  h2("Adding Components"),
  p("In the **Components** tab, click **Add a line** to list the required raw materials. For each component, specify the product, quantity, and unit of measure."),
  p("Optional columns available via the settings icon:"),
  bullet("**Apply on Variants** — restrict the component to specific product variants"),
  bullet("**Consumed in Operation** — link the component to a specific production step"),
  bullet("**Manual Consumption** — require operators to manually confirm consumption"),

  // Operations
  h2("Adding Operations"),
  p("To use operations, first enable **Work Orders**:"),
  nav("Manufacturing \u2192 Configuration \u2192 Settings \u2192 Operations \u2192 tick Work Orders"),
  p("Then, on the BOM's **Operations** tab, click **Add a line** to define each production step. Key fields include the operation name, work center, duration computation method, and an optional work sheet (PDF, Google Slide, or text instructions)."),
  imgPlaceholder("Operations tab with work center and duration fields"),

  // By-Products
  h2("By-Products"),
  p("To track residual materials produced during manufacturing, enable the **By-Products** setting under Manufacturing \u2192 Configuration \u2192 Settings. Then use the **By-products** tab on the BOM to add each by-product with its quantity and the operation in which it is produced."),

  // Multi-Level BOMs
  h2("Multi-Level BOMs"),
  p("When a component is itself manufactured, Odoo supports **multi-level BOMs** — BOMs nested within other BOMs. Build from the bottom up: create the sub-assembly BOM first, then add that product as a component in the parent BOM."),
  p("For automated procurement, set reordering rules on sub-assembly products with minimum and maximum quantities both at zero. This triggers manufacturing only when demand arises."),

  // Miscellaneous
  h2("Key Miscellaneous Settings"),
  bullet("**Manufacturing Readiness** — start production when first-operation components are available, or wait for all components"),
  bullet("**Flexible Consumption** — allow, warn, or block deviations from BOM quantities"),
  bullet("**Manufacturing Lead Time** — days to complete a manufacturing order"),

  // FAQs
  h2("Frequently Asked Questions"),
  ...faqItem(1, "What is a Bill of Materials (BOM) in Odoo 19?", "A BOM defines the components, quantities, and operations needed to manufacture a product. Odoo uses it to generate manufacturing orders, calculate costs, and manage procurement."),
  ...faqItem(2, "What is the difference between a Kit BOM and a Manufacturing BOM?", "A Manufacturing BOM triggers a manufacturing order where components are consumed to produce a finished product. A Kit BOM does not trigger manufacturing \u2014 it breaks the product into individual components at delivery."),
  ...faqItem(3, "How do I add operations to a BOM?", "Enable Work Orders under Manufacturing \u2192 Configuration \u2192 Settings, then add operations in the BOM\u2019s Operations tab with the operation name, work center, and duration."),
  ...faqItem(4, "What is a multi-level BOM?", "A multi-level BOM nests sub-assembly BOMs within a parent BOM. Use it when your finished product contains components that are themselves manufactured."),
  ...faqItem(5, "How does Odoo calculate product cost from a BOM?", "Odoo sums the purchase cost of all components plus the cost of operations (work center hourly rate multiplied by duration) to calculate the total manufacturing cost."),
  ...faqItem(6, "Where do I find BOM configuration in Odoo 19?", "Navigate to Manufacturing \u2192 Products \u2192 Bills of Materials, or click the Bill of Materials smart button on any product form."),

  // Conclusion
  h2("Conclusion"),
  p("A correctly configured BOM is the foundation of manufacturing in Odoo 19. It drives production, costing, and procurement across your entire supply chain. Whether you are manufacturing in-house, selling kits, or outsourcing to subcontractors, the BOM is where it all begins."),

  cta("Infintor Solutions is an Official Odoo Partner in India. Need help setting up your manufacturing operations in Odoo 19? Contact our consultants for expert BOM configuration and MRP implementation. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════
// Generate DOCX
// ═══════════════════════════════════════════
const OUT_PATH = path.join(__dirname, "..", "My learnings", "Blogs InDevelopment", "BLOG_BOM_Configuration_Short_Odoo_19.docx");

async function main() {
  const doc = makeDoc(
    "How to Configure Bill of Materials (BOM) in Odoo",
    "Rohan Raj  |  Infintor Solutions",
    "Mar 24, 2026",
    bomShortSections
  );
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(OUT_PATH, buf);
  console.log(`Created: ${OUT_PATH}  (${(buf.length / 1024).toFixed(0)} KB)`);
}

main().catch(err => { console.error(err); process.exit(1); });
