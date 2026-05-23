# Complete Prompt Chain: CSV → HTML

This document shows the exact prompts that transform a CSV file into a beautiful investigation page.

---

## Overview

**3 Prompts Transform Raw Data → Publication:**

```
CSV Data
    ↓
PROMPT 1: Ollama Data Analysis (FREE)
    ↓
Statistical Summary
    ↓
PROMPT 2: Claude Journalism (~$0.02-0.08)
    ↓
Investigation JSON (headline, findings, stats)
    ↓
PROMPT 3: Claude Visualization (~$0.02-0.04)
    ↓
Beautiful HTML
    ↓
Wrapped in Template → Final Page
```

**Total Cost:** ~$0.04-0.12 per investigation

---

## PROMPT 1: Ollama Data Analysis

**Model:** `qwen2.5-coder:7b` (Ollama, FREE)  
**Purpose:** Analyze CSV data and find patterns  
**Input:** Raw CSV file  
**Output:** Statistical summary with insights

### The Prompt:

```
You are a data analyst. Analyze this dataset and provide comprehensive statistics.

DATASET: {csv_path}
ROWS: {row_count}
COLUMNS: {column_list}

SAMPLE DATA (first 3 rows):
{sample_data}

COLUMN TYPES:
{data_types}

Please analyze and return a structured summary in this EXACT format:

## DATASET OVERVIEW
- Rows: [number]
- Columns: [number]
- Date range: [if temporal data exists]

## NUMERICAL COLUMNS
For each numeric column, provide:
- Mean, Median, Min, Max
- Outliers (values > 2 std devs from mean)
- Distribution notes

## CATEGORICAL COLUMNS
For each categorical column:
- Unique values count
- Top 5 most frequent values with counts
- Any rare categories worth noting

## KEY PATTERNS
- Correlations between columns (if numeric data)
- Unexpected relationships
- Clusters or natural groupings (if you see them)
- Anomalies or suspicious data points

## MOST NEWSWORTHY FINDINGS
List the 3-5 most surprising or significant patterns you found.
What would make a journalist say "Wow, I need to write about this"?

Be specific with numbers. Focus on patterns that contradict expectations or reveal disparities.
```

### Example Output (Dark Money Dataset):

```
## DATASET OVERVIEW
- Rows: 242
- Columns: 15

## NUMERICAL COLUMNS
total_spending:
  - Mean: $3,425,780
  - Median: $398,396
  - Max: $24,636,157 (CO-08)
  - Outliers: 33 districts > 2 std devs

spending_against:
  - Mean: $2,240,959
  - Median: $13,837
  - Total: $542,311,959
  - Key: 65.4% of all spending is ATTACK ads

## MOST NEWSWORTHY FINDINGS
1. Attack spending ($542M) nearly doubles support spending ($287M)
2. Top 10 districts consume 27.3% of all spending
3. HMP appears in 48 districts with $230M total
4. 3,000+ transactions in some districts (micro-targeting)
5. Republicans face more attack spending ($850M vs $580M DEM)
```

---

## PROMPT 2: Claude Journalism

**Model:** `claude-sonnet-4-5-20250929`  
**Purpose:** Write compelling investigative journalism  
**Input:** Ollama's statistical analysis  
**Output:** Structured investigation JSON

### The Prompt:

