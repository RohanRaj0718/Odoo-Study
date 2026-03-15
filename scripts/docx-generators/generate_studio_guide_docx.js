const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, LevelFormat,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  TableOfContents, ExternalHyperlink
} = require("docx");

const FONT = "Arial";
const BRAND = "714B67"; // Odoo purple
const ACCENT = "1B4F72";
const LIGHT_BG = "F3EDF7";
const TABLE_HEADER_BG = "714B67";
const TABLE_ALT_BG = "F9F5FB";
const BORDER_COLOR = "CCCCCC";

const PAGE_W = 12240;
const PAGE_H = 15840;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN; // 9360

const border = { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

// Helper: heading
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, font: FONT, size: 32, bold: true, color: BRAND })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: ACCENT })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: "333333" })],
  });
}

// Helper: paragraph
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 100 },
    children: [new TextRun({ text, font: FONT, size: 22, ...opts })],
  });
}

// Helper: bold paragraph
function pb(label, text) {
  return new Paragraph({
    spacing: { before: 60, after: 100 },
    children: [
      new TextRun({ text: label, font: FONT, size: 22, bold: true }),
      new TextRun({ text, font: FONT, size: 22 }),
    ],
  });
}

// Helper: bullet
function bullet(text, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}

// Helper: bullet with bold lead
function bulletBold(label, rest) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [
      new TextRun({ text: label, font: FONT, size: 22, bold: true }),
      new TextRun({ text: rest, font: FONT, size: 22 }),
    ],
  });
}

// Helper: numbered item
function numbered(text, ref = "numbers") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: FONT, size: 22 })],
  });
}

// Helper: callout box
function callout(text, bgColor = LIGHT_BG) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    shading: { fill: bgColor, type: ShadingType.CLEAR },
    indent: { left: 360, right: 360 },
    children: [new TextRun({ text, font: FONT, size: 21, italics: true, color: "444444" })],
  });
}

