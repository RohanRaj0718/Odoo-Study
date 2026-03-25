const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType,
        PageNumber, PageBreak } = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: "FFFFFF" };
const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

const PAGE_WIDTH = 12240;
const MARGINS = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGINS; // 9360

function makeHeaderCell(text, width) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "2E4057", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, font: "Calibri", size: 22, color: "FFFFFF" })] })]
  });
}

function makeCell(text, width, opts = {}) {
  const runs = [];
  if (opts.bold) {
    runs.push(new TextRun({ text, bold: true, font: "Calibri", size: 22, color: opts.color || "333333" }));
  } else {
    runs.push(new TextRun({ text, font: "Calibri", size: 22, color: opts.color || "333333" }));
  }
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: runs })]
  });
}

function makeTable(headers, rows, colWidths) {
  const tableRows = [];
  // Header row
  tableRows.push(new TableRow({
    children: headers.map((h, i) => makeHeaderCell(h, colWidths[i]))
  }));
  // Data rows
  rows.forEach((row, ri) => {
    tableRows.push(new TableRow({
      children: row.map((cell, ci) => {
        if (typeof cell === "object") {
          return makeCell(cell.text, colWidths[ci], cell);
        }
        return makeCell(cell, colWidths[ci], { fill: ri % 2 === 0 ? "F5F7FA" : undefined });
      })
    }));
  });
  return new Table({
    width: { size: CONTENT_WIDTH, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: tableRows,
  });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, font: "Calibri", size: 32, color: "2E4057" })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, bold: true, font: "Calibri", size: 26, color: "3B6B8A" })]
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, bold: true, font: "Calibri", size: 24, color: "4A8FB5" })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, font: "Calibri", size: 22, color: opts.color || "333333", bold: opts.bold, italics: opts.italics })]
  });
}

function bulletItem(text, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Calibri", size: 22, color: "333333" })]
  });
}

function numberedItem(text, ref = "numbers", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Calibri", size: 22, color: "333333" })]
  });
}

function boldBullet(boldText, normalText, ref = "bullets", level = 0) {
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { before: 40, after: 40 },
    children: [
      new TextRun({ text: boldText, font: "Calibri", size: 22, color: "333333", bold: true }),
      new TextRun({ text: normalText, font: "Calibri", size: 22, color: "333333" }),
    ]
  });
}

function separator() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "D0D5DD", space: 1 } },
    children: []
  });
}

function emptyLine() {
  return new Paragraph({ spacing: { before: 40, after: 40 }, children: [] });
}