```
You are an investigative data journalist for RecordsReveal, a data journalism 
publication known for bold, specific, number-driven stories.

# DATASET ANALYSIS
You just received comprehensive analysis from your data team:

{ollama_analysis}

DATASET: {dataset_name}
RECORDS: {row_count}

# YOUR MISSION
Write a compelling data investigation. You have COMPLETE CREATIVE FREEDOM.

# RECORDSREVEAL STYLE GUIDE

**Tone:**
- Direct, conversational, immediate
- Use "you" to make it personal
- Present tense for impact
- Contradict conventional wisdom when possible

**Numbers:**
- Always use **bold** for key numbers: **$829 million**, **65.4%**
- Be specific: not "many" but "242 districts"
- Lead with the most surprising number

**Structure:**
- Headline: 12-25 words, dramatic, uses specific numbers
- Lede: 3-5 sentences that challenge assumptions
  - Start with relatable scenario
  - Contradict conventional wisdom
  - Use specific numbers and times
  - Make it immediate and personal

- Findings: As many as you need (NOT forced to 3-4)
  - Each finding reveals ONE major pattern
  - Start with impact: "This is the finding that..."
  - Use 2-3 paragraphs per finding
  - Bold all key numbers
  - Explain WHY this matters

**Examples:**

GOOD HEADLINE:
"$829 Million in Dark Money Flooded Swing Districts. We Analyzed 242 Races 
to Find Who's Really Buying Your Vote."

GOOD LEDE:
"If you believe your vote is swayed by the candidate who knocks on your door, 
consider this: in Colorado's 8th district alone, shadow groups you've never 
heard of spent **$24.6 million**—roughly $127 for every single voter—to 
change your mind."

# WHAT TO FOCUS ON
- What's most SURPRISING in the data?
- What contradicts what people THINK they know?
- What reveals DISPARITY or INJUSTICE?
- What would make someone FORWARD this article?
- What matters to REGULAR PEOPLE (not just data nerds)?

# OUTPUT FORMAT
Return ONLY valid JSON:

{
  "headline": "Your compelling headline here",
  "lede": "Your gripping 3-5 sentence lede here",
  "findings": [
    {
      "title": "Finding Title",
      "body": "Full text with **bold numbers**. Multiple paragraphs.",
      "key_stat": "$24.6M or 65.4%"
    }
  ],
  "pull_quotes": [
    "Compelling 10-20 word quote with surprising finding"
  ],
  "methodology": "Brief explanation of analysis",
  "stat_boxes": [
    {
      "label": "Short label",
      "value": "Big number",
      "context": "Brief explanation"
    }
  ]
}

CRITICAL: Return ONLY the JSON. No explanations before or after.
Be bold. Be specific. Find the story that matters.
```

### Example Output:

```json
{
  "headline": "Dark Money Spent $1.9 Billion Against Candidates in 242 Swing Districts. Opposition Money Outspent Support by Nearly 2-to-1.",
  "lede": "You think campaigns are about who you want to win. But in America's most competitive congressional districts, the real money isn't spent convincing you to support someone—it's spent making you hate their opponent. Across **242** swing districts in 2024, dark money groups spent **$1.17 billion** tearing down candidates, compared to just **$679 million** building them up.",
  "findings": [
    {
      "title": "The Negativity Machine: Attack Ads Dominate Every Single District",
      "body": "In every measurable way, dark money has chosen destruction over construction. The median swing district received **$5.3 million** in spending against candidates, compared to just **$3.2 million** spent supporting them. That's a **67% premium** on negativity...",
      "key_stat": "$1.73"
    }
  ],
  "stat_boxes": [
    {
      "label": "Total Dark Money",
      "value": "$1.9B",
      "context": "Spent across 242 swing districts in 2024"
    },
    {
      "label": "Attack Spending Premium",
      "value": "73%",
      "context": "More spent against than for candidates"
    }
  ]
}
```

---

## PROMPT 3: Claude Visualization

**Model:** `claude-sonnet-4-5-20250929`  
**Purpose:** Design stunning HTML visualizations  
**Input:** Investigation JSON from Prompt 2  
**Output:** HTML/CSS/JS content sections

### The Prompt:

```
You are a world-class data visualization designer.

Create STUNNING visualization content for this investigation:

**Headline:** {headline}

**Lede:** {lede}

**Statistics:**
{stat_boxes JSON}

**Findings:**
{findings JSON}

**Pull Quotes:**
{pull_quotes JSON}

# WHAT TO CREATE

Generate beautiful HTML/CSS/JS for these sections ONLY:

1. **Hero Section** - Dramatic headline treatment with the investigation title
2. **KPI Dashboard** - Interactive cards showing the key stats
3. **Charts** - 4 Chart.js visualizations with REAL DATA:
   - Attack vs Support (doughnut chart)
   - Party spending breakdown (bar chart)  
   - Top spenders or geographic (horizontal bars)
   - Trend or distribution (your choice based on data)
4. **Findings Cards** - Each finding as beautiful cards with pull quotes

# DESIGN REQUIREMENTS

- Modern, professional design (dark theme acceptable)
- Use Chart.js 4.x via CDN
- All CSS inline in <style> tags
- All JavaScript inline in <script> tags
- Mobile responsive
- Smooth animations
- Real data from the findings above

# CRITICAL

Return ONLY the HTML content sections (hero, kpis, charts, findings).
Do NOT include:
- <!DOCTYPE html>, <html>, <head>, <body> tags
- Site header/navigation  
- Footer
- Those will be added by the template wrapper

Start directly with the hero <section> and end with the last finding.
Include all <style> and <script> tags needed for YOUR sections.

Make it AMAZING.
```

### Example Output Structure:

