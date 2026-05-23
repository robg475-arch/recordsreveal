# RecordsReveal Complete Workflow
## End-to-End Guide with All Features

---

## Overview

This is the **production-ready workflow** with all features:
- Leonardo.ai hero images
- Google AdSense placements (3 in content + sidebar)
- Sidebar (ads, investigation links, data download)
- Professional layout
- Mobile responsive

**Total time:** ~3-4 minutes per investigation  
**Total cost:** ~$0.04-0.12 per investigation

---

## Quick Start

### 1. Investigate Data (Ollama + Claude)

```bash
python3 investigate.py data/your_dataset.csv
```

**What happens:**
- Ollama analyzes data (free, ~2 minutes)
- Claude writes journalism (~$0.02-0.08, ~30 seconds)
- Outputs: `investigation_output/investigation-YYYYMMDD-HHMMSS.json`

### 2. Render Complete Page (Leonardo + Claude + Template)

```bash
python3 render_complete.py investigation_output/investigation-YYYYMMDD-HHMMSS.json
```

**What happens:**
- Leonardo.ai generates hero image (~$0.00, ~30 seconds)
- Claude designs visualizations (~$0.02-0.04, ~20 seconds)
- Template wraps everything (instant)
- Outputs: `investigations/investigation-YYYYMMDD-HHMMSS.html`

### 3. Review and Deploy

```bash
open investigations/investigation-YYYYMMDD-HHMMSS.html
```

---

## Features Included

### Hero Image (Leonardo.ai)
- Custom illustration per investigation
- Based on headline/content
- 1024x768px, modern editorial style
- Saved to: `images/heroes/`

### Google AdSense
**3 Content Placements:**
- After KPI dashboard
- Between charts and findings
- After findings

**Sidebar Ad:**
- Right column
- Sticky on scroll

### Sidebar Components
1. **Advertisement** - AdSense unit
2. **More Investigations** - Links to other stories
3. **Download Data** - CSV download button
4. **Share This** - X, Facebook, Copy Link buttons

### Layout
- **Main column:** 800px (AI visualization content)
- **Sidebar:** 320px (ads, links, data)
- **Mobile:** Sidebar stacks below content
- **Header/Footer:** Consistent RecordsReveal branding

---

## Cost Breakdown

| Step | Tool | Model/API | Cost | Time |
|------|------|-----------|------|------|
| 1. Data Analysis | Ollama | qwen2.5-coder:7b | $0.00 | ~2 min |
| 2. Journalism | Claude | Sonnet 4.5 | $0.02-0.08 | ~30 sec |
| 3. Hero Image | Leonardo.ai | Phoenix | $0.00* | ~30 sec |
| 4. Visualization | Claude | Sonnet 4.5 | $0.02-0.04 | ~20 sec |
| 5. Template | Python | N/A | $0.00 | instant |
| **TOTAL** | | | **$0.04-0.12** | **~3-4 min** |

*Leonardo.ai offers free tier with credits

---

## File Structure

```
recordsreveal-site/
├── investigate.py              # Step 1: Ollama + Claude journalism
├── render_complete.py          # Step 2: Hero + Viz + Template
├── .env                        # API keys
│   ├── ANTHROPIC_API_KEY
│   ├── LEONARDO_API_KEY
│   └── (GA4, AdSense IDs hardcoded)
├── investigation_output/       # JSON results from investigate.py
│   └── investigation-20260523-131003.json
├── investigations/             # Final HTML pages
│   └── investigation-20260523-131003.html
├── images/heroes/              # Leonardo.ai hero images
│   └── investigation-20260523-131003.jpg
└── data/                       # Your datasets
    └── dark_money_swing_districts_2024.csv
```

---

## Example: Dark Money Investigation

### Step 1: Investigate
```bash
python3 investigate.py data/campaign_finance/dark_money_swing_districts_2024.csv
```

