# RecordsReveal
## AI-Powered Investigative Data Journalism

**Status:** ✅ Production Ready  
**Last Updated:** May 23, 2026

---

## What is This?

RecordsReveal is a complete system for turning raw government data (CSV files) into professional investigative journalism articles with:
- AI-generated analysis and writing
- Interactive data visualizations
- Statistical deep dives for technical audiences
- Google AdSense monetization
- Professional editorial design

**Time:** ~2-4 hours from CSV to published investigation  
**Cost:** $0.04-0.12 per investigation  
**Quality:** Publication-ready with peer-reviewable methodology

---

## Quick Start

```bash
# 1. Investigate a dataset (3 min)
python3 investigate.py data/your_dataset.csv

# 2. Render complete page (1 min)
python3 render_complete.py investigation_output/investigation-*.json

# 3. Create data science deep dive (1 hour)
cp investigations/dark-money-data-analysis.html investigations/your-topic-data-analysis.html
# Edit: schema, statistics, formulas, code snippets

# 4. Deploy
open investigations/investigation-*.html  # Verify first!
```

**See:** `QUICK_START.md` for detailed 4-hour workflow

---

## Documentation Map

### 🚀 Getting Started
- **`QUICK_START.md`** - 30-second checklist and 4-hour workflow
- **`COMPLETE_WORKFLOW.md`** - End-to-end guide with all features
- **`NEW_WORKFLOW.md`** - System architecture and AI pipeline

### 📚 Reference
- **`LESSONS_LEARNED.md`** - Complete checklist from first investigation (READ THIS!)
- **`PROMPT_CHAIN.md`** - All AI prompts documented word-for-word
- **`methodology.html`** - Public-facing technical methodology page

### 🔧 Technical
- **`investigate.py`** - Ollama data analysis + Claude journalism
- **`render_complete.py`** - Full render (hero, sidebar, ads, viz)
- **`render_hybrid.py`** - Fast render (viz only, no extras)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CSV Dataset                             │
│                  (Public Records)                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: investigate.py                                     │
│  ┌──────────────────────────┐  ┌──────────────────────────┐│
│  │   Ollama (qwen2.5-coder) │→ │  Claude Sonnet 4.5       ││
│  │   • Data analysis        │  │  • Headline & lede       ││
│  │   • Statistics           │  │  • Findings (3-7)        ││
│  │   • Pattern detection    │  │  • Pull quotes           ││
│  │   $0.00                  │  │  $0.02-0.08              ││
│  └──────────────────────────┘  └──────────────────────────┘│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          investigation-YYYYMMDD-HHMMSS.json
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: render_complete.py                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Leonardo.ai     │  │  Claude      │  │  Template     │ │
│  │  Hero image      │→ │  Viz design  │→ │  Wrapper      │ │
│  │  $0.00           │  │  $0.02-0.04  │  │  $0.00        │ │
│  └──────────────────┘  └──────────────┘  └───────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          investigation-YYYYMMDD-HHMMSS.html
          (Complete page with ads, sidebar, hero)
