/**
 * Branch-Wise Accounting & Reporting Demo Flow Guide
 * For Krishnadas Group - Odoo 19
 * 
 * Comprehensive step-by-step guide for demonstrating branch-wise reports
 */

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

// ── Shared Styles ──
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: "2E75B6" };
const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };

function headerCell(text, width) {
  return new TableCell({
    borders: headerBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "2E75B6", type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}

function dataCell(text, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shade ? { fill: "F2F7FB", type: ShadingType.CLEAR } : undefined,
    margins: { top: 50, bottom: 50, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 19, bold: opts.bold || false })] })]
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, bold: true, font: "Arial", size: 32, color: "1A3C6E" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, bold: true, font: "Arial", size: 26, color: "2E75B6" })]
  });
}

function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, bold: true, font: "Arial", size: 22, color: "404040" })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 21, ...opts })]
  });
}

function boldPara(label, value) {
  return new Paragraph({
    spacing: { after: 100 },
    children: [
      new TextRun({ text: label, font: "Arial", size: 21, bold: true }),
      new TextRun({ text: value, font: "Arial", size: 21 })
    ]
  });
}

function bullet(text, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 21 })]
  });
}

function numberedItem(text, ref = "steps") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 21 })]
  });
}

function stepBold(label, rest) {
  return new Paragraph({
    numbering: { reference: "steps", level: 0 },
    spacing: { after: 80 },
    children: [
      new TextRun({ text: label, font: "Arial", size: 21, bold: true }),
      new TextRun({ text: rest, font: "Arial", size: 21 })
    ]
  });
}

function importantBox(text) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    indent: { left: 360, right: 360 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 6, color: "FF6B35", space: 10 }
    },
    children: [
      new TextRun({ text: "IMPORTANT: ", font: "Arial", size: 21, bold: true, color: "FF6B35" }),
      new TextRun({ text, font: "Arial", size: 21 })
    ]
  });
}

function tipBox(text) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    indent: { left: 360, right: 360 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 6, color: "28A745", space: 10 }
    },
    children: [
      new TextRun({ text: "TIP: ", font: "Arial", size: 21, bold: true, color: "28A745" }),
      new TextRun({ text, font: "Arial", size: 21 })
    ]
  });
}

function warningBox(text) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    indent: { left: 360, right: 360 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 6, color: "DC3545", space: 10 }
    },
    children: [
      new TextRun({ text: "WARNING: ", font: "Arial", size: 21, bold: true, color: "DC3545" }),
      new TextRun({ text, font: "Arial", size: 21 })
    ]
  });
}

function menuPath(path) {
  return new Paragraph({
    spacing: { after: 100 },
    indent: { left: 360 },
    children: [
      new TextRun({ text: "Menu Path: ", font: "Arial", size: 20, bold: true, color: "555555" }),
      new TextRun({ text: path, font: "Consolas", size: 20, color: "2E75B6" })
    ]
  });
}

function spacer() {
  return new Paragraph({ spacing: { after: 80 }, children: [] });
}

