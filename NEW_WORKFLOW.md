# RecordsReveal AI-Driven Investigation System

## Overview

**Philosophy:** Give the AI creative freedom to investigate data, then render results in a consistent visual template.

**Old Approach:** 9-step rigid pipeline with forced analysis types
**New Approach:** 2-step flexible workflow with AI-driven journalism

---

## Quick Start

### 1. Investigate a Dataset

```bash
python3 investigate.py data/your_dataset.csv
```

**What happens:**
- **Phase 1 (Ollama):** Analyzes data comprehensively - $0.00
  - Loads CSV with pandas
  - Calculates statistics, finds patterns, detects outliers
  - Identifies most newsworthy findings
  - Returns structured analysis

- **Phase 2 (Claude):** Writes compelling journalism - ~$0.02-0.08
  - Reviews Ollama's analysis
  - Has COMPLETE creative freedom
  - Writes headline, lede, findings (as many as needed)
  - Returns structured investigation JSON

**Output:** `investigation_output/investigation-YYYYMMDD-HHMMSS.json`

### 2. Render to HTML

```bash
python3 render.py investigation_output/investigation-YYYYMMDD-HHMMSS.json
```

**What happens:**
- Loads investigation JSON
- Applies RecordsReveal design system
- Converts markdown (**bold**) to HTML
- Generates stat boxes, findings, pull quotes
- AdSense-compliant layout

**Output:** `investigations/investigation-YYYYMMDD-HHMMSS.html`

### 3. Review and Deploy

Open the HTML file in your browser to review. If you like it, deploy to production.

---

## How It Works

### AI Division of Labor

**Ollama (qwen2.5-coder:7b)** - The Data Analyst
- Cost: $0.00 (local/remote)
- Role: Execute Python code, calculate statistics, find patterns
- Output: Comprehensive data analysis summary

**Claude (Sonnet 4.5)** - The Journalist
- Cost: ~$0.02-0.08 per investigation
- Role: Write compelling narrative with complete creative freedom
- Output: Headline, lede, findings, pull quotes, methodology

### Why This Works Better

**Old Pipeline Problems:**
- Forced analysis types (temporal, geographic, categorical, financial)
- Forced finding structure (exactly 3-4 findings)
- AI had no creative freedom (just filling templates)
- 9 rigid steps with merge/extract/write

**New System Advantages:**
- AI decides what analyses to run
- AI decides how many findings (1-10+)
- AI writes continuously (not filling slots)
- Only 2 steps (investigate → render)
- Same cost (~$0.02-0.08)
- Better journalism

---

## Output Schema

The AI must return JSON matching this schema:

```json
{
  "headline": "12-25 word dramatic headline with specific numbers",
  "lede": "3-5 sentence opening that contradicts conventional wisdom",
  "findings": [
    {
      "title": "Finding Title",
      "body": "Markdown text with **bold numbers**. Multiple paragraphs.",
      "key_stat": "$1.73 or 65.4% or other big number"
    }
  ],
  "pull_quotes": [
    "Compelling 10-20 word quote with a number"
  ],
  "methodology": "Brief explanation of analysis performed",
  "stat_boxes": [
    {
      "label": "Short Label",
      "value": "$850M or 65.4%",
      "context": "Explanatory text"
    }
  ]
}
```

**Flexible Fields:**
- `findings`: AI decides how many (tested: 5 findings worked great)
- `pull_quotes`: 0-5 quotes
- `stat_boxes`: 0-6 stat boxes for visualization

---

## RecordsReveal Style Guide

The AI follows these guidelines when writing:

### Tone
- Direct, conversational, immediate
- Use "you" to make it personal
- Present tense for impact
- Contradict conventional wisdom when possible

### Numbers
- Always **bold** key numbers: **$829 million**, **65.4%**
- Be specific: not "many" but "242 districts"
- Lead with the most surprising number

### Structure
- **Headline:** 12-25 words, dramatic, uses specific numbers
- **Lede:** 3-5 sentences that challenge assumptions
  - Start with relatable scenario
  - Contradict conventional wisdom
  - Use specific numbers
  - Make it immediate and personal

- **Findings:** As many as needed (NOT forced to 3-4)
  - Each reveals ONE major pattern
  - Start with impact: "This is the finding that..."
  - Use 2-3 paragraphs per finding
  - Bold all key numbers
  - Explain WHY this matters

### Examples