// ============ BUILD DOCUMENT ============

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Calibri", color: "2E4057" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Calibri", color: "3B6B8A" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Calibri", color: "4A8FB5" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ] },
      { reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbers2",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbers3",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbers4",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbers5",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbers6",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbersResupply",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "numbersResupply2",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
      { reference: "talkingPoints",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: 15840 },
        margin: { top: 1440, right: MARGINS, bottom: 1440, left: MARGINS }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E4057", space: 1 } },
          spacing: { after: 120 },
          children: [
            new TextRun({ text: "INFINTOR SOLUTIONS", font: "Calibri", size: 18, bold: true, color: "2E4057" }),
            new TextRun({ text: "  |  Client Meeting Notes  |  Krishnadas Group", font: "Calibri", size: 18, color: "888888" }),
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "D0D5DD", space: 1 } },
          children: [
            new TextRun({ text: "Confidential  |  Infintor Solutions  |  Page ", font: "Calibri", size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Calibri", size: 16, color: "999999" }),
          ]
        })]
      })
    },
    children: [
      // ===== TITLE PAGE =====
      emptyLine(), emptyLine(), emptyLine(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 600, after: 200 },
        children: [new TextRun({ text: "CLIENT MEETING BRIEF", font: "Calibri", size: 52, bold: true, color: "2E4057" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: "Krishnadas Group", font: "Calibri", size: 36, color: "3B6B8A" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 100, after: 100 },
        children: [new TextRun({ text: "Multi-Company & Branch Operations in Odoo 19", font: "Calibri", size: 26, color: "666666", italics: true })]
      }),
      separator(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text: "Date: March 3, 2026", font: "Calibri", size: 22, color: "666666" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 40, after: 40 },
        children: [new TextRun({ text: "Prepared by: Rohan Raj | Infintor Solutions", font: "Calibri", size: 22, color: "666666" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 40, after: 40 },
        children: [new TextRun({ text: "Database: client-cient.odoo.com (Odoo 19, saas-19.1+e)", font: "Calibri", size: 22, color: "666666" })]
      }),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 1: CURRENT SCENARIO =====
      heading1("1. CURRENT SCENARIO \u2014 What\u2019s Already Set Up"),
      
      heading2("1.1 Company Structure"),
      para("The Krishnadas Group database has 4 companies. Three are linked; one is standalone."),
      emptyLine(),
      makeTable(
        ["Company", "Type", "Parent", "Location"],
        [
          [{ text: "Krishnadas Group", bold: true }, "Parent Company", "\u2014 (Root)", "Pathanamthitta, Kerala"],
          ["Devika Furniture", "Branch", "Krishnadas Group", "Pathanamthitta"],
          ["KDESIGN INTERIOR", "Branch", "Krishnadas Group", "Kochi"],
          [{ text: "KDESIGN INTERIOR FURNISHING", color: "CC5500", bold: true }, { text: "Standalone", color: "CC5500", bold: true }, { text: "None (No Parent!)", color: "CC5500", bold: true }, "Pathanamthitta"],
        ],
        [2800, 1800, 2400, 2360]
      ),
      emptyLine(),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u26A0 Key Observation: ", font: "Calibri", size: 22, bold: true, color: "856404" }),
          new TextRun({ text: "KDESIGN INTERIOR FURNISHING is NOT a branch \u2014 it\u2019s a separate company with no parent. This affects how stock transfers work. Discuss with client if this is intentional.", font: "Calibri", size: 22, color: "856404" }),
        ]
      }),

      heading2("1.2 Warehouse Map"),
      makeTable(
        ["Company", "Warehouses", "Short Code"],
        [
          [{ text: "Krishnadas Group", bold: true }, "Main Warehouse", "WH"],
          ["Krishnadas Group", "Near Home GF", "NH GF"],
          ["Krishnadas Group", "Near Home FF", "NH FF"],
          ["Krishnadas Group", "Factory Building", "FB"],
          [{ text: "Devika Furniture", bold: true }, "Showroom", "DF"],
          ["Devika Furniture", "Test Branch WH", "TBW"],
          [{ text: "KDESIGN INTERIOR", bold: true }, "Kochi Location", "KDI"],
          [{ text: "KDESIGN INT. FURNISHING", bold: true }, "kd warehouse", "kd"],
        ],
        [3200, 3800, 2360]
      ),
      emptyLine(),
      para("Total: 4 companies, 8 warehouses across 2 cities (Pathanamthitta & Kochi)."),

      heading2("1.3 What\u2019s Already Working"),
      boldBullet("Auto-resupply routes: ", "NH GF and NH FF automatically pull stock from Krishnadas Group main WH."),
      boldBullet("Internal transfers: ", "WH/Stock \u2192 NH GF/Stock (1 completed, 1 draft)."),
      boldBullet("Inter-company transfers: ", "Krishnadas \u2192 Devika Furniture and Krishnadas \u2192 KDESIGN INT. FURNISHING via transit location (completed)."),
      boldBullet("Purchase orders: ", "Active POs across all 4 companies with local vendors."),
      boldBullet("Inter-company Purchase: ", "P00006 \u2014 KDESIGN INT. FURNISHING buying from Krishnadas Group (inter-company link)."),
      boldBullet("Sales orders: ", "Active SOs from Devika Furniture Showroom, KDESIGN INTERIOR Kochi, and KDESIGN INT. FURNISHING."),

      heading2("1.4 What\u2019s NOT Configured Yet"),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: "\u274C Inter-company rules ", font: "Calibri", size: 22, bold: true, color: "DC3545" }),
          new TextRun({ text: "\u2014 No automatic SO/PO generation between companies.", font: "Calibri", size: 22, color: "333333" }),
        ]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: "\u274C Product tracking ", font: "Calibri", size: 22, bold: true, color: "DC3545" }),
          new TextRun({ text: "\u2014 ALL products are consumable with tracking = none. No lot/serial numbers.", font: "Calibri", size: 22, color: "333333" }),
        ]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: "\u274C Cross-company resupply ", font: "Calibri", size: 22, bold: true, color: "DC3545" }),
          new TextRun({ text: "\u2014 Only intra-company (within Krishnadas Group) routes exist. No auto-resupply to branches.", font: "Calibri", size: 22, color: "333333" }),
        ]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { before: 40, after: 40 },
        children: [
          new TextRun({ text: "\u274C User roles ", font: "Calibri", size: 22, bold: true, color: "DC3545" }),
          new TextRun({ text: "\u2014 Only 1 admin user (Rohan Raj). No branch-specific users yet.", font: "Calibri", size: 22, color: "333333" }),
        ]
      }),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 2: SCENARIOS =====
      heading1("2. TRANSFER SCENARIOS \u2014 How Stock Moves"),

      // --- SCENARIO 1 ---
      heading2("Scenario 1: Internal Transfer (Same Company, Between Warehouses)"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Use Case: ", font: "Calibri", size: 22, bold: true, color: "1565C0" }),
          new TextRun({ text: "Move furniture from Krishnadas Group main WH to Near Home GF or Factory Building.", font: "Calibri", size: 22, color: "1565C0" }),
        ]
      }),
      emptyLine(),
      heading3("Manual Method:"),
      numberedItem("Go to Inventory \u2192 Operations \u2192 Internal Transfers \u2192 Create", "numbers"),
      numberedItem("Source Location: WH/Stock", "numbers"),
      numberedItem("Destination Location: NH GF/Stock (or FB/Stock)", "numbers"),
      numberedItem("Add products and quantities \u2192 Validate", "numbers"),
      emptyLine(),
      heading3("Automatic Method (Already Configured):"),
      para("NH GF and NH FF have auto-resupply routes from main WH. When stock is needed (e.g., SO created from NH GF warehouse), Odoo auto-creates the replenishment transfer."),
      emptyLine(),
      para("\u2705 Evidence in DB: WH/INT/00001 (WH \u2192 NH GF, State: done)", { bold: true, color: "28A745" }),

      separator(),

      // --- SCENARIO 2 ---
      heading2("Scenario 2: Transfer Between Branches (Under Same Parent)"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Use Case: ", font: "Calibri", size: 22, bold: true, color: "1565C0" }),
          new TextRun({ text: "Devika Furniture (Pathanamthitta) needs items from KDESIGN INTERIOR (Kochi) or from Krishnadas Group main WH.", font: "Calibri", size: 22, color: "1565C0" }),
        ]
      }),
      emptyLine(),
      para("Since both are branches under Krishnadas Group, stock moves via the inter-company transit location."),
      emptyLine(),
      heading3("Method A \u2014 Manual Internal Transfer:"),
      numberedItem("Switch to source company (e.g., Krishnadas Group)", "numbers2"),
      numberedItem("Create Internal Transfer: WH/Stock \u2192 Inter-company Transit", "numbers2"),
      numberedItem("Switch to destination company (e.g., Devika Furniture)", "numbers2"),
      numberedItem("Create Receipt: Inter-company Transit \u2192 DF/Stock", "numbers2"),
      emptyLine(),
      heading3("Method B \u2014 Inter-company SO/PO (Recommended):"),
      numberedItem("Devika Furniture creates a Purchase Order with vendor = Krishnadas Group", "numbers3"),
      numberedItem("Krishnadas Group creates corresponding Sales Order", "numbers3"),
      numberedItem("Delivery (Krishnadas) and Receipt (Devika) happen through transit", "numbers3"),
      emptyLine(),
      para("\u2705 Evidence in DB:", { bold: true, color: "28A745" }),
      bulletItem("WH/INT/00008 \u2192 WH/Stock to Inter-company transit (done)"),
      bulletItem("DF/INT/00003 \u2192 Inter-company transit to DF/Stock (done)"),

      separator(),

      // --- SCENARIO 2.5: AUTOMATIC RESUPPLY BETWEEN BRANCHES ---
      heading2("Scenario 3: AUTOMATIC Resupply Between Branches (Eliminating Manual Transfers)"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F5E9", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u2B50 KEY INSIGHT: ", font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
          new TextRun({ text: "Instead of manually creating 2 internal transfers every time, Odoo can AUTOMATICALLY resupply branch warehouses from the central warehouse \u2014 just like NH GF and NH FF already work!", font: "Calibri", size: 22, color: "2E7D32" }),
        ]
      }),
      emptyLine(),

      heading3("The Problem:"),
      para("Currently, moving stock from Krishnadas Group WH to Devika Furniture or KDESIGN INTERIOR requires:"),
      bulletItem("Step 1: Manually create internal transfer from WH/Stock \u2192 Inter-company Transit"),
      bulletItem("Step 2: Switch company, manually create receipt from Transit \u2192 DF/Stock or KDI/Stock"),
      para("This is tedious and error-prone when done repeatedly."),
      emptyLine(),

      heading3("The Solution \u2014 \u201CResupply From\u201D Configuration (Same as NH GF/NH FF):"),
      para("Odoo\u2019s inter-warehouse replenishment feature can work for branch warehouses too, but ONLY for warehouses within the SAME company. For branches (which are separate companies in Odoo), this requires a different approach."),
      emptyLine(),

      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u26A0 Important Distinction: ", font: "Calibri", size: 22, bold: true, color: "856404" }),
          new TextRun({ text: "The \u201CResupply From\u201D checkbox on warehouses works ONLY within the same company. NH GF and NH FF can auto-resupply from main WH because they are ALL under Krishnadas Group company. But Devika Furniture and KDESIGN INTERIOR are separate companies (branches), so the resupply route does NOT appear for them.", font: "Calibri", size: 22, color: "856404" }),
        ]
      }),
      emptyLine(),

      makeTable(
        ["Warehouse", "Company", "Resupply From", "Status"],
        [
          ["Near Home GF", "Krishnadas Group", "Krishnadas Group (main WH)", { text: "\u2705 WORKING", bold: true, color: "28A745" }],
          ["Near Home FF", "Krishnadas Group", "Krishnadas Group (main WH)", { text: "\u2705 WORKING", bold: true, color: "28A745" }],
          ["Factory Building", "Krishnadas Group", "NONE", { text: "Can be enabled", color: "1565C0" }],
          ["Devika Furniture Showroom", "Devika Furniture", "NONE", { text: "\u274C Different company", bold: true, color: "DC3545" }],
          ["KDESIGN Interior Kochi", "KDESIGN INTERIOR", "NONE", { text: "\u274C Different company", bold: true, color: "DC3545" }],
          ["kd warehouse", "KDESIGN INT. FURNISHING", "NONE", { text: "\u274C Separate company", bold: true, color: "DC3545" }],
        ],
        [2200, 2200, 2560, 2400]
      ),
      emptyLine(),

      heading3("Option A \u2014 Inter-Company Transaction Rules + Reordering Rules (RECOMMENDED):"),
      para("This is the best approach for automating transfers between branches/companies:"),
      emptyLine(),
      numberedItem("Enable Inter-Company Transactions in Settings \u2192 Companies for each company", "numbersResupply"),
      numberedItem("Configure: When Devika Furniture creates a PO from Krishnadas Group \u2192 auto-generate SO in Krishnadas Group", "numbersResupply"),
      numberedItem("Set up Reordering Rules on products at Devika Furniture\u2019s warehouse (DF/Stock)", "numbersResupply"),
      numberedItem("When stock falls below minimum \u2192 Odoo auto-creates PO to Krishnadas Group", "numbersResupply"),
      numberedItem("Inter-company rules auto-create the matching SO \u2192 Delivery + Receipt happen automatically", "numbersResupply"),
      emptyLine(),
      para("Result: Fully automatic! Stock drops at branch \u2192 PO auto-created \u2192 SO auto-created at parent \u2192 goods shipped via transit \u2192 received at branch. Zero manual intervention.", { bold: true, color: "2E7D32" }),
      emptyLine(),

      heading3("Option B \u2014 Consolidate Warehouses Under One Company:"),
      para("If the business doesn\u2019t need separate legal entities per branch:"),
      emptyLine(),
      numberedItem("Move Devika Furniture Showroom and KDESIGN Interior warehouses under Krishnadas Group company", "numbersResupply2"),
      numberedItem("Set \u201CResupply From\u201D = Krishnadas Group on each warehouse", "numbersResupply2"),
      numberedItem("Works exactly like NH GF/NH FF \u2014 auto internal transfers, single-step", "numbersResupply2"),
      emptyLine(),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u26A0 Trade-off: ", font: "Calibri", size: 22, bold: true, color: "856404" }),
          new TextRun({ text: "This loses separate accounting per branch. Only do this if branches don\u2019t need independent P&L/books. Not recommended for businesses with GST registrations per branch.", font: "Calibri", size: 22, color: "856404" }),
        ]
      }),
      emptyLine(),

      heading3("Recommendation for Krishnadas Group:"),
      para("\u2705 Go with Option A (Inter-company rules + Reordering rules). It gives you:", { bold: true }),
      bulletItem("Automatic stock replenishment at branch warehouses"),
      bulletItem("Proper accounting trail (PO/SO between companies)"),
      bulletItem("GST-compliant documentation (each transfer has invoice/bill)"),
      bulletItem("Delivery Challan / E-Way Bill can be generated from the delivery order"),
      bulletItem("Branch-wise P&L stays intact"),

      separator(),

      // --- SCENARIO 4 (was 3) ---
      heading2("Scenario 4: Transfer to Separate Company (KDESIGN INT. FURNISHING)"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Important: ", font: "Calibri", size: 22, bold: true, color: "856404" }),
          new TextRun({ text: "KDESIGN INTERIOR FURNISHING has NO parent. It\u2019s a separate legal entity. Transfers MUST go through Sale + Purchase.", font: "Calibri", size: 22, color: "856404" }),
        ]
      }),
      emptyLine(),
      heading3("Process:"),
      numberedItem("KDESIGN INT. FURNISHING creates PO with vendor = Krishnadas Group", "numbers4"),
      numberedItem("Krishnadas Group creates SO (manual now; can be automated with inter-company rules)", "numbers4"),
      numberedItem("Krishnadas ships: WH/Stock \u2192 Inter-company transit", "numbers4"),
      numberedItem("KDESIGN INT. FURNISHING receives: Transit \u2192 kd/Stock", "numbers4"),
      emptyLine(),
      para("\u2705 Evidence in DB:", { bold: true, color: "28A745" }),
      bulletItem("P00006: KDESIGN INT. FURNISHING purchased from Krishnadas Group"),
      bulletItem("WH/INT/00009 + kd/INT/00001: Physical stock moved through transit (done)"),

      separator(),

      // --- SCENARIO 5 ---
      heading2("Scenario 5: Branch-wise Reporting"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Use Case: ", font: "Calibri", size: 22, bold: true, color: "1565C0" }),
          new TextRun({ text: "Client wants to see sales, purchases, and stock reports per branch/company.", font: "Calibri", size: 22, color: "1565C0" }),
        ]
      }),
      emptyLine(),
      heading3("What Works Now:"),
      bulletItem("Company switcher (top-right) \u2014 switch to any company to see its data only"),
      bulletItem("All reports (Sales, Purchase, Inventory) respect the active company filter"),
      bulletItem("Stock valuation is per-warehouse \u2014 each branch shows its own stock value"),
      bulletItem("No analytic accounting needed for basic branch-wise reporting"),
      emptyLine(),
      heading3("For Advanced Reporting:"),
      bulletItem("Enable Analytic Accounting for project-wise cost tracking across companies"),
      bulletItem("Use parent company view (Krishnadas Group) for consolidated reports"),

      separator(),

      // --- SCENARIO 6 ---
      heading2("Scenario 6: Purchasing to Specific Warehouse/Branch"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Use Case: ", font: "Calibri", size: 22, bold: true, color: "1565C0" }),
          new TextRun({ text: "Each branch buys from its own vendors and receives stock at its own warehouse.", font: "Calibri", size: 22, color: "1565C0" }),
        ]
      }),
      emptyLine(),
      heading3("How It Works:"),
      numberedItem("Switch to the branch company (e.g., Devika Furniture)", "numbers5"),
      numberedItem("Create PO \u2014 delivery warehouse auto-set to DF (Showroom)", "numbers5"),
      numberedItem("Confirm and receive goods at the branch warehouse", "numbers5"),
      emptyLine(),
      para("\u2705 Already Working \u2014 POs exist for all companies:", { bold: true, color: "28A745" }),
      bulletItem("Krishnadas Group: P00007, P00008 (Kerala Blinds, Southern Mattress)"),
      bulletItem("Devika Furniture: P00009, P00010 (Kerala Blinds, Malabar Furnishing)"),
      bulletItem("KDESIGN INTERIOR: P00011, P00012 (Cochin Laminate, Kerala Blinds)"),
      bulletItem("KDESIGN INT. FURNISHING: P00013, P00014 (Travancore Wood, Kerala Blinds)"),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 3: FUTURE SCOPE =====
      heading1("4. FUTURE SCOPE \u2014 Recommendations"),
      para("Priority improvements to discuss with the client, ordered by business impact:"),
      emptyLine(),
      makeTable(
        ["#", "Area", "Current State", "Recommendation", "Priority"],
        [
          ["1", "Product Type", "All consumable (consu)", "Convert to Storable for accurate stock levels & valuation", { text: "HIGH", bold: true, color: "DC3545" }],
          ["2", "Inter-company Rules", "Not configured", "Auto-generate SO when branch creates PO from parent. Saves manual work.", { text: "HIGH", bold: true, color: "DC3545" }],
          ["3", "Product Tracking", "No lots or serials", "Enable Lot tracking for high-value furniture, Serial for unique items.", { text: "HIGH", bold: true, color: "DC3545" }],
          ["4", "Cross-company Resupply", "Only within Krishnadas Group", "Add resupply routes from main WH to Devika & KDESIGN INTERIOR.", { text: "MEDIUM", bold: true, color: "FFC107" }],
          ["5", "KDESIGN INT. FURNISHING Structure", "No parent company", "Decide: make it a branch under Krishnadas Group? Simplifies transfers.", { text: "MEDIUM", bold: true, color: "FFC107" }],
          ["6", "User Roles", "1 admin user", "Create branch-specific users (WH managers, salespersons) with access rights.", { text: "MEDIUM", bold: true, color: "FFC107" }],
          ["7", "Barcode Scanning", "Not enabled", "Enable for warehouse ops \u2014 receiving, transfers, delivery.", { text: "LOW", bold: true, color: "28A745" }],
          ["8", "Analytic Accounting", "Not enabled", "Add for project-wise tracking across companies.", { text: "LOW", bold: true, color: "28A745" }],
        ],
        [400, 1600, 1800, 3560, 2000]
      ),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 4: TALKING POINTS =====
      heading1("6. KEY TALKING POINTS"),
      para("Use these during the meeting to structure the conversation:"),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "F0F7ED", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"Your structure is solid."', font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
        ]
      }),
      para("3 branches + 1 independent company, 8 warehouses, 2 cities. The foundation for multi-company operations is correctly set up in Odoo 19."),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "F0F7ED", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"Auto-resupply is already working."', font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
        ]
      }),
      para("Near Home GF and FF auto-replenish from WH. This same mechanism can be extended to branch warehouses for fully automated restocking."),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "F0F7ED", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"Inter-company transfers work but are manual."', font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
        ]
      }),
      para("Stock is moving between companies through the transit location. Enabling inter-company rules will automate the matching SO/PO creation \u2014 less manual work, fewer errors."),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"Products need an upgrade."', font: "Calibri", size: 22, bold: true, color: "856404" }),
        ]
      }),
      para("Currently all products are consumable with no tracking. For a furniture business, storable products with lot tracking are essential for accurate inventory, valuation, and warranty management."),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"KDESIGN INTERIOR FURNISHING is structurally different."', font: "Calibri", size: 22, bold: true, color: "856404" }),
        ]
      }),
      para("It has no parent company, unlike Devika Furniture and KDESIGN INTERIOR. Ask: Is this intentional? If not, making it a branch under Krishnadas Group will simplify transfers and reporting."),
      emptyLine(),

      new Paragraph({
        numbering: { reference: "talkingPoints", level: 0 },
        spacing: { before: 100, after: 60 },
        shading: { fill: "F0F7ED", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: '"Branch-wise reporting works out of the box."', font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
        ]
      }),
      para("Just switch companies using the company switcher. All standard reports filter automatically. For deeper cross-company analysis, analytic accounting can be enabled later."),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 5: QUICK REFERENCE =====
      heading1("5. QUICK REFERENCE \u2014 Transfer Flow Cheat Sheet"),
      emptyLine(),

      makeTable(
        ["Transfer Type", "From \u2192 To", "Method", "Example in DB"],
        [
          ["Same company, same WH to sub-warehouse", "WH/Stock \u2192 NH GF/Stock", "Internal Transfer or Auto-resupply", "WH/INT/00001 (done)"],
          ["Branch to Branch (same parent)", "Krishnadas \u2192 Devika Furniture", "Internal via Transit OR SO/PO", "WH/INT/00008 + DF/INT/00003"],
          ["Branch to Branch (same parent)", "Devika \u2192 KDESIGN INTERIOR", "Internal via Transit OR SO/PO", "DF/INT/00004 (draft)"],
          ["Separate companies", "Krishnadas \u2192 KDESIGN INT. FURNISHING", "Must use SO/PO method", "P00006 + kd/INT/00001"],
          ["External vendor to branch", "Vendor \u2192 Devika Furniture", "Standard PO", "P00009, P00010"],
          ["Branch to customer", "KDESIGN INTERIOR \u2192 Customer", "Standard SO", "S00014, S00015, S00016"],
        ],
        [2200, 2200, 2560, 2400]
      ),

      emptyLine(), emptyLine(),

      heading2("Stock Location Hierarchy (Krishnadas Group Main WH):"),
      bulletItem("WH/Stock (main storage)"),
      new Paragraph({
        numbering: { reference: "bullets", level: 1 },
        spacing: { before: 40, after: 40 },
        children: [new TextRun({ text: "Ground Floor, First Floor, Second Floor, Third Floor, Fourth Floor, Fifth Floor", font: "Calibri", size: 22, color: "333333" })]
      }),
      bulletItem("NH GF/Stock (Near Home Ground Floor)"),
      bulletItem("NH FF/Stock (Near Home First Floor)"),
      bulletItem("FB/Stock (Factory Building)"),
      bulletItem("Inter-company Transit (shared between all companies)"),

      // ===== PAGE BREAK =====
      new Paragraph({ children: [new PageBreak()] }),

      // ===== SECTION 6: DELIVERY CHALLAN & E-WAY BILL =====
      heading1("7. DELIVERY CHALLAN & E-WAY BILL \u2014 Transport Documents"),

      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "FFF3CD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u26A0 The Problem: ", font: "Calibri", size: 22, bold: true, color: "856404" }),
          new TextRun({ text: "Internal transfers between branches have NO invoice or accounting entries. But when goods physically move on a truck, transport authorities or checkposts can ask for documentation. Without it, goods can be seized.", font: "Calibri", size: 22, color: "856404" }),
        ]
      }),
      emptyLine(),

      heading2("7.1 What is a Delivery Challan?"),
      para("A Delivery Challan is a legal document used when goods are transported WITHOUT a sale/purchase transaction. It covers:"),
      bulletItem("Inter-branch transfers (same company or between branches)"),
      bulletItem("Goods sent for job work / subcontracting"),
      bulletItem("Goods sent on approval / returnable basis"),
      bulletItem("Supply of liquid gas where quantity is unknown at dispatch"),
      emptyLine(),
      para("Under GST Rule 55, a Delivery Challan must contain:", { bold: true }),
      bulletItem("Date and serial number of the challan"),
      bulletItem("Name, address, and GSTIN of consigner and consignee"),
      bulletItem("HSN code, description, and quantity of goods"),
      bulletItem("Taxable value and tax rate (CGST/SGST/IGST)"),
      bulletItem("Place of supply and reason for transportation"),
      bulletItem("Signature of the consigner"),

      separator(),

      heading2("7.2 What is an E-Way Bill?"),
      para("An E-Way Bill (Electronic Way Bill) is MANDATORY under GST when goods worth more than \u20B950,000 are transported. It\u2019s generated on the government portal and must accompany the goods during transit."),
      emptyLine(),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "Key Rule: ", font: "Calibri", size: 22, bold: true, color: "1565C0" }),
          new TextRun({ text: "E-Way Bill is required for goods movement exceeding \u20B950,000 \u2014 even if there is no sale. This includes internal/branch transfers!", font: "Calibri", size: 22, color: "1565C0" }),
        ]
      }),
      emptyLine(),
      para("E-Way Bill contains:"),
      bulletItem("E-Way Bill number and generation date"),
      bulletItem("Validity period (based on distance: ~100 km/day for normal cargo)"),
      bulletItem("GSTIN of supplier and recipient"),
      bulletItem("Document type (Invoice / Challan / Bill of Supply)"),
      bulletItem("Vehicle number and transporter details"),
      bulletItem("HSN codes and goods value"),

      separator(),

      heading2("7.3 How Odoo 19 Handles This (Indian Localization)"),
      para("Odoo 19 has built-in modules for both:", { bold: true }),
      emptyLine(),

      makeTable(
        ["Module", "Technical Name", "Purpose"],
        [
          [{ text: "Indian E-waybill", bold: true }, "l10n_in_ewaybill", "E-Way bill integration with NIC portal (from Accounting/Invoicing)"],
          [{ text: "Indian E-waybill Stock", bold: true }, "l10n_in_ewaybill_stock", "E-Way bill / Delivery Challan from Inventory (Deliveries & Receipts)"],
        ],
        [2800, 2800, 3760]
      ),
      emptyLine(),

      heading3("From Invoices/Bills (Accounting):"),
      numberedItem("Confirm the customer invoice or vendor bill", "numbers6"),
      numberedItem("Click \u201CCreate e-Waybill\u201D on the invoice", "numbers6"),
      numberedItem("Enter transport details (vehicle number, distance, etc.)", "numbers6"),
      numberedItem("Click \u201CGenerate e-Waybill\u201D \u2192 submits to NIC portal", "numbers6"),
      numberedItem("Print invoice PDF \u2014 includes E-Way Bill number and validity date", "numbers6"),
      emptyLine(),

      heading3("From Deliveries/Receipts (Inventory) \u2014 FOR INTERNAL TRANSFERS:"),
      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F5E9", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u2B50 This is the key feature for branch transfers!", font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
        ]
      }),
      numberedItem("Go to Inventory \u2192 Operations \u2192 Deliveries (or Receipts)", "numbers5"),
      numberedItem("Select the validated delivery order (state must be \u201CDone\u201D)", "numbers5"),
      numberedItem("Click \u201CCreate E-waybill/Challan\u201D", "numbers5"),
      numberedItem("Two options appear:", "numbers5"),
      emptyLine(),

      makeTable(
        ["Option", "When to Use", "What Happens"],
        [
          [{ text: "Generate e-Waybill", bold: true }, "Goods value > \u20B950,000 OR interstate movement", "Submits to NIC portal, gets E-Way Bill number, legally valid"],
          [{ text: "Use as Challan", bold: true }, "Goods value < \u20B950,000 AND intrastate (within Kerala)", "Creates Delivery Challan locally, does NOT submit to NIC portal"],
        ],
        [2600, 3200, 3560]
      ),
      emptyLine(),
      numberedItem("To print: Click the Gear icon \u2192 Print \u2192 \u201CEwaybill / Delivery Challan\u201D", "numbers5"),

      separator(),

      heading2("7.4 Which Document for Which Transfer?"),
      emptyLine(),
      makeTable(
        ["Transfer Scenario", "Document Needed", "Why"],
        [
          ["WH \u2192 NH GF (same building/nearby)", "None (optional Challan)", "No road transport involved"],
          ["WH \u2192 Factory Building (within city)", "Delivery Challan", "Goods on road, but likely < \u20B950K per trip"],
          ["Krishnadas \u2192 Devika Furniture (same city)", "Delivery Challan", "Inter-branch, same city (Pathanamthitta)"],
          ["Krishnadas \u2192 KDESIGN INTERIOR (Pathanamthitta \u2192 Kochi)", { text: "E-Way Bill (MANDATORY)", bold: true, color: "DC3545" }, "Interstate/intercity, likely > \u20B950K for furniture"],
          ["Krishnadas \u2192 KDESIGN INT. FURNISHING", "Delivery Challan or E-Way Bill", "Separate company, check value threshold"],
          ["Vendor \u2192 Any warehouse (Purchase)", "E-Way Bill from vendor", "Vendor\u2019s responsibility, but verify on receipt"],
        ],
        [3000, 2800, 3560]
      ),

      separator(),

      heading2("7.5 Setup Steps for Client"),
      para("To enable this in the client-cient database:", { bold: true }),
      emptyLine(),
      numberedItem("Install module: Indian E-waybill (l10n_in_ewaybill)", "numbers2"),
      numberedItem("Install module: Indian E-waybill Stock (l10n_in_ewaybill_stock)", "numbers2"),
      numberedItem("Go to Accounting \u2192 Configuration \u2192 Settings \u2192 Indian Integration", "numbers2"),
      numberedItem("Enable \u201CRegistered Under GST\u201D and \u201CE-Way bill\u201D", "numbers2"),
      numberedItem("Register API credentials on NIC E-Way Bill portal (ewaybillgst.gov.in)", "numbers2"),
      numberedItem("Set GSP provider to \u201CBVM IT Consulting Services India Pvt Ltd\u201D", "numbers2"),
      numberedItem("Ensure GSTIN is configured for each company/branch", "numbers2"),
      emptyLine(),

      new Paragraph({
        spacing: { before: 80, after: 80 },
        shading: { fill: "E8F5E9", type: ShadingType.CLEAR },
        children: [
          new TextRun({ text: "\u2705 Quick Win: ", font: "Calibri", size: 22, bold: true, color: "2E7D32" }),
          new TextRun({ text: "Even without NIC portal registration, the \u201CUse as Challan\u201D option works immediately. The client can start generating Delivery Challans for branch transfers right away while E-Way Bill API setup is done separately.", font: "Calibri", size: 22, color: "2E7D32" }),
        ]
      }),

      emptyLine(), emptyLine(),
      separator(),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200 },
        children: [new TextRun({ text: "\u2014 End of Meeting Brief \u2014", font: "Calibri", size: 22, italics: true, color: "999999" })]
      }),
    ]
  }]
});

const OUTPUT_PATH = "C:\\Odoo Study\\My learnings\\Rohan_Documentation\\Client_Meeting_Brief_Krishnadas_Group_V3.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log("Document created: " + OUTPUT_PATH);
});
