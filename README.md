# Odoo 19 — Business Analyst Internship Repository

Study materials, documentation, and tools for an **Odoo 19 Business Analyst Intern** at Infintor Solutions.

---

## 📁 Repository Structure

```
├── docs/                        Documentation & deliverables
│   ├── user-manuals/            Polished .docx user manuals (14 docs)
│   │   ├── WorkCenter.docx
│   │   ├── Subcontracting.docx
│   │   ├── Recruitment.docx
│   │   ├── RealEstate.docx
│   │   └── ...
│   ├── blogs/                   Blog posts for infintor.com (22 files)
│   ├── comparison/              ERP comparison documents
│   └── guides/                  SEO & writing style references
│
├── transcripts/                 Video learning resources
│   ├── manufacturing/           57 Odoo MRP video transcripts
│   └── client-bom/              Client BOM reference materials
│
├── scripts/                     Utility scripts
│   ├── docx-generators/         JS scripts for creating Word documents
│   ├── odoo-automation/         Python scripts for Odoo API & demo setup
│   └── youtube/                 YouTube transcript downloader
│
├── screenshots/                 UI screenshots for documentation
│   └── referral-reports/        Referral module report screenshots
│
├── assets/                      Company assets & misc files
│
├── .agents/                     AI agent configuration & skills
├── CLAUDE.md                    Agent bootstrap instructions
└── odoo-official-docs/          Local Odoo 19 docs clone (gitignored)
```

---

## 📄 Key Documents

| Document | Path | Description |
|----------|------|-------------|
| WorkCenter Guide | `docs/user-manuals/WorkCenter.docx` | Complete work center configuration & management |
| Subcontracting Guide | `docs/user-manuals/Subcontracting.docx` | Subcontractor workflows in Odoo 19 |
| Recruitment Guide | `docs/user-manuals/Recruitment.docx` | Hiring pipeline & applicant tracking |
| Real Estate Module | `docs/user-manuals/RealEstate.docx` | Property management in Odoo 19 |
| Shop Floor Guide | `docs/user-manuals/ShopFloor.docx` | Manufacturing shop floor operations |
| Bank Reconciliation | `docs/blogs/BANK_RECONCILIATION_COMPLETE_GUIDE.md` | Step-by-step bank reconciliation |
| Live Demo Script | `docs/blogs/LIVE_DEMO_PRESENTATION_SCRIPT.docx` | Presentation script for client demos |

---

## 🎥 Manufacturing Transcripts

57 indexed transcripts from Odoo MRP video tutorials covering:
- Bill of Materials, Work Centers, Sub-assemblies
- Costing methods (AVCO, FIFO, Standard)
- Subcontracting, Maintenance, Shop Floor
- Manufacturing planning, lead times, backorders

Start with the index: `transcripts/manufacturing/00_INDEX.txt`

---

## 🛠️ Scripts

### Odoo Automation (`scripts/odoo-automation/`)
Setup scripts for demo environments, data creation, and blog verification against live Odoo instances.

### Document Generators (`scripts/docx-generators/`)
Generate professionally formatted `.docx` files for blog posts and guides.

### YouTube Transcripts (`scripts/youtube/`)
```bash
pip install pytube youtube-transcript-api
python scripts/youtube/youtube_transcript.py "<YouTube URL>"
```

---

## 📋 Agent Configuration

This repo includes AI agent configuration (`.agents/` + `CLAUDE.md`) optimized for:
- Answering Odoo 19 questions using local docs first
- Producing blog posts following Infintor's style guide
- Creating BA deliverables (BRDs, SOPs, user manuals)

See `CLAUDE.md` for full agent bootstrap instructions.

---

**Maintained for:** Rohan Raj — BA Intern, Infintor Solutions