**Good Headlines:**
- "Dark Money Spent **$1.9 Billion** Against Candidates in 242 Swing Districts. Opposition Money Outspent Support by Nearly 2-to-1."
- "$829 Million in Dark Money Flooded Swing Districts. We Analyzed 242 Races to Find Who's Really Buying Your Vote."

**Good Lede:**
"You think campaigns are about who you want to win. But in America's most competitive congressional districts, the real money isn't spent convincing you to support someone—it's spent making you hate their opponent. Across **242** swing districts in 2024, dark money groups spent **$1.17 billion** tearing down candidates, compared to just **$679 million** building them up."

---

## Test Results (Dark Money Dataset)

**Old Rigid Pipeline Found:**
- 4 findings (forced: temporal, geographic, categorical, financial)
- Temporal finding was useless ("no data")
- Only basic stats: $829M total, $75M DEM advantage, 65% attack ads

**New AI-Driven System Found:**
- **5 findings** (AI decided)
- Novel insights NOT in rigid pipeline:
  1. **$1.73 attack/support ratio** - Every $1 for support = $1.73 for attacks
  2. **$850M spent AGAINST Republicans** - More than against Democrats ($580M)
  3. **HMP/DCCC/NRCC iron triangle** - Three orgs control battlefield
  4. **3,000+ transactions** in some districts - Industrial-scale operations
  5. **Geographic concentration** patterns

**Quality Comparison:**
- Old: Factual but template-driven
- New: Investigative, surprising, human-readable

**Time:** ~143 seconds (similar to old)
**Cost:** ~$0.02-0.08 (same as old)
**Better:** YES!

---

## File Structure

```
recordsreveal-site/
├── investigate.py          # Main investigation script (Ollama + Claude)
├── render.py              # HTML renderer (template system)
├── investigation_output/   # AI-generated investigation JSONs
│   └── investigation-YYYYMMDD-HHMMSS.json
├── investigations/        # Rendered HTML files
│   └── investigation-YYYYMMDD-HHMMSS.html
├── ollama_helper.py       # Ollama connection utilities
└── data/                  # Your datasets
    └── your_data.csv
```

---

## What Happened to the Old Pipeline?

The old pipeline (`run_full_pipeline.sh`, 9 steps) is still there but deprecated. The new workflow is:

**Old:** Profile → Clean → Analyze (6 types) → Merge → Extract → Write → Generate Image → Build HTML → Preview (9 steps)

**New:** Investigate (Ollama + Claude) → Render (template) (2 steps)

**Why Change:**
- Old: Rigid, forced types, no AI freedom
- New: Flexible, AI-driven, better journalism
- Same cost, same time, better results

---

## FAQ

**Q: Can I still use the old pipeline?**
A: Yes, but the new workflow produces better journalism with less complexity.

**Q: How do I add more datasets?**
A: Just drop CSV files in `data/` and run `investigate.py`. The AI figures out what to analyze.

**Q: What if the AI returns malformed JSON?**
A: The script attempts to clean markdown formatting. If it still fails, check the raw Claude response in the error message.

**Q: Can I customize the HTML template?**
A: Yes! Edit `render.py`. The template is flexible and uses RecordsReveal design system.

**Q: Does this work for AdSense?**
A: Yes! The HTML template includes AdSense placements and meets quality guidelines.

**Q: What about hero images?**
A: Not yet integrated into new workflow. Coming soon (Leonardo.ai integration).

---

## Next Steps

1. **Try it:** `python3 investigate.py data/your_dataset.csv`
2. **Render:** `python3 render.py investigation_output/investigation-*.json`
3. **Review:** Open HTML in browser
4. **Deploy:** Copy to production (preview/approve workflow coming soon)

---

## Technical Notes

**Ollama Connection:**
- Remote server at `192.168.1.153:11434`
- Model: `qwen2.5-coder:7b` (code execution)
- Timeout: 120 seconds
- Cost: $0.00

**Claude API:**
- Model: `claude-sonnet-4-5-20250929` (fallback to 3.5 if unavailable)
- Max tokens: 4000
- Temperature: 1.0 (creative)
- Cost: ~$0.02-0.08 per investigation

**Dependencies:**
```bash
pip install anthropic python-dotenv pandas requests
```

**Environment:**
Create `.env` file with:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Success Metrics

✅ AI has creative freedom
✅ Better journalism than rigid pipeline
✅ Same cost (~$0.02-0.08)
✅ Simpler workflow (2 steps vs 9)
✅ Flexible findings (AI decides how many)
✅ AdSense compliant HTML
✅ RecordsReveal design system
✅ Works with ANY dataset (not just pre-defined types)

---

*Last updated: May 23, 2026*