// ── Document ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1A3C6E" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "404040" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps2",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps3",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps4",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps5",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps6",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps7",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "steps8",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "stepsDemo",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets3",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets4",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // ══════════════════════════════════════════════════
    // COVER PAGE
    // ══════════════════════════════════════════════════
    {
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
            children: [new TextRun({ text: "Krishnadas Group | Branch-Wise Reporting Guide", font: "Arial", size: 16, color: "999999" })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Confidential | Infintor Solutions | Page ", font: "Arial", size: 16, color: "999999" }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })
            ]
          })]
        })
      },
      children: [
        spacer(), spacer(), spacer(), spacer(), spacer(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "KRISHNADAS GROUP", font: "Arial", size: 44, bold: true, color: "1A3C6E" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 },
          children: [new TextRun({ text: "Branch-Wise Accounting & Reporting", font: "Arial", size: 36, color: "2E75B6" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({ text: "Complete Demo Flow Guide", font: "Arial", size: 28, color: "555555" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          children: [new TextRun({ text: "Odoo 19 Enterprise", font: "Arial", size: 24, color: "777777" })]
        }),
        spacer(), spacer(), spacer(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          children: [new TextRun({ text: "Prepared by: Rohan Raj", font: "Arial", size: 22, color: "555555" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          children: [new TextRun({ text: "Infintor Solutions", font: "Arial", size: 22, color: "555555" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          children: [new TextRun({ text: "Date: March 3, 2026", font: "Arial", size: 22, color: "555555" })]
        }),
        spacer(), spacer(), spacer(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" } },
          children: []
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 120 },
          children: [new TextRun({ text: "Database: client-cient.odoo.com", font: "Consolas", size: 20, color: "777777" })]
        }),

        // ══════════════════════════════════════════════════
        // PAGE BREAK → SECTION 1
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════ SECTION 1: WHY REPORTS SHOW COMBINED DATA ═══════
        h1("1. Why Your Reports Show Combined Data"),
        para("This section explains the root cause of why the Partner Ledger (and other reports) showed combined data instead of branch-specific data."),
        
        h2("1.1 Root Cause"),
        importantBox("When you are logged into the parent company (Krishnadas Group), ALL reports automatically consolidate data from ALL branches. This is BY DESIGN in Odoo 19."),
        
        para("Odoo's branch accounting works on this principle:"),
        bullet("Parent company (Krishnadas Group) = Consolidated view of ALL branches"),
        bullet("Individual branch (Devika Furniture / KDESIGN INTERIOR) = Only that branch's data"),
        bullet("The Company Selector in the top-right corner of the screen controls which data you see"),

        h2("1.2 How the Company Selector Works"),
        numberedItem("Click the company name in the top-right corner of the header menu", "steps"),
        numberedItem("A dropdown appears showing all companies/branches you have access to", "steps"),
        numberedItem("Checkboxes let you select which companies are active", "steps"),
        numberedItem("The HIGHLIGHTED company is the active environment", "steps"),
        numberedItem("To switch: click on the company name (not just the checkbox)", "steps"),

        importantBox("Selecting Krishnadas Group (parent) automatically includes ALL branches. Selecting only Devika Furniture shows ONLY Devika's data. This applies to ALL reports, invoices, bills, and payments."),

        h2("1.3 Your Company Structure"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2500, 2000, 1200, 1800, 1860],
          rows: [
            new TableRow({ children: [
              headerCell("Company", 2500), headerCell("Type", 2000), headerCell("ID", 1200), headerCell("GSTIN", 1800), headerCell("Location", 1860)
            ]}),
            new TableRow({ children: [
              dataCell("Krishnadas Group", 2500, { bold: true }), dataCell("Parent Company", 2000), dataCell("1", 1200), dataCell("32AABFK5678M1ZQ", 1800), dataCell("Pathanamthitta", 1860)
            ]}),
            new TableRow({ children: [
              dataCell("Devika Furniture", 2500, { shade: true }), dataCell("Branch of KG", 2000, { shade: true }), dataCell("2", 1200, { shade: true }), dataCell("Same as parent", 1800, { shade: true }), dataCell("Pathanamthitta", 1860, { shade: true })
            ]}),
            new TableRow({ children: [
              dataCell("KDESIGN INTERIOR", 2500), dataCell("Branch of KG", 2000), dataCell("3", 1200), dataCell("Same as parent", 1800), dataCell("Kochi", 1860)
            ]}),
            new TableRow({ children: [
              dataCell("KDESIGN INT. FURNISHING", 2500, { shade: true }), dataCell("Standalone Company", 2000, { shade: true }), dataCell("4", 1200, { shade: true }), dataCell("32AAKCK2345R1Z5", 1800, { shade: true }), dataCell("Pathanamthitta", 1860, { shade: true })
            ]}),
          ]
        }),

        // ═══════ PAGE BREAK → SECTION 2 ═══════
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════ SECTION 2: EXISTING DATA SNAPSHOT ═══════
        h1("2. Current Data Snapshot (Per Branch)"),
        para("Below is the complete summary of all accounting data currently in the system, organized by company/branch."),

        h2("2.1 Krishnadas Group (Parent Company)"),
        h3("Journals"),
        bullet("Bank Yes 0024 (Bank)"),
        bullet("Bank Fed 3185 (Bank)"),
        bullet("Bank SIB 0388 (Bank)"),
        bullet("Cash (Cash)"),
        
        h3("Customer Invoices (10 invoices, all unpaid)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 3000, 1580, 2580],
          rows: [
            new TableRow({ children: [
              headerCell("Invoice #", 2200), headerCell("Customer", 3000), headerCell("Amount", 1580), headerCell("Status", 2580)
            ]}),
            ...[
              ["INV/25-26/0001", "KDESIGN INT. FURNISHING", "1,638", "Not Paid"],
              ["INV/25-26/0002", "Anoop Krishnan Nair", "5,000", "Not Paid"],
              ["INV/25-26/0003", "Anoop Krishnan Nair", "7,500", "Not Paid"],
              ["INV/25-26/0004", "Anoop Krishnan Nair", "3,000", "Not Paid"],
              ["INV/25-26/0005", "Deepa Nambiar", "2,000", "Not Paid"],
              ["INV/25-26/0006", "Deepa Nambiar", "1,500", "Not Paid"],
              ["INV/25-26/0007", "Deepa Nambiar", "4,000", "Not Paid"],
              ["INV/25-26/0008", "Anoop Krishnan Nair", "10,000", "Not Paid"],
              ["INV/25-26/0009", "Anoop Krishnan Nair", "8,242.50", "Not Paid"],
              ["INV/25-26/0010", "Varghese & Sons Builders", "55,125", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2200, { shade: i % 2 === 1 }), dataCell(r[1], 3000, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 2580, { shade: i % 2 === 1 })
            ]}))
          ]
        }),
        
        h3("Vendor Bills (7 bills, all unpaid)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2600, 3200, 1580, 1980],
          rows: [
            new TableRow({ children: [
              headerCell("Bill #", 2600), headerCell("Vendor", 3200), headerCell("Amount", 1580), headerCell("Status", 1980)
            ]}),
            ...[
              ["BILL/25-26/02/0001", "Cochin Laminate House", "3,000", "Not Paid"],
              ["BILL/25-26/02/0002", "Cochin Laminate House", "4,500", "Not Paid"],
              ["BILL/25-26/02/0003", "Cochin Laminate House", "1,800", "Not Paid"],
              ["BILL/25-26/02/0004", "Southern Mattress Factory", "1,31,250", "Not Paid"],
              ["BILL/25-26/02/0005", "Kerala Blinds & Curtains", "43,575", "Not Paid"],
              ["BILL/25-26/03/0003", "Malabar Furnishing Supplies", "4,200", "Not Paid"],
              ["BILL/25-26/03/0004", "Alabama Dept. of Labor", "5,880", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2600, { shade: i % 2 === 1 }), dataCell(r[1], 3200, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 1980, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Payments (4 payments)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2500, 2500, 1500, 1500, 1360],
          rows: [
            new TableRow({ children: [
              headerCell("Partner", 2500), headerCell("Type", 2500), headerCell("Amount", 1500), headerCell("Journal", 1500), headerCell("Status", 1360)
            ]}),
            ...[
              ["Anoop Krishnan Nair", "Customer Payment", "5,000", "Bank Yes 0024", "Posted"],
              ["Deepa Nambiar", "Customer Payment", "2,000", "Bank Yes 0024", "Posted"],
              ["Varghese & Sons", "Customer Payment", "25,000", "Bank Yes 0024", "Posted"],
              ["Cochin Laminate House", "Vendor Payment", "3,000", "Bank Yes 0024", "Posted"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2500, { shade: i % 2 === 1 }), dataCell(r[1], 2500, { shade: i % 2 === 1 }),
              dataCell(r[2], 1500, { shade: i % 2 === 1 }), dataCell(r[3], 1500, { shade: i % 2 === 1 }),
              dataCell(r[4], 1360, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        // ── Devika Furniture ──
        new Paragraph({ children: [new PageBreak()] }),
        h2("2.2 Devika Furniture (Branch)"),
        h3("Journals"),
        bullet("Bank Devika 4501 (Bank)", "bullets2"),
        bullet("Cash - Devika (Cash)", "bullets2"),
        bullet("Cash Devika Furniture (Cash)", "bullets2"),

        h3("Customer Invoices (2 invoices + 2 partially paid)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 3000, 1580, 2580],
          rows: [
            new TableRow({ children: [
              headerCell("Invoice #", 2200), headerCell("Customer", 3000), headerCell("Amount", 1580), headerCell("Status", 2580)
            ]}),
            ...[
              ["INV/25-26/0001", "Lakshmi Devi", "5,500", "Not Paid"],
              ["INV/25-26/0002", "Deepa Nambiar", "26,800", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2200, { shade: i % 2 === 1 }), dataCell(r[1], 3000, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 2580, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Vendor Bills (5 bills)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2600, 3200, 1580, 1980],
          rows: [
            new TableRow({ children: [
              headerCell("Bill #", 2600), headerCell("Vendor", 3200), headerCell("Amount", 1580), headerCell("Status", 1980)
            ]}),
            ...[
              ["BILL/25-26/02/0001", "Malabar Furnishing", "27,600", "Not Paid"],
              ["BILL/25-26/02/0002", "Kerala Blinds & Curtains", "20,500", "Not Paid"],
              ["BILL/25-26/03/0001", "Malabar Furnishing", "10,000", "Not Paid"],
              ["BILL/25-26/03/0002", "Malabar Furnishing", "2,000", "Not Paid"],
              ["BILL/25-26/03/0005", "Alabama Dept. of Labor", "210", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2600, { shade: i % 2 === 1 }), dataCell(r[1], 3200, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 1980, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Payments (4 payments)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2500, 2500, 1500, 1500, 1360],
          rows: [
            new TableRow({ children: [
              headerCell("Partner", 2500), headerCell("Type", 2500), headerCell("Amount", 1500), headerCell("Journal", 1500), headerCell("Status", 1360)
            ]}),
            ...[
              ["Deepa Nambiar", "Customer Payment", "1,560", "Bank Yes 0024", "Posted"],
              ["(No partner)", "Customer Payment", "54.60", "Bank Yes 0024", "Posted"],
              ["Deepa Nambiar", "Customer Payment", "5,000", "Bank Devika 4501", "Posted"],
              ["Malabar Furnishing", "Vendor Payment", "10,000", "Bank Devika 4501", "Posted"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2500, { shade: i % 2 === 1 }), dataCell(r[1], 2500, { shade: i % 2 === 1 }),
              dataCell(r[2], 1500, { shade: i % 2 === 1 }), dataCell(r[3], 1500, { shade: i % 2 === 1 }),
              dataCell(r[4], 1360, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        // ── KDESIGN INTERIOR ──
        h2("2.3 KDESIGN INTERIOR (Branch)"),
        h3("Journals"),
        bullet("Bank KDESIGN 7802 (Bank)", "bullets3"),
        bullet("Cash - KDESIGN (Cash)", "bullets3"),

        h3("Customer Invoices (2 invoices)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 3000, 1580, 2580],
          rows: [
            new TableRow({ children: [
              headerCell("Invoice #", 2200), headerCell("Customer", 3000), headerCell("Amount", 1580), headerCell("Status", 2580)
            ]}),
            ...[
              ["INV/25-26/0001", "Suresh Menon", "16,900", "Not Paid"],
              ["INV/25-26/0002", "Green Valley Residency", "22,900", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2200, { shade: i % 2 === 1 }), dataCell(r[1], 3000, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 2580, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Vendor Bills (2 bills)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2600, 3200, 1580, 1980],
          rows: [
            new TableRow({ children: [
              headerCell("Bill #", 2600), headerCell("Vendor", 3200), headerCell("Amount", 1580), headerCell("Status", 1980)
            ]}),
            ...[
              ["BILL/25-26/02/0001", "Kerala Blinds & Curtains", "11,250", "Not Paid"],
              ["BILL/25-26/02/0002", "Cochin Laminate House", "53,400", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2600, { shade: i % 2 === 1 }), dataCell(r[1], 3200, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 1980, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Payments (2 payments)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2500, 2500, 1500, 1500, 1360],
          rows: [
            new TableRow({ children: [
              headerCell("Partner", 2500), headerCell("Type", 2500), headerCell("Amount", 1500), headerCell("Journal", 1500), headerCell("Status", 1360)
            ]}),
            ...[
              ["Suresh Menon", "Customer Payment", "10,000", "Bank KDESIGN", "Posted"],
              ["Kerala Blinds", "Vendor Payment", "11,250", "Bank KDESIGN", "Posted"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2500, { shade: i % 2 === 1 }), dataCell(r[1], 2500, { shade: i % 2 === 1 }),
              dataCell(r[2], 1500, { shade: i % 2 === 1 }), dataCell(r[3], 1500, { shade: i % 2 === 1 }),
              dataCell(r[4], 1360, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        // ── KDESIGN INTERIOR FURNISHING ──
        h2("2.4 KDESIGN INTERIOR FURNISHING (Standalone)"),
        h3("Journals"),
        bullet("Bank (Bank)", "bullets4"),

        h3("Customer Invoices (2 invoices)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 3000, 1580, 2580],
          rows: [
            new TableRow({ children: [
              headerCell("Invoice #", 2200), headerCell("Customer", 3000), headerCell("Amount", 1580), headerCell("Status", 2580)
            ]}),
            ...[
              ["INV/25-26/0001", "Skyline Apartments Kochi", "32,340", "Not Paid"],
              ["INV/25-26/0002", "Anoop Krishnan Nair", "4,515", "Not Paid"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2200, { shade: i % 2 === 1 }), dataCell(r[1], 3000, { shade: i % 2 === 1 }),
              dataCell(r[2], 1580, { shade: i % 2 === 1 }), dataCell(r[3], 2580, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        h3("Payments (1 payment)"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2500, 2500, 1500, 1500, 1360],
          rows: [
            new TableRow({ children: [
              headerCell("Partner", 2500), headerCell("Type", 2500), headerCell("Amount", 1500), headerCell("Journal", 1500), headerCell("Status", 1360)
            ]}),
            ...[
              ["Skyline Apartments", "Customer Payment", "15,000", "Bank", "Posted"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 2500, { shade: i % 2 === 1 }), dataCell(r[1], 2500, { shade: i % 2 === 1 }),
              dataCell(r[2], 1500, { shade: i % 2 === 1 }), dataCell(r[3], 1500, { shade: i % 2 === 1 }),
              dataCell(r[4], 1360, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        // ══════════════════════════════════════════════════
        // SECTION 3: STEP-BY-STEP - HOW TO VIEW BRANCH-WISE REPORTS
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("3. How to View Branch-Wise Reports (Step-by-Step)"),
        
        warningBox("This is the most critical section. The entire issue was about not knowing how to switch between companies. Follow these steps exactly."),

        h2("3.1 Viewing Combined Report (All Branches)"),
        para("To see consolidated data across all branches:"),
        numberedItem("Click the company selector in the top-right corner of the screen", "steps2"),
        numberedItem("Ensure 'Krishnadas Group' (parent company) is CHECKED and HIGHLIGHTED", "steps2"),
        numberedItem("When the parent is selected, all branches (Devika & KDESIGN) are automatically included", "steps2"),
        numberedItem("Navigate to the desired report:", "steps2"),
        menuPath("Accounting > Reporting > Partner Ledger"),
        numberedItem("The report will show data from ALL branches combined", "steps2"),

        tipBox("When the parent company is selected, you see the CONSOLIDATED view. This is correct behavior, not a bug."),

        h2("3.2 Viewing Devika Furniture Only"),
        para("To see ONLY Devika Furniture's data:"),
        numberedItem("Click the company selector in the top-right corner", "steps3"),
        numberedItem("UNCHECK 'Krishnadas Group' (parent)", "steps3"),
        numberedItem("CHECK only 'Devika Furniture'", "steps3"),
        numberedItem("Click on 'Devika Furniture' to make it the ACTIVE company (it should be highlighted)", "steps3"),
        numberedItem("Navigate to the report:", "steps3"),
        menuPath("Accounting > Reporting > Partner Ledger"),
        numberedItem("The report will now show ONLY Devika Furniture's invoices, bills, and payments", "steps3"),
        
        importantBox("You should see only: Lakshmi Devi (INV 5,500), Deepa Nambiar (INV 26,800), Malabar Furnishing (Bills), Kerala Blinds (Bills), and their payments."),

        h2("3.3 Viewing KDESIGN INTERIOR Only"),
        para("To see ONLY KDESIGN INTERIOR's data:"),
        numberedItem("Click the company selector in the top-right corner", "steps4"),
        numberedItem("UNCHECK everything else", "steps4"),
        numberedItem("CHECK only 'KDESIGN INTERIOR'", "steps4"),
        numberedItem("Click on 'KDESIGN INTERIOR' to make it ACTIVE (highlighted)", "steps4"),
        numberedItem("Navigate to the report:", "steps4"),
        menuPath("Accounting > Reporting > Partner Ledger"),
        numberedItem("The report shows ONLY KDESIGN INTERIOR's data", "steps4"),
        
        importantBox("You should see only: Suresh Menon (INV 16,900), Green Valley Residency (INV 22,900), Kerala Blinds (Bill 11,250), Cochin Laminate (Bill 53,400), and their payments."),

        h2("3.4 Viewing KDESIGN INTERIOR FURNISHING"),
        para("KDESIGN INTERIOR FURNISHING is a SEPARATE company (not a branch of Krishnadas Group). It has its own GSTIN."),
        numberedItem("Click the company selector in the top-right corner", "steps5"),
        numberedItem("UNCHECK everything else", "steps5"),
        numberedItem("CHECK only 'KDESIGN INTERIOR FURNISHING'", "steps5"),
        numberedItem("Click on its name to make it ACTIVE", "steps5"),
        numberedItem("Navigate to reports", "steps5"),
        
        warningBox("Since KDESIGN INTERIOR FURNISHING is a separate company (different GSTIN), its data is NEVER included in Krishnadas Group's consolidated view. You must switch to this company to see its data."),

        // ══════════════════════════════════════════════════
        // SECTION 4: ALL REPORTS AND WHAT THEY SHOW
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("4. Complete Report Guide — What Each Report Shows"),
        para("Here is every accounting report available and how it works with branch-wise filtering."),
        
        importantBox("ALL reports follow the same rule: they show data for the company/branch selected in the Company Selector. No exceptions."),

        h2("4.1 Partner Ledger"),
        menuPath("Accounting > Reporting > Partner Ledger"),
        para("Shows the balance of all customers and vendors with transaction details."),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3500, 5860],
          rows: [
            new TableRow({ children: [headerCell("View", 3500), headerCell("What You See", 5860)] }),
            new TableRow({ children: [dataCell("Krishnadas Group (parent)", 3500), dataCell("All partner balances from KG + Devika + KDESIGN INTERIOR combined", 5860)] }),
            new TableRow({ children: [dataCell("Devika Furniture only", 3500, { shade: true }), dataCell("Only Devika's customers (Lakshmi Devi, Deepa Nambiar) and vendors (Malabar, Kerala Blinds)", 5860, { shade: true })] }),
            new TableRow({ children: [dataCell("KDESIGN INTERIOR only", 3500), dataCell("Only KDESIGN's customers (Suresh Menon, Green Valley) and vendors (Kerala Blinds, Cochin Laminate)", 5860)] }),
          ]
        }),

        h2("4.2 General Ledger"),
        menuPath("Accounting > Reporting > General Ledger"),
        para("Shows all journal entries grouped by account. Every debit and credit posted."),
        bullet("Combined view (parent): Shows all accounts with entries from all branches"),
        bullet("Branch view: Shows only journal entries posted in that specific branch"),

        h2("4.3 Profit and Loss (P&L)"),
        menuPath("Accounting > Reporting > Profit and Loss"),
        para("Shows revenue, expenses, and net profit/loss for the selected period."),
        bullet("Combined view: Total revenue and expenses from all branches"),
        bullet("Branch view: Revenue and expenses of that branch only"),
        tipBox("Use this to compare profitability between Devika Furniture and KDESIGN INTERIOR individually."),

        h2("4.4 Balance Sheet"),
        menuPath("Accounting > Reporting > Balance Sheet"),
        para("Shows assets, liabilities, and equity as of a specific date."),
        bullet("Combined view: Consolidated financial position of the entire group"),
        bullet("Branch view: Financial position of that branch only"),

        h2("4.5 Trial Balance"),
        menuPath("Accounting > Reporting > Trial Balance"),
        para("Shows debit and credit totals for every account."),
        bullet("Combined view: All accounts with cumulative balances from all branches"),
        bullet("Branch view: Only balances from that branch's journal entries"),

        h2("4.6 Aged Receivable"),
        menuPath("Accounting > Reporting > Aged Receivable"),
        para("Shows outstanding customer invoices grouped by aging period (Current, 1-30 days, 31-60, etc)."),
        bullet("Combined view: All customers across all branches"),
        bullet("Branch view: Only customers who have invoices in that specific branch"),

        h2("4.7 Aged Payable"),
        menuPath("Accounting > Reporting > Aged Payable"),
        para("Shows outstanding vendor bills grouped by aging period."),
        bullet("Combined view: All vendors across all branches"),
        bullet("Branch view: Only vendors with bills in that specific branch"),

        h2("4.8 Cash Flow Statement"),
        menuPath("Accounting > Reporting > Cash Flow Statement"),
        para("Shows cash inflows and outflows from operating, investing, and financing activities."),

        h2("4.9 Tax Report (GST)"),
        menuPath("Accounting > Reporting > Tax Report"),
        para("Shows tax collected and tax paid, grouped by tax type (CGST, SGST, IGST)."),
        bullet("Combined view: Total GST from all branches (useful for consolidated GSTR filing)"),
        bullet("Branch view: GST from that branch only"),

        h2("4.10 Journal Report"),
        menuPath("Accounting > Reporting > Journal Report"),
        para("Shows all transactions entered in each journal (Sales, Purchase, Bank, Cash, etc)."),

        h2("4.11 India-Specific Reports"),
        para("These are available only when signed into the parent company:"),
        bullet("TCS Report: Tax Collected at Source"),
        bullet("TDS Report: Tax Deducted at Source"),
        menuPath("Accounting > Reporting > TCS Report / TDS Report"),

        // ══════════════════════════════════════════════════
        // SECTION 5: LIVE DEMO FLOW
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("5. Live Demo Flow — Step-by-Step Script"),
        para("Follow this exact sequence to demonstrate branch-wise accounting to the client. Do everything in one branch first, then switch and repeat."),

        h2("5.1 Part A: Demonstrate in Devika Furniture"),

        h3("Step A1: Switch to Devika Furniture"),
        numberedItem("Click Company Selector (top-right corner)", "steps6"),
        numberedItem("Uncheck all companies", "steps6"),
        numberedItem("Check ONLY 'Devika Furniture'", "steps6"),
        numberedItem("Click on 'Devika Furniture' to make it active (highlighted)", "steps6"),
        numberedItem("Verify: The company name in the top-right should show 'Devika Furniture'", "steps6"),

        h3("Step A2: Show Existing Invoices"),
        menuPath("Accounting > Customers > Invoices"),
        numberedItem("Point out that you can see ONLY Devika Furniture's invoices:", "steps7"),
        bullet("INV/25-26/0001 — Lakshmi Devi — Rs 5,500"),
        bullet("INV/25-26/0002 — Deepa Nambiar — Rs 26,800"),
        numberedItem("Emphasize: 'These are ONLY Devika's invoices. Krishnadas Group and KDESIGN invoices are NOT visible here.'", "steps7"),

        h3("Step A3: Show Existing Bills"),
        menuPath("Accounting > Vendors > Bills"),
        numberedItem("Show ONLY Devika's vendor bills:", "steps7"),
        bullet("Malabar Furnishing — Rs 27,600, Rs 10,000, Rs 2,000"),
        bullet("Kerala Blinds & Curtains — Rs 20,500"),

        h3("Step A4: Show Payments"),
        menuPath("Accounting > Customers > Payments (or Vendors > Payments)"),
        numberedItem("Show the payments registered for Devika:", "steps7"),
        bullet("Deepa Nambiar — Rs 1,560 (Bank Yes 0024)"),
        bullet("Deepa Nambiar — Rs 5,000 (Bank Devika 4501)"),
        bullet("Malabar Furnishing — Rs 10,000 (Vendor Payment)"),

        h3("Step A5: Register a New Payment (Live Demo)"),
        para("To create a payment against an invoice during the demo:"),
        numberedItem("Go to Accounting > Customers > Invoices", "steps8"),
        numberedItem("Open INV/25-26/0001 (Lakshmi Devi, Rs 5,500)", "steps8"),
        numberedItem("Click 'Register Payment' button at the top", "steps8"),
        numberedItem("Select Journal: Bank Devika 4501", "steps8"),
        numberedItem("Amount: 5,500 (full payment)", "steps8"),
        numberedItem("Click 'Create Payment'", "steps8"),
        numberedItem("The invoice status changes to 'In Payment' or 'Paid'", "steps8"),

        h3("Step A6: View Branch-Specific Reports"),
        para("Now show the reports while still in Devika Furniture:"),
        
        boldPara("Partner Ledger: ", "Accounting > Reporting > Partner Ledger"),
        para("Shows ONLY Devika's customers and vendors with their balances."),
        
        boldPara("Profit & Loss: ", "Accounting > Reporting > Profit and Loss"),
        para("Shows ONLY Devika's revenue and expenses."),
        
        boldPara("Aged Receivable: ", "Accounting > Reporting > Aged Receivable"),
        para("Shows ONLY Devika's outstanding customer invoices."),
        
        boldPara("General Ledger: ", "Accounting > Reporting > General Ledger"),
        para("Shows ONLY journal entries posted under Devika Furniture."),
        
        importantBox("Key talking point: 'As you can see, when we are in Devika Furniture, all reports show ONLY Devika's data. No other branch's data appears here.'"),

        // ── Part B: KDESIGN INTERIOR ──
        new Paragraph({ children: [new PageBreak()] }),

        h2("5.2 Part B: Demonstrate in KDESIGN INTERIOR"),

        h3("Step B1: Switch to KDESIGN INTERIOR"),
        numberedItem("Click Company Selector", "stepsDemo"),
        numberedItem("Uncheck 'Devika Furniture'", "stepsDemo"),
        numberedItem("Check ONLY 'KDESIGN INTERIOR'", "stepsDemo"),
        numberedItem("Click 'KDESIGN INTERIOR' to make it active", "stepsDemo"),

        h3("Step B2: Show KDESIGN's Data"),
        para("Repeat the same flow:"),
        bullet("Invoices: Suresh Menon (Rs 16,900), Green Valley Residency (Rs 22,900)"),
        bullet("Bills: Kerala Blinds (Rs 11,250), Cochin Laminate (Rs 53,400)"),
        bullet("Payments: Suresh Menon (Rs 10,000 inbound), Kerala Blinds (Rs 11,250 outbound)"),

        h3("Step B3: Show KDESIGN's Reports"),
        para("Open each report and show that it contains ONLY KDESIGN INTERIOR data:"),
        bullet("Partner Ledger → Only Suresh Menon, Green Valley, Kerala Blinds, Cochin Laminate"),
        bullet("P&L → Only KDESIGN's revenue and expenses"),
        bullet("Aged Receivable → Only KDESIGN's outstanding invoices"),

        importantBox("Key talking point: 'When we switch to KDESIGN INTERIOR, all data changes. We now see only KDESIGN's transactions and reports. This is how branch-wise reporting works.'"),

        // ── Part C: Combined View ──
        h2("5.3 Part C: Show Combined (Consolidated) View"),

        h3("Step C1: Switch to Krishnadas Group (Parent)"),
        numberedItem("Click Company Selector", "steps2"),
        numberedItem("Check 'Krishnadas Group' (this auto-includes Devika and KDESIGN)", "steps2"),
        numberedItem("Click 'Krishnadas Group' to make it active", "steps2"),

        h3("Step C2: Show Consolidated Reports"),
        para("Now open the same reports:"),
        
        boldPara("Partner Ledger: ", "Shows ALL partners from ALL branches combined"),
        para("You'll see Anoop Krishnan Nair, Deepa Nambiar, Lakshmi Devi, Suresh Menon, Varghese & Sons, Green Valley, ALL vendors — everything consolidated."),
        
        boldPara("Profit & Loss: ", "Shows total revenue and expenses from all branches"),
        para("Revenue from Krishnadas Group + Devika Furniture + KDESIGN INTERIOR combined."),
        
        boldPara("Balance Sheet: ", "Shows consolidated assets, liabilities, equity"),
        
        importantBox("Key talking point: 'When we select the parent company Krishnadas Group, all reports show CONSOLIDATED data from all branches. This gives the management a complete group-level view.'"),

        warningBox("KDESIGN INTERIOR FURNISHING is a SEPARATE company (different GSTIN). Its data is NEVER included in the Krishnadas Group consolidated view. You must switch to it separately."),

        // ══════════════════════════════════════════════════
        // SECTION 6: QUICK REFERENCE TABLE
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("6. Quick Reference: Company Selector → Report Behavior"),
        
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3000, 2200, 2000, 2160],
          rows: [
            new TableRow({ children: [
              headerCell("Company Selected", 3000), headerCell("Branches Included", 2200), headerCell("Report Scope", 2000), headerCell("Use Case", 2160)
            ]}),
            new TableRow({ children: [
              dataCell("Krishnadas Group", 3000, { bold: true }), dataCell("KG + Devika + KDESIGN", 2200), dataCell("Consolidated", 2000), dataCell("Group-level view", 2160)
            ]}),
            new TableRow({ children: [
              dataCell("Devika Furniture only", 3000, { bold: true, shade: true }), dataCell("Devika only", 2200, { shade: true }), dataCell("Branch-specific", 2000, { shade: true }), dataCell("Branch manager view", 2160, { shade: true })
            ]}),
            new TableRow({ children: [
              dataCell("KDESIGN INTERIOR only", 3000, { bold: true }), dataCell("KDESIGN only", 2200), dataCell("Branch-specific", 2000), dataCell("Branch manager view", 2160)
            ]}),
            new TableRow({ children: [
              dataCell("KDESIGN INT. FURNISHING", 3000, { bold: true, shade: true }), dataCell("Furnishing only", 2200, { shade: true }), dataCell("Company-specific", 2000, { shade: true }), dataCell("Separate entity", 2160, { shade: true })
            ]}),
            new TableRow({ children: [
              dataCell("KG + Devika (no KDESIGN)", 3000, { bold: true }), dataCell("KG + Devika", 2200), dataCell("Partial consolidated", 2000), dataCell("Selective view", 2160)
            ]}),
          ]
        }),

        spacer(),

        h2("6.1 Report Menu Paths"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3000, 6360],
          rows: [
            new TableRow({ children: [headerCell("Report", 3000), headerCell("Menu Path", 6360)] }),
            ...[
              ["Partner Ledger", "Accounting > Reporting > Partner Ledger"],
              ["General Ledger", "Accounting > Reporting > General Ledger"],
              ["Profit and Loss", "Accounting > Reporting > Profit and Loss"],
              ["Balance Sheet", "Accounting > Reporting > Balance Sheet"],
              ["Trial Balance", "Accounting > Reporting > Trial Balance"],
              ["Cash Flow", "Accounting > Reporting > Cash Flow Statement"],
              ["Aged Receivable", "Accounting > Reporting > Aged Receivable"],
              ["Aged Payable", "Accounting > Reporting > Aged Payable"],
              ["Tax Report", "Accounting > Reporting > Tax Report"],
              ["Journal Report", "Accounting > Reporting > Journal Report"],
              ["TCS Report", "Accounting > Reporting > TCS Report"],
              ["TDS Report", "Accounting > Reporting > TDS Report"],
            ].map((r, i) => new TableRow({ children: [
              dataCell(r[0], 3000, { bold: true, shade: i % 2 === 1 }),
              dataCell(r[1], 6360, { shade: i % 2 === 1 })
            ]}))
          ]
        }),

        // ══════════════════════════════════════════════════
        // SECTION 7: COMMON MISTAKES & TROUBLESHOOTING
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("7. Common Mistakes & Troubleshooting"),

        h2("7.1 Mistake: Report shows combined data"),
        boldPara("Problem: ", "Partner Ledger shows data from all branches combined."),
        boldPara("Cause: ", "You are logged into the PARENT company (Krishnadas Group)."),
        boldPara("Fix: ", "Switch to the specific branch using the Company Selector (see Section 3.2 or 3.3)."),

        h2("7.2 Mistake: Report shows no data"),
        boldPara("Problem: ", "No data appears in reports."),
        boldPara("Cause 1: ", "No transactions have been posted for the selected company/branch."),
        boldPara("Cause 2: ", "Date filter is set to wrong period. Check the date range in the report filter."),
        boldPara("Cause 3: ", "You switched to KDESIGN INTERIOR FURNISHING but it has no bills posted (only 2 draft bills)."),

        h2("7.3 Mistake: Invoice created in wrong company"),
        boldPara("Problem: ", "You created an invoice but it appears under the wrong branch."),
        boldPara("Cause: ", "The Company Selector was set to a different company when the invoice was created."),
        boldPara("Fix: ", "Always check the Company Selector BEFORE creating any transaction. The company shown in the selector is the one the invoice will be assigned to."),
        warningBox("Once an invoice is posted, you CANNOT change its company. You would need to cancel and create a new one in the correct company."),

        h2("7.4 Mistake: Payment not visible in branch report"),
        boldPara("Problem: ", "You registered a payment but it doesn't appear in the branch's Partner Ledger."),
        boldPara("Cause: ", "The payment was registered using a journal from a different company (e.g., using Bank Yes 0024 which belongs to Krishnadas Group while signed into Devika Furniture)."),
        boldPara("Fix: ", "Always use the branch-specific journal: Bank Devika 4501 for Devika, Bank KDESIGN 7802 for KDESIGN."),

        // ══════════════════════════════════════════════════
        // SECTION 8: BEST PRACTICES
        // ══════════════════════════════════════════════════
        h1("8. Best Practices for Branch-Wise Accounting"),

        h2("8.1 Before Creating Any Transaction"),
        bullet("ALWAYS check the Company Selector first"),
        bullet("Verify the correct company/branch is active (highlighted)"),
        bullet("Use branch-specific journals (Bank Devika 4501, Bank KDESIGN 7802, etc.)"),

        h2("8.2 For Reporting"),
        bullet("For branch manager: Switch to their specific branch before generating reports"),
        bullet("For group-level management: Use Krishnadas Group (parent) for consolidated view"),
        bullet("Export reports as PDF or Excel for sharing: Use the download button on any report"),
        bullet("Set date filters properly: Always check the fiscal year/period filter at the top of reports"),

        h2("8.3 Journal Configuration"),
        para("Each branch has its own dedicated journals. Use the correct journal for each branch:"),
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3000, 3500, 2860],
          rows: [
            new TableRow({ children: [headerCell("Branch", 3000), headerCell("Bank Journal", 3500), headerCell("Cash Journal", 2860)] }),
            new TableRow({ children: [dataCell("Krishnadas Group", 3000, { bold: true }), dataCell("Bank Yes 0024, Fed 3185, SIB 0388", 3500), dataCell("Cash", 2860)] }),
            new TableRow({ children: [dataCell("Devika Furniture", 3000, { bold: true, shade: true }), dataCell("Bank Devika 4501", 3500, { shade: true }), dataCell("Cash - Devika", 2860, { shade: true })] }),
            new TableRow({ children: [dataCell("KDESIGN INTERIOR", 3000, { bold: true }), dataCell("Bank KDESIGN 7802", 3500), dataCell("Cash - KDESIGN", 2860)] }),
            new TableRow({ children: [dataCell("KDESIGN INT. FURNISHING", 3000, { bold: true, shade: true }), dataCell("Bank", 3500, { shade: true }), dataCell("-", 2860, { shade: true })] }),
          ]
        }),

        h2("8.4 User Access Control"),
        para("Restrict users to see only their branch:"),
        bullet("Branch manager should only have access to their specific branch in user settings"),
        bullet("Group-level managers should have access to the parent company"),
        menuPath("Settings > Users & Companies > Users > [Select user] > Allowed Companies"),

        // ══════════════════════════════════════════════════
        // SECTION 9: SUMMARY
        // ══════════════════════════════════════════════════
        new Paragraph({ children: [new PageBreak()] }),

        h1("9. Summary"),
        
        new Paragraph({
          spacing: { after: 200 },
          border: {
            top: { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" },
            bottom: { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" },
            left: { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" },
            right: { style: BorderStyle.SINGLE, size: 2, color: "2E75B6" }
          },
          children: [
            new TextRun({ text: "The #1 Rule: ", font: "Arial", size: 24, bold: true, color: "1A3C6E" }),
            new TextRun({ text: "The Company Selector controls EVERYTHING. Switch company = switch data.", font: "Arial", size: 24, color: "333333" })
          ]
        }),

        para("Key takeaways:"),
        bullet("Parent company (Krishnadas Group) → Consolidated view of all branches"),
        bullet("Individual branch → Only that branch's data in all reports"),
        bullet("KDESIGN INTERIOR FURNISHING → Separate company, never in KG consolidated view"),
        bullet("All 12 accounting reports follow the same company selector rule"),
        bullet("Always check company selector BEFORE creating invoices, bills, or payments"),
        bullet("Use branch-specific journals for accurate branch-wise tracking"),

        spacer(),
        para("For any questions or issues, contact the implementation team at Infintor Solutions.", { color: "777777" }),
      ]
    }
  ]
});

// Generate
const outputPath = "My learnings/Rohan_Documentation/Branch_Wise_Reporting_Demo_Flow_Guide.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Document saved: ${outputPath}`);
  console.log(`Size: ${(buffer.length / 1024).toFixed(1)} KB`);
});