```html
<style>
  /* Claude designs custom styles for this investigation */
  .hero-section {
    background: linear-gradient(135deg, #0a0e27 0%, #151932 100%);
    padding: 100px 20px;
  }
  .kpi-card {
    background: white;
    border-radius: 16px;
    transition: transform 0.3s;
  }
  .kpi-card:hover {
    transform: translateY(-4px);
  }
</style>

<section class="hero-section">
  <h1>Dark Money Spent $1.9 Billion Against Candidates...</h1>
  <p class="lede">You think campaigns are about who you want to win...</p>
</section>

<section class="kpi-dashboard">
  <div class="kpi-card">
    <div class="kpi-value">$1.9B</div>
    <div class="kpi-label">Total Dark Money</div>
  </div>
  <!-- More KPI cards -->
</section>

<section class="charts">
  <canvas id="attackSupportChart"></canvas>
  <canvas id="partyChart"></canvas>
  <!-- More charts -->
</section>

<section class="findings">
  <div class="finding-card">
    <h3>The Negativity Machine</h3>
    <p>In every measurable way, dark money has chosen destruction...</p>
  </div>
  <!-- More findings -->
</section>

<script>
// Chart.js initialization with REAL DATA
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Attack Spending', 'Support Spending'],
    datasets: [{
      data: [1170, 679], // Real numbers from findings
      backgroundColor: ['#ef4444', '#3b82f6']
    }]
  }
});
// More chart initializations
</script>
```

---

## Template Wrapper (No AI)

**Purpose:** Add consistent branding  
**Input:** Claude's visualization HTML  
**Output:** Complete page

The template wraps Claude's content with:
- RecordsReveal header (logo, navigation)
- Google Analytics
- Google AdSense
- Footer (branding, links)

```html
<!DOCTYPE html>
<html>
<head>
  <title>{headline} | RecordsReveal</title>
  <!-- Analytics, fonts, Chart.js CDN -->
</head>
<body>
  <header class="site-header">
    <div class="site-name">RECORDSREVEAL</div>
    <!-- Navigation -->
  </header>
  
  <!-- CLAUDE'S VISUALIZATION CONTENT INSERTED HERE -->
  {claude_visualization_html}
  
  <footer>
    <div class="footer-logo">RECORDSREVEAL</div>
    <!-- Links, copyright -->
  </footer>
</body>
</html>
```

---

## Complete Command Sequence

```bash
# Step 1: Investigate (Prompt 1 + Prompt 2)
python3 investigate.py data/your_dataset.csv
# → Uses Ollama for analysis (Prompt 1)
# → Uses Claude for journalism (Prompt 2)
# → Outputs: investigation_output/investigation-TIMESTAMP.json

# Step 2: Render (Prompt 3 + Template)
python3 render_hybrid.py investigation_output/investigation-TIMESTAMP.json
# → Uses Claude for visualization (Prompt 3)
# → Wraps in RecordsReveal template
# → Outputs: investigations/investigation-TIMESTAMP.html

# Step 3: Result
open investigations/investigation-TIMESTAMP.html
# → Professional, branded, amazing data journalism
```

---

## Cost Breakdown

| Step | AI Model | Tokens | Cost |
|------|----------|--------|------|
| Prompt 1: Data Analysis | Ollama (qwen2.5-coder:7b) | ~2000 in + ~3000 out | $0.00 |
| Prompt 2: Journalism | Claude Sonnet 4.5 | ~4000 in + ~2000 out | ~$0.02-0.08 |
| Prompt 3: Visualization | Claude Sonnet 4.5 | ~3000 in + ~8000 out | ~$0.02-0.04 |
| **TOTAL** | | | **~$0.04-0.12** |

---

## Key Design Decisions

1. **Why 3 prompts instead of 1?**
   - Separation of concerns
   - Ollama (free) handles computation
   - Claude handles creativity (where it excels)
   - Each prompt optimized for its task

2. **Why JSON between prompts?**
   - Structured data easier to work with
   - Can validate and transform
   - Template can parse reliably

3. **Why split visualization from template?**
   - Claude gets creative freedom (unique per investigation)
   - Template ensures consistency (same across all)
   - Best of both worlds

4. **Why not one giant prompt?**
   - Would hit token limits
   - Less control over output
   - Higher cost (all in Claude)
   - Harder to debug

---

## Modifying the Prompts

Want to customize? Edit these files:

- **Prompt 1:** `investigate.py` line ~93 (`ollama_prompt`)
- **Prompt 2:** `investigate.py` line ~167 (`claude_prompt`)
- **Prompt 3:** `render_hybrid.py` line ~76 (`prompt`)

Each prompt is clearly marked and can be adjusted for:
- Different tone/style
- Additional analysis types
- Custom visualization requirements
- Specific data domains

---

*Last updated: May 23, 2026*
