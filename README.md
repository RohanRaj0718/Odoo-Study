# Odoo 19 — Business Analyst Internship Repository

Study materials, documentation, and tools for **Rohan Raj**, Business Analyst Intern at Infintor Solutions.

Built to support Odoo 19 BA work: answering client questions, producing deliverables, and practising module knowledge.

---

## Repository Structure

```
├── docs/                     All documentation & deliverables
│   ├── user-manuals/         14 polished Word (.docx) user guides
│   ├── blogs/                Blog posts for infintor.com
│   ├── guides/               Style guide & SEO reference
│   ├── comparison/           Odoo vs. traditional ERP
│   └── media/                Screenshots & reference PDFs
│
├── transcripts/              Learning source material
│   ├── manufacturing/        57 Odoo MRP video transcripts (start: 00_INDEX.txt)
│   └── client-bom/           Client 1 BOM reference
│
├── scripts/                  Utility scripts
│   ├── odoo-automation/      Python: demo setup, audit, screenshots
│   ├── docx-generators/      JS (Node): Word document generators
│   └── youtube/              Python: YouTube transcript downloader
│
├── .agents/                  AI agent skills & config
│   ├── blog-style-guide.md   Infintor blog writing rules
│   └── skills/               Supporting agent skills (docx, pdf, xlsx, etc.)
│
├── CLAUDE.md                 Agent bootstrap — read this first every session
├── .gitignore
└── odoo-official-docs/       Odoo 19 docs clone (local only, gitignored)
```

> **For AI agents:** Read `CLAUDE.md` first, then each subfolder's `README.md` before diving into files.

---

## Key Documents

| Document | Path |
|----------|------|
| WorkCenter Guide | `docs/user-manuals/WorkCenter.docx` |
| Subcontracting Guide | `docs/user-manuals/Subcontracting.docx` |
| Recruitment Guide | `docs/user-manuals/Recruitment.docx` |
| Real Estate Module | `docs/user-manuals/RealEstate.docx` |
| Bank Reconciliation | `docs/blogs/BANK_RECONCILIATION_COMPLETE_GUIDE.md` |
| Live Demo Script | `docs/blogs/LIVE_DEMO_PRESENTATION_SCRIPT.docx` |
| Odoo Studio Guide | `docs/blogs/Odoo_Studio_Complete_Guide.docx` |
| Inter-Company Ops | `docs/blogs/Odoo19_Inter_Company_Operations_Guide_V3.docx` |

---

## MRP Transcripts (57 videos)

Start with `transcripts/manufacturing/00_INDEX.txt` — covers BoM, costing, subcontracting, shop floor, maintenance, planning, and lot/serial tracking.

---

## Scripts Quick Start

```bash
# Download a YouTube transcript
python scripts/youtube/youtube_transcript.py "<YouTube URL>"

# Set up an Odoo demo environment
python scripts/odoo-automation/setup_advanced_demo.py

# Generate a blog .docx
node scripts/docx-generators/generate_seo_blog_docx_v2.js
```

---

**Maintained by:** Rohan Raj, Infintor Solutions Intern