// Helper: table
function makeTable(headers, rows, colWidths) {
  const totalW = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) =>
      new TableCell({
        borders,
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: TABLE_HEADER_BG, type: ShadingType.CLEAR },
        margins: cellMargins,
        children: [new Paragraph({ children: [new TextRun({ text: h, font: FONT, size: 20, bold: true, color: "FFFFFF" })] })],
      })
    ),
  });
  const dataRows = rows.map((row, ri) =>
    new TableRow({
      children: row.map((cell, ci) =>
        new TableCell({
          borders,
          width: { size: colWidths[ci], type: WidthType.DXA },
          shading: ri % 2 === 1 ? { fill: TABLE_ALT_BG, type: ShadingType.CLEAR } : undefined,
          margins: cellMargins,
          children: [new Paragraph({ children: [new TextRun({ text: cell, font: FONT, size: 20 })] })],
        })
      ),
    })
  );
  return new Table({
    width: { size: totalW, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

// Helper: page break
function pb_break() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ======================= DOCUMENT CONTENT =======================

const children = [];

// TITLE PAGE
children.push(
  new Paragraph({ spacing: { before: 3000 } }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: "Odoo Studio", font: FONT, size: 56, bold: true, color: BRAND })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "Complete Guide for Business Analysts", font: FONT, size: 32, color: ACCENT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BRAND, space: 1 } },
    children: [new TextRun({ text: " ", font: FONT, size: 12 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 100 },
    children: [new TextRun({ text: "Customization | Automation | Reports | Approvals | App Building", font: FONT, size: 22, color: "666666" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 600 },
    children: [new TextRun({ text: "Rohan Raj  |  Business Analyst Intern  |  Infintor Solutions", font: FONT, size: 22, color: "555555" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 100 },
    children: [new TextRun({ text: "March 2026  |  Odoo 19.0", font: FONT, size: 22, color: "555555" })],
  }),
  pb_break(),

  // TABLE OF CONTENTS
  new Paragraph({
    spacing: { before: 200, after: 300 },
    children: [new TextRun({ text: "Table of Contents", font: FONT, size: 32, bold: true, color: BRAND })],
  }),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
  pb_break(),
);

// =========== SECTION 1 ===========
children.push(
  h1("1. What is Odoo Studio?"),
  p("Odoo Studio is a no-code/low-code customization toolbox built into Odoo. It lets you modify any Odoo app — add fields, change views, create automation rules, build PDF reports, set up approval workflows, and even create entirely new apps — without writing a single line of Python or XML."),
  p("Think of it as a visual builder sitting on top of Odoo's technical layer."),
  h2("How to Access Studio"),
  bullet("Click the Toggle Studio icon (pencil icon) from any app view"),
  bullet("Close it by clicking Close in the upper-right corner"),
  h2("Pricing Impact (Critical for BA)"),
  callout("Important: Installing Studio on a Standard plan database automatically upgrades it to the Custom plan — which costs significantly more per user. This is a key cost consideration when recommending Studio to clients."),
  pb_break(),
);

// =========== SECTION 2 ===========
children.push(
  h1("2. What Can Studio Do? (The 7 Pillars)"),
  makeTable(
    ["#", "Capability", "What It Means"],
    [
      ["1", "Fields & Widgets", "Add custom fields (text, number, date, monetary, relational) to any model. Change display using widgets (badges, progress bars, radio buttons, etc.)"],
      ["2", "Views", "Modify Form, List, Kanban, Calendar, Gantt, Pivot, Graph, Map, Cohort, and Search views"],
      ["3", "Models, Modules & Apps", "Create entirely new models (database tables), modules, and apps from scratch with 14 suggested features"],
      ["4", "Automation Rules", "Trigger actions automatically: update records, send emails/SMS/WhatsApp, create activities, execute code — based on field changes, timing, email events, or webhooks"],
      ["5", "PDF Reports", "Edit existing reports (invoices, quotations) or create new ones — change layout, add fields, tables, conditional blocks"],
      ["6", "Approval Rules", "Add multi-step approval workflows to any button — with approvers, groups, exclusive approval, and delegation"],
      ["7", "Security Rules", "Control who can see/edit what using access groups"],
    ],
    [500, 2200, 6660]
  ),
  pb_break(),
);

// =========== SECTION 3 ===========
children.push(
  h1("3. Workflow — Start to End (The Studio Journey)"),

  h2("Phase 1: Open Studio and Understand the Current Model"),
  numbered("Navigate to the app/model you want to customize (e.g., Sales > Orders)", "phase1"),
  numbered("Click the Toggle Studio icon", "phase1"),
  numbered("You are now in Studio mode — the current Form view is editable", "phase1"),
  numbered("Click the Views tab to see all available views for this model", "phase1"),

  h2("Phase 2: Add/Modify Fields"),
  pb("Where: ", "Form view or List view (new fields can ONLY be added on these two views)"),
  p(""),
  h3("Field Types Available (20 Options)"),
  makeTable(
    ["Category", "Fields"],
    [
      ["Simple", "Text, Multiline Text, Integer, Decimal, Monetary, HTML, Date, Date & Time, Checkbox, Selection, Priority, File, Image, Sign"],
      ["Relational", "Many2One, One2Many, Many2Many, Tags, Lines, Related Field"],
    ],
    [2000, 7360]
  ),
  p(""),
  h3("Key Widget Options"),
  makeTable(
    ["Field Type", "Available Widgets"],
    [
      ["Text", "Badge, Copy to Clipboard, Email, Phone, URL"],
      ["Integer", "Percentage Pie, Progress Bar, Handle (drag-to-sort)"],
      ["Decimal", "Percentage, Monetary, Time, Progress Bar"],
      ["Selection", "Badge, Badges, Radio, Status Bar, Priority"],
      ["Checkbox", "Button, Toggle"],
    ],
    [2000, 7360]
  ),
  p(""),
  h3("Field Properties"),
  bulletBold("Invisible: ", "Hide a field conditionally based on filters"),
  bulletBold("Required: ", "Force users to fill in the field before saving"),
  bulletBold("Readonly: ", "Prevent users from modifying the field"),
  bulletBold("Label: ", "Field name displayed on the UI"),
  bulletBold("Help Tooltip: ", "Hover text explaining the field purpose"),
  bulletBold("Widget: ", "Change default appearance or functionality"),
  bulletBold("Placeholder: ", "Example text shown in light gray"),
  bulletBold("Default Value: ", "Pre-filled value when creating a new record"),
  bulletBold("Allow/Forbid visibility to groups: ", "Restrict field access to specific user groups"),
  pb_break(),

  h2("Phase 3: Customize Views"),
  makeTable(
    ["View Type", "Purpose", "Key Settings"],
    [
      ["Form", "Create/edit records", "Add tabs, columns, buttons, smart buttons. Control Can Create/Edit/Delete"],
      ["List", "Overview many records", "Enable Mass Editing, set Sort By, Default Group By, column widths"],
      ["Kanban", "Pipeline/card view", "Quick Create, Default Group By"],
      ["Calendar", "Schedule view", "Color records, set default display (Day/Week/Month/Year)"],
      ["Gantt", "Project timeline", "Row grouping, time scale, color, precision"],
      ["Pivot", "Data analysis", "Row/column grouping, measures, display count"],
      ["Graph", "Charts (bar/line/pie)", "Dimensions, measures, sorting, stacking"],
      ["Map", "Geographical display", "Requires contact field with address"],
      ["Cohort", "Retention/churn analysis", "Measure field, interval, mode (retention/churn)"],
      ["Search", "Filters & grouping", "Custom filters, autocompletion fields"],
      ["Activity", "Activity overview", "XML editing only"],
    ],
    [1600, 2800, 4960]
  ),
  pb_break(),

  h2("Phase 4: Build Automation Rules"),
  p("Menu: Studio > Automations > New"),
  h3("5 Trigger Categories"),
  makeTable(
    ["Trigger", "When It Fires"],
    [
      ["Values Updated", "When a specific field value changes (e.g., Stage is set to Won)"],
      ["Email Events", "On email received/sent"],
      ["Timing Conditions", "Before/after a date field, after creation, after last update"],
      ["Custom", "On create, on create & edit, on deletion, on UI change"],
      ["External (Webhook)", "On receiving a POST request from an external system"],
    ],
    [2500, 6860]
  ),
  p(""),
  h3("Available Actions"),
  makeTable(
    ["Action", "What It Does"],
    [
      ["Update Record", "Change a field value (static, AI-powered, sequence, or computed)"],
      ["Create/Duplicate Record", "Create new records on any model"],
      ["Create Activity", "Schedule activities (calls, meetings, to-dos)"],
      ["Send Email/SMS/WhatsApp", "Automated communications"],
      ["Add/Remove Followers", "Subscribe/unsubscribe contacts"],
      ["Execute Code", "Run custom Python (additional cost on Standard/Custom plans)"],
      ["Send Webhook", "POST data to an external URL"],
      ["Multi Actions", "Chain multiple actions together"],
    ],
    [3000, 6360]
  ),
  p(""),
  callout("Conditions: You can add Before Update Domain (pre-trigger) and Apply on (post-trigger) filters to narrow when rules fire."),
  pb_break(),

  h2("Phase 5: Custom PDF Reports"),
  numbered("Go to Studio > Reports > New", "pdf"),
  numbered("Choose report type: External (company header/footer), Internal (minimal header), or Blank", "pdf"),
  numbered("Edit with the visual editor — add fields, tables, conditional blocks", "pdf"),
  numbered('Use "/" (powerbox) to insert fields, tables, images', "pdf"),
  numbered("Configure: paper format, print menu visibility, group visibility", "pdf"),
  callout("Pro Tip: Always duplicate a standard report before editing it — standard reports reset on module upgrades."),
  p(""),
  h3("Report Layout Options"),
  p("Seven default layouts are available: Light, Boxed, Bold, Striped, Bubble, Wave, and Folder. Each determines header/footer styling and visual theme."),
  p("You can configure: company logo, primary/secondary colors, tagline, footer text, background, font (8 options), and paper format (A4 or US Letter)."),
  pb_break(),

  h2("Phase 6: Set Up Approval Rules"),
  numbered("Open Studio on the relevant view", "approval"),
  numbered('Click the button that needs approval (e.g., "Confirm" on a Purchase Order)', "approval"),
  numbered("Click Add an approval step in the Properties panel", "approval"),
  numbered("Set Approvers (specific users) and/or Approver Group", "approval"),
  numbered("Optional: Enable Exclusive Approval (same user cannot approve multiple steps)", "approval"),
  numbered("Users can Approve, Reject, or Delegate their approval rights", "approval"),
  p(""),
  h3("Approval Features"),
  bulletBold("Exclusive Approval: ", "A user who approves one step cannot approve another step for the same record"),
  bulletBold("Approval Order: ", "Sequential numbering (1, 2, 3...) — higher-step approvers can approve/reject lower steps"),
  bulletBold("Delegation: ", "Approvers can delegate to other users temporarily or permanently"),
  bulletBold("Chatter Tracking: ", "All approval actions are logged in the record's chatter"),
  bulletBold("Conditional Steps: ", "Filter icon next to Approvers field allows conditions for when the step applies"),
  pb_break(),

  h2("Phase 7: Export and Migrate Customizations"),
  bullet("Studio creates a studio_customization module containing all changes"),
  bullet("Export: Toggle Studio from dashboard > Export > Download ZIP"),
  bullet("Import: On destination DB > Studio > Import > Upload ZIP"),
  bullet("Configure which models/data to include in export"),
  bullet("Options: Include Data, Include Demo Data, Attachments, Updatable records"),
  callout("Rule: Source and destination DBs must be on the same Odoo version with same apps installed."),
  pb_break(),
);

// =========== SECTION 4 ===========
children.push(
  h1("4. Building a New App from Scratch"),
  p("Studio > Toggle Studio from dashboard > Create New App"),
  p("When creating a new model or app, you can choose from 14 suggested features that bundle fields, settings, and views:"),
  makeTable(
    ["Feature", "What It Adds"],
    [
      ["Contact Details", "Customer field + Phone + Email + Map view"],
      ["User Assignment", "Responsible user field with avatar (internal users only)"],
      ["Date & Calendar", "Date field + Calendar view"],
      ["Date Range & Gantt", "Start/end dates with daterange widget + Gantt view"],
      ["Pipeline Stages", "Kanban with New/In Progress/Done stages + Priority + Kanban State"],
      ["Tags", "Tag field + auto-created Tag model with access rights"],
      ["Picture", "Image field on top-right of form"],
      ["Lines", "One2Many lines table inside a Tab component"],
      ["Notes", "HTML rich text field (full width)"],
      ["Monetary Value", "Currency-aware money field + Graph + Pivot views"],
      ["Company", "Multi-company Many2One field (for multi-company environments)"],
      ["Custom Sorting", "Drag handle icon for manual record ordering in List view"],
      ["Chatter", "Messages, notes, and scheduled activities"],
      ["Archiving", "Archive/unarchive action + hidden archived records by default"],
    ],
    [2500, 6860]
  ),
  callout("Tip: Features interact with each other. For example, enabling Picture + Pipeline Stages together shows the image in Kanban card layout."),
  pb_break(),
);

// =========== SECTION 5 ===========
children.push(
  h1("5. Odoo Studio in Sales Commission Context"),
  p("Here is how Studio directly enhances the Sales Commission workflow covered in our previous blog:"),
  p(""),

  h2("Scenario 1: Add Custom Fields to Commission Plans"),
  pb("Problem: ", 'Client wants to track "Commission Type" (Cash/Gift Card/Trip) — not available out of the box.'),
  pb("Studio Solution: ", ""),
  numbered("Open Studio on Commission Plan form", "sc1"),
  numbered('Add a Selection field: "Payout Method" with values Cash, Gift Card, Travel', "sc1"),
  numbered('Drag it next to "On Target Commission" field', "sc1"),
  numbered("Save — done, no coding needed", "sc1"),
  p(""),

  h2("Scenario 2: Automated Notification When Commission Exceeds Threshold"),
  pb("Problem: ", "Manager wants an email when any salesperson's commission exceeds Rs. 50,000."),
  pb("Studio Solution: ", "Create an Automation Rule:"),
  bulletBold("Trigger: ", "Values Updated > Commission Amount changed"),
  bulletBold("Condition: ", "Commission Amount > 50000"),
  bulletBold("Action: ", "Send Email to Sales Manager with commission details"),
  p(""),

  h2("Scenario 3: Commission Approval Workflow"),
  pb("Problem: ", "Commission payouts above Rs. 1 lakh need VP Sales approval before payroll processing."),
  pb("Studio Solution: ", "Add approval steps to the Approve button:"),
  bulletBold("Step 1: ", "Sales Manager (for all amounts)"),
  bulletBold("Step 2: ", "VP Sales (conditional: amount > Rs. 1,00,000)"),
  bullet("Enable Exclusive Approval so same person cannot approve both steps"),
  p(""),

  h2("Scenario 4: Custom Commission Report PDF"),
  pb("Problem: ", "Client needs a branded monthly commission statement per salesperson."),
  pb("Studio Solution: ", ""),
  numbered("Create a new External PDF report on the Commission model", "sc4"),
  numbered("Add fields: Salesperson name, plan name, period, target, achieved %, payout amount", "sc4"),
  numbered("Include company logo and footer with bank details", "sc4"),
  numbered("Make it available in Print menu", "sc4"),
  p(""),

  h2("Scenario 5: Auto-Create Activity for Underperformers"),
  pb("Problem: ", "If a salesperson achieves <50% of target, schedule a coaching call."),
  pb("Studio Solution: ", "Automation Rule:"),
  bulletBold("Trigger: ", "Timing Condition > Based on period end date"),
  bulletBold("Condition: ", "Achievement % < 50"),
  bulletBold("Action: ", 'Create Activity > "Performance Review Call" assigned to Team Leader, due in 3 days'),
  pb_break(),
);

// =========== SECTION 6 ===========
children.push(
  h1("6. Advantages of Odoo Studio"),
  makeTable(
    ["Advantage", "Detail"],
    [
      ["No coding required", "BA/Functional consultants can make customizations directly"],
      ["Rapid prototyping", "Show clients changes in real-time during live demos"],
      ["Faster deployment", "Skip the development cycle for simple customizations"],
      ["Export/Import", "Migrate customizations between DBs (dev > staging > production)"],
      ["Audit-friendly", "Approval rules with full chatter tracking and approval entries"],
      ["Low risk", "Changes stored as a separate module; can be rolled back"],
      ["Integrated", "Works with all standard Odoo modules seamlessly"],
    ],
    [2500, 6860]
  ),
  pb_break(),
);

// =========== SECTION 7 ===========
children.push(
  h1("7. Disadvantages of Odoo Studio"),
  makeTable(
    ["Disadvantage", "Detail"],
    [
      ["Cost", "Forces upgrade from Standard to Custom plan (significantly more expensive per user)"],
      ["Performance", "Complex automation rules or too many custom fields can slow down the system"],
      ["Upgrade risk", "Studio customizations may conflict with major version upgrades"],
      ["Limited logic", "Cannot handle complex business logic requiring Python inheritance or ORM overrides"],
      ["Execute Code costs extra", "Custom Python in automation rules incurs additional fees beyond Custom plan"],
      ["No unit testing", "Studio changes cannot be unit tested like custom modules"],
      ["Dependency management", "Export/import requires same apps installed — no automatic dependency tracking"],
      ["Technical debt", "Excessive Studio customizations make the system harder to maintain long-term"],
    ],
    [2800, 6560]
  ),
  pb_break(),
);

// =========== SECTION 8 ===========
children.push(
  h1("8. Alternatives to Odoo Studio"),
  makeTable(
    ["Alternative", "When to Use", "Cost"],
    [
      ["Custom Module Dev", "Complex logic, computed fields, Python overrides, multi-model workflows", "Developer hours"],
      ["Odoo.sh", "Full dev environment with Git, staging, CI/CD for custom modules", "Subscription tier"],
      ["Standard Configuration", "Many things people think need Studio are achievable via Settings", "Free (Standard plan)"],
      ["App Store (Third-party)", "Pre-built solutions for common needs (e.g., advanced commissions)", "Per-app pricing"],
      ["Spreadsheet Integration", "Custom reports/calculations without modifying models", "Included in Odoo"],
      ["XML/Python Custom Dev", "Version-controlled, testable, upgrade-safe customizations", "Developer hours"],
    ],
    [2500, 4860, 2000]
  ),
  p(""),
  h2("BA Decision Framework"),
  p("When evaluating whether to use Studio, follow this decision tree:"),
  numbered("Can it be done with standard configuration? → YES → Use Settings & Config", "decision"),
  numbered("Is it a simple field/view/report change? → YES → Use Studio", "decision"),
  numbered("Does it need complex logic? → YES → Custom Module Development", "decision"),
  numbered("None of the above? → Check Odoo App Store for pre-built solutions", "decision"),
  pb_break(),
);

// =========== SECTION 9 ===========
children.push(
  h1("9. Most Common Real-World Use Cases"),
  p("For Indian SME clients (Infintor Solutions context):"),
  makeTable(
    ["#", "Use Case", "Studio Feature"],
    [
      ["1", "Add GST fields to custom models (GSTIN, HSN Code)", "Custom Fields"],
      ["2", "Purchase Order approval — MD approves orders above Rs. 5 lakhs", "Approval Rules"],
      ["3", "Custom quotation PDF — add terms, bank details, QR code", "PDF Reports"],
      ["4", "Auto-assign tasks when opportunity moves to Won", "Automation Rules"],
      ["5", "Track equipment warranty — alert 30 days before expiry", "Fields + Automation"],
      ["6", "Employee onboarding checklist with pipeline stages", "New App with Pipeline"],
      ["7", "Vendor rating — add rating field visible in vendor form", "Related Fields"],
      ["8", "Custom CRM stages with mandatory fields per stage", "View + Required Fields"],
      ["9", "Inventory alerts — email warehouse manager on low stock", "Automation + Email"],
      ["10", "Interview tracker — HR app with stages, scoring, calendar", "New App from Scratch"],
    ],
    [500, 5360, 3500]
  ),
  pb_break(),
);

// =========== SECTION 10 ===========
children.push(
  h1("10. YouTube Playlist Coverage (14 Videos)"),
  p("The Odoo Studio tutorial playlist typically covers these topics:"),
  makeTable(
    ["Video", "Topic", "Key Takeaway"],
    [
      ["1", "Introduction to Studio", "What Studio is, how to access it, pricing impact"],
      ["2", "Customizing Form Views", "Adding fields, tabs, groups, buttons"],
      ["3", "Customizing List & Kanban Views", "Column editing, grouping, quick create"],
      ["4", "Creating Custom Fields", "All 20 field types + widget options"],
      ["5", "Relational Fields", "Many2One, One2Many, Many2Many, Related Fields"],
      ["6", "Building a Custom App", "Using suggested features, model creation"],
      ["7", "Automation Rules (Part 1)", "Triggers, conditions, basic actions"],
      ["8", "Automation Rules (Part 2)", "Timing conditions, email/SMS, sequences"],
      ["9", "PDF Reports", "Creating & editing reports, conditional blocks"],
      ["10", "Approval Workflows", "Multi-step approvals, delegation, exclusive approval"],
      ["11", "Webhooks", "External triggers, POST API integration"],
      ["12", "Export/Import Studio", "Moving customizations between databases"],
      ["13", "Advanced: Execute Code", "Python in automation rules, available variables"],
      ["14", "Best Practices", "When to use Studio vs. custom development"],
    ],
    [900, 3000, 5460]
  ),
  pb_break(),
);

// =========== SECTION 11 ===========
children.push(
  h1("11. Key BA Takeaways"),
  p(""),
  h3("1. Studio is a Great Demo Tool"),
  p('During client demos, you can add a custom field on-the-fly and say: "Look, we just added exactly what you need. No developer required." This builds client confidence immediately.'),
  p(""),

  h3("2. Always Evaluate Cost First"),
  p("If the client is on Standard plan, Studio forces an upgrade to Custom. Calculate whether the customization justifies the cost increase across all users before recommending Studio."),
  p(""),

  h3("3. Document Every Studio Change"),
  p('Studio changes are invisible in source control. Maintain a separate "Studio Customization Log" document listing every field, view, and automation added — including who requested it and why.'),
  p(""),

  h3("4. Studio is Not Development"),
  p('For complex business rules (e.g., "calculate commission based on payment received within 60 days of invoice, prorated by product category margin"), Studio\'s Update Record action is not sufficient. That needs a custom module.'),
  p(""),

  h3("5. Three-Tier Gap Resolution"),
  p("When a gap exists between client requirements and Odoo standard, classify the resolution as:"),
  bulletBold("Configure: ", "Standard settings change (no Studio needed)"),
  bulletBold("Studio: ", "Field/view/report/automation change (no developer needed)"),
  bulletBold("Custom Dev: ", "Python module required (developer needed)"),
  p(""),
  callout("This three-tier classification shows maturity in your BA recommendations and helps clients understand the cost/complexity tradeoffs."),
  p(""),

  // Source label
  new Paragraph({
    spacing: { before: 400, after: 200 },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: BRAND, space: 8 } },
    children: [
      new TextRun({ text: "Source: ", font: FONT, size: 20, bold: true, color: "666666" }),
      new TextRun({ text: "[Local Docs] — Odoo 19.0 Official Documentation (studio.rst, fields.rst, views.rst, models_modules_apps.rst, automated_actions.rst, approval_rules.rst, pdf_reports.rst)", font: FONT, size: 20, color: "666666", italics: true }),
    ],
  }),
);

// ======================= BUILD DOCUMENT =======================
async function generate() {
  const doc = new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 22 } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, font: FONT, color: BRAND },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: FONT, color: ACCENT },
          paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: "333333" },
          paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 },
        },
      ],
    },
    numbering: {
      config: [
        { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "phase1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "pdf", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "approval", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "decision", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "sc1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        { reference: "sc4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: PAGE_W, height: PAGE_H },
            margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
          },
        },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: BRAND, space: 4 } },
                children: [
                  new TextRun({ text: "Odoo Studio — Complete BA Guide", font: FONT, size: 18, color: BRAND, italics: true }),
                ],
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                border: { top: { style: BorderStyle.SINGLE, size: 2, color: BRAND, space: 4 } },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Rohan Raj | Infintor Solutions | Page ", font: FONT, size: 18, color: "888888" }),
                  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync("Odoo_Studio_Complete_Guide.docx", buffer);
  console.log(`Created: Odoo_Studio_Complete_Guide.docx (${(buffer.length / 1024).toFixed(1)} KB)`);
}

generate().catch((e) => { console.error("Error:", e); process.exit(1); });