```

---

## What Gets Created

### For Each Investigation:

```
investigations/
├── investigation-YYYYMMDD-HHMMSS.html    # Main article
│   ├── Hero image (Leonardo.ai)
│   ├── KPI dashboard
│   ├── 4 Chart.js visualizations
│   ├── Findings cards
│   ├── 3 AdSense placements
│   └── Sidebar:
│       ├── Advertisement
│       ├── "🔬 For Data Nerds" (orange button)
│       ├── More investigations links
│       ├── Data download
│       └── Share buttons
│
└── YOUR-TOPIC-data-analysis.html         # Data science deep dive
    ├── Complete dataset schema
    ├── Descriptive statistics
    ├── Key finding calculations
    ├── Python code snippets
    ├── Statistical tests (t-tests, Cohen's d)
    ├── Outlier analysis
    ├── Reproducibility instructions
    └── Limitations & caveats

images/heroes/
└── investigation-YYYYMMDD-HHMMSS.jpg     # Hero image

investigation_output/
└── investigation-YYYYMMDD-HHMMSS.json    # Structured data
```

---

## Technology Stack

| Component | Tool | Purpose | Cost |
|-----------|------|---------|------|
| **Data Analysis** | Ollama (qwen2.5-coder:7b) | Statistical analysis, pattern detection | $0.00 |
| **Journalism** | Claude Sonnet 4.5 | Headline, lede, findings, writing | $0.02-0.08 |
| **Visualization** | Claude Sonnet 4.5 | Chart.js designs, KPI dashboards | $0.02-0.04 |
| **Hero Images** | Leonardo.ai Phoenix | Editorial illustrations | $0.00 (free tier) |
| **Charts** | Chart.js 4.x | Interactive data viz | $0.00 (CDN) |
| **Analytics** | Google Analytics 4 | Traffic tracking | $0.00 |
| **Monetization** | Google AdSense | Revenue | Publisher ID: ca-pub-9045696717764033 |

**Total Cost Per Investigation:** $0.04-0.12

---

## Design System

### RecordsReveal Branding

**Colors:**
- **RED:** `#b5271f` - Headlines, CTAs, critical stats
- **ORANGE:** `#d2691e` - Data science callouts, accents
- **CREAM:** `#f8f6f1` - Background
- **INK:** `#1a1a1a` - Body text

**Typography:**
- **Headlines:** Barlow Condensed, 700, uppercase
- **Body:** Barlow, 400, 1.05rem
- **Numbers:** Barlow Condensed, 700, 2.5rem+
- **Code:** JetBrains Mono, 400-500

**Layout:**
- Main content: ~800px
- Sidebar: 320px
- Mobile: Sidebar stacks below
- Synchronized scrolling (no sticky sidebar)

---

## Key Features

### 1. AI-Driven Analysis (Not Rigid Pipeline)
- Ollama explores data freely (no forced analysis types)
- Claude writes journalism based on what data actually shows
- Result: Better insights than rigid statistical templates

### 2. Two-Audience Strategy
- **General audience:** Beautiful visualizations, plain English findings
- **Data scientists:** Full statistical methodology, reproducible code

### 3. Complete Transparency
- All prompts documented (`PROMPT_CHAIN.md`)
- All costs reported
- Raw data downloadable
- Python code provided

### 4. Monetization Ready
- 3 AdSense placements in content
- 1 AdSense placement in sidebar
- Google Analytics tracking
- AdSense-compliant layout

### 5. Professional Quality
- Leonardo.ai hero images (editorial style)
- Chart.js interactive visualizations
- RecordsReveal consistent branding
- Mobile responsive design

---

## Example: Dark Money Investigation

**Dataset:** 242 swing congressional districts, 16 variables, $1.9B in spending

**AI Findings:**
1. $1.73 attack-to-support ratio (opposition spending dominates)
2. $850M spent against GOP vs $580M against Dems (counterintuitive)
3. HMP, DCCC, NRCC iron triangle controls battlegrounds
4. 1,645 average transactions per district (industrial scale)
5. $24.6M max district (Colorado's 8th, $127 per voter)

**Statistical Validation:**
- One-sample t-test: Attack premium p < 0.000001
- Two-sample t-test: Partisan spending p < 0.000001
- Cohen's d = 1.24 (large effect size)
- IQR outlier detection: 8 outlier districts identified

**Output:**
- Main investigation: `investigations/investigation-20260523-133019.html`
- Data science deep dive: `investigations/dark-money-data-analysis.html`
- Hero image: `images/heroes/investigation-20260523-133019.jpg`

**Time:** 3 min automated + 1 hour manual  
**Cost:** $0.08

---

## Requirements

### Software
- Python 3.9+
- Ollama (remote or local)
- Git

### Python Packages
```bash
pip install anthropic python-dotenv requests pandas
```

### API Keys (.env)
```env
ANTHROPIC_API_KEY=sk-ant-...
LEONARDO_API_KEY=...
```

### Services
- Ollama server at `192.168.1.153:11434` (or change in `investigate.py`)
- Google Analytics property `G-7B3KBBGVWE`
- Google AdSense account `ca-pub-9045696717764033`

---

## Workflows

### Complete Investigation (Recommended)

```bash
# 1. Investigate
python3 investigate.py data/your_data.csv

# 2. Render with all features
python3 render_complete.py investigation_output/investigation-*.json

# 3. Create data science page
cp investigations/dark-money-data-analysis.html investigations/your-topic-data-analysis.html
# Edit schema, stats, formulas, code

# 4. Verify
open investigations/investigation-*.html
open investigations/your-topic-data-analysis.html
```

**Time:** ~2-4 hours  
**Cost:** $0.04-0.12

### Fast Investigation (No Extras)

```bash
# 1. Investigate
python3 investigate.py data/your_data.csv

# 2. Fast render (no hero, no sidebar)
python3 render_hybrid.py investigation_output/investigation-*.json

# 3. Verify
open investigations/investigation-*.html
```

**Time:** ~30 minutes  
**Cost:** $0.02-0.08  
**Missing:** Hero image, sidebar, ads, data science page

---

## Quality Control Checklist

**Before publishing:**
- [ ] HTML ends with `</html>` (not truncated)
- [ ] Hero image displays correctly
- [ ] All 4 charts render
- [ ] Sidebar scrolls WITH content (not independently)
- [ ] "🔬 For Data Nerds" button links to data science page
- [ ] Data science page exists and is accurate
- [ ] All statistics manually verified
- [ ] Python code snippets tested
- [ ] No markdown artifacts (```)
- [ ] Mobile responsive (test on phone)
- [ ] CSV download works
- [ ] Share buttons functional

**See:** `LESSONS_LEARNED.md` for complete QA checklist

---

## Project Structure

```
recordsreveal-site/
├── README.md                    # This file
├── QUICK_START.md              # 4-hour workflow
├── LESSONS_LEARNED.md          # Complete checklist (READ THIS!)
├── COMPLETE_WORKFLOW.md        # End-to-end guide
├── NEW_WORKFLOW.md             # System architecture
├── PROMPT_CHAIN.md             # AI prompts documented
│
├── investigate.py              # Step 1: Ollama + Claude journalism
├── render_complete.py          # Step 2: Full render (recommended)
├── render_hybrid.py            # Step 2 alternative: Fast render
├── ollama_helper.py            # Ollama connection utilities
│
├── .env                        # API keys (not in git)
├── requirements.txt            # Python dependencies
│
├── data/                       # Raw datasets (CSV)
│   └── campaign_finance/
│       └── dark_money_swing_districts_2024.csv
│
├── investigation_output/       # AI-generated JSON
│   └── investigation-YYYYMMDD-HHMMSS.json
│
├── investigations/             # Published HTML
│   ├── investigation-YYYYMMDD-HHMMSS.html
│   └── dark-money-data-analysis.html
│
├── images/heroes/              # Leonardo.ai hero images
│   └── investigation-YYYYMMDD-HHMMSS.jpg
│
├── methodology.html            # Public methodology page
├── index.html                  # Homepage
├── investigations.html         # Investigation index
└── about.html                  # About page
```

---

## Cost Analysis

### Per Investigation

| Component | Time | Cost | Notes |
|-----------|------|------|-------|
| Data analysis | ~2 min | $0.00 | Ollama local inference |
| Journalism | ~30 sec | $0.02-0.08 | Claude Sonnet 4.5 |
| Hero image | ~30 sec | $0.00 | Leonardo.ai free tier |
| Visualization | ~20 sec | $0.02-0.04 | Claude Sonnet 4.5 |
| Data science page | ~1 hour | $0.00 | Manual editing |
| **TOTAL** | **~1.5 hours** | **$0.04-0.12** | |

### At Scale

| Volume | Cost | Revenue Potential* |
|--------|------|-------------------|
| 10 investigations/month | $0.40-1.20 | $50-200/month |
| 50 investigations/month | $2.00-6.00 | $250-1,000/month |
| 100 investigations/month | $4.00-12.00 | $500-2,000/month |

*AdSense estimates, varies by traffic

---

## Deployment

### Current Setup
- Static HTML files
- No server-side rendering
- No database required
- Host anywhere (GitHub Pages, Netlify, Vercel, S3)

### Recommended Stack
- **Hosting:** Netlify or Vercel (free tier)
- **Domain:** Custom domain for AdSense approval
- **SSL:** Automatic via host
- **CDN:** Automatic via host

### Deploy Command
```bash
# Build (already HTML, no build step)
# Just git push

git add .
git commit -m "Investigation: [Topic]"
git push origin main

# Netlify/Vercel auto-deploys from main branch
```

---

## Contributing

This is a personal project, but if you want to:
- Report bugs: Open GitHub issue
- Suggest features: Open GitHub issue
- Ask questions: Email data@recordsreveal.com

---

## License

Code: MIT License  
Content: © 2026 RecordsReveal.com  
Data: Public domain (government records)

---

## Roadmap

### Completed ✅
- AI investigation pipeline (Ollama + Claude)
- Complete rendering with all features
- Data science deep dive pages
- Leonardo.ai hero images
- Google AdSense integration
- Sidebar with ads/links/download
- Mobile responsive design
- Statistical validation (t-tests, Cohen's d)
- Complete documentation

### Next ⏳
- Automated data science page generation
- Investigation index auto-updater
- Selenium testing suite
- SEO optimization (meta tags, schema.org)
- Social media auto-posting
- RSS feed generation

---

## Credits

**Built by:** RecordsReveal Team  
**AI Models:**
- Ollama (qwen2.5-coder:7b) - Data analysis
- Anthropic Claude Sonnet 4.5 - Journalism & visualization
- Leonardo.ai Phoenix - Hero images

**Data Sources:** Public government records

**Design Inspiration:** NYT graphics, The Pudding, FiveThirtyEight

---

## Support

**Documentation:**
- Quick start: `QUICK_START.md`
- Complete workflow: `COMPLETE_WORKFLOW.md`
- Lessons learned: `LESSONS_LEARNED.md` ⭐

**Contact:**
- Technical: data@recordsreveal.com
- General: hello@recordsreveal.com
- GitHub: github.com/recordsreveal

---

**Last Investigation:** Dark Money in Swing Districts (May 23, 2026)  
**Next Investigation:** Your dataset here! 🚀

**Time to first publication:** 2-4 hours  
**Cost:** $0.04-0.12  
**Quality:** Peer-reviewable

Start with: `python3 investigate.py data/your_data.csv`