**Output:**
```json
{
  "headline": "Dark Money Spent $1.9 Billion Against Candidates in 242 Swing Districts. Opposition Money Outspent Support by Nearly 2-to-1.",
  "lede": "In 242 congressional swing districts...",
  "findings": [
    {
      "number": 1,
      "title": "The $1.73-to-$1 Attack Advantage",
      "summary": "Opposition spending dominated...",
      "pull_quote": "For every dollar spent supporting..."
    },
    // ... 4 more findings
  ],
  "stat_boxes": [
    {"label": "$1.9B", "description": "Total Dark Money Spent"},
    {"label": "242", "description": "Swing Districts"},
    {"label": "1.73:1", "description": "Attack vs Support Ratio"}
  ]
}
```

### Step 2: Render Complete
```bash
python3 render_complete.py investigation_output/investigation-20260523-131003.json
```

**Output:**
```
╔════════════════════════════════════════════════════════════════════╗
║                  ✅ COMPLETE RENDERING DONE!                   ║
╚════════════════════════════════════════════════════════════════════╝

📁 Output: investigations/investigation-20260523-131003.html
📏 Size: 41.0KB
🖼️  Hero image: images/heroes/investigation-20260523-131003.jpg
💰 Cost: ~$0.02-0.08

✨ FEATURES INCLUDED:
   ✅ Hero image (Leonardo.ai)
   ✅ 3 AdSense placements in content
   ✅ Sidebar with ads
   ✅ Links to other investigations
   ✅ Data download button
   ✅ Share buttons
   ✅ Professional header/footer
```

### Step 3: Review
```bash
open investigations/investigation-20260523-131003.html
```

**What you'll see:**
- Hero image (data visualization illustration)
- KPI dashboard (3 stat boxes)
- 4 Chart.js charts (doughnut, bar, horizontal bar, line)
- 5 findings cards with pull quotes
- Sidebar with ads, links, download button
- Professional header/footer

---

## Alternative: Fast Render (No Hero Image)

If you want to skip Leonardo.ai and render faster:

```bash
python3 render_hybrid.py investigation_output/investigation-YYYYMMDD-HHMMSS.json
```

**Differences:**
- ❌ No hero image
- ❌ No sidebar
- ❌ No AdSense placements
- ✅ Just Claude visualization + template
- ✅ Faster (~30 seconds vs ~60 seconds)
- ✅ Cheaper (~$0.02-0.04 vs ~$0.04-0.08)

---

## Troubleshooting

### Hero image not generating
- Check `LEONARDO_API_KEY` in `.env`
- Verify Leonardo.ai credits available
- Script continues without image if API fails

### AdSense units not showing
- Verify `ca-pub-9045696717764033` is your publisher ID
- AdSense requires approved site (use test mode during development)
- Ads won't show on localhost (deploy to test)

### Charts not rendering
- Check browser console for errors
- Verify Chart.js CDN is accessible
- Claude may have generated invalid chart config (rare)

### Sidebar links broken
- Update sidebar investigation links in `render_complete.py:257-263`
- Point to actual investigation files

---

## Customization

### Change AdSense Publisher ID
Edit `render_complete.py:179`:
```python
data-ad-client="ca-pub-YOUR-ID-HERE"
```

### Modify Sidebar Content
Edit `render_complete.py:257-303`:
- Investigation links
- Download button
- Share buttons

### Adjust Layout Widths
Edit `render_complete.py:83-86`:
```css
.page-layout {
    grid-template-columns: 1fr 320px;  /* main + sidebar */
    gap: 40px;
}
```

### Change Hero Image Style
Edit `render_complete.py:39-47` (Leonardo prompt):
```python
prompt = f"""Your custom style here..."""
```

---

## Next Steps

1. **Test on multiple datasets:** Run investigations on different CSV files
2. **Create data science deep dive:** See `LESSONS_LEARNED.md` for checklist
3. **Deploy to production:** Upload to web host, test AdSense
4. **Monitor performance:** Check GA4 for traffic, AdSense for revenue
5. **Iterate design:** Tweak layouts based on user feedback

---

## 🚨 IMPORTANT: Don't Skip Data Science Page!

Every investigation MUST have a data science deep dive page showing:
- Complete dataset schema
- All statistical calculations
- Python code snippets
- Reproducibility instructions

**See:** `LESSONS_LEARNED.md` for complete checklist and template

---

## Questions?

See `NEW_WORKFLOW.md` for AI architecture details  
See `PROMPT_CHAIN.md` for exact prompts and costs
