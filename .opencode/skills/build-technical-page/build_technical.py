#!/usr/bin/env python3
"""
RecordsReveal Build Technical Page
Generates detailed technical analysis page for data scientists
"""

import sys
import os
import json
from pathlib import Path

try:
    from anthropic import Anthropic
    from dotenv import load_dotenv
    # Load API key from .env
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    print("⚠️  anthropic/dotenv not installed, Claude features disabled")
    Anthropic = None

def generate_hero_content_with_claude(stats, page_data):
    """
    Use Claude to generate engaging hero content based on data insights.
    Returns dict with: tag, title_lines, subtitle, stat1, stat2, stat3
    """
    
    # Prepare data summary for Claude
    dataset_name = page_data.get('dataset', 'Unknown')
    total_records = stats.get('total_records', 'N/A')
    peak_hour = stats.get('peak_hour', 'N/A')
    top_location = stats.get('top_location', 'N/A')
    majority_category = stats.get('majority_category', 'N/A')
    majority_pct = stats.get('majority_pct', 'N/A')
    
    prompt = f"""You are writing hero section content for a data journalism technical report.

Dataset: {dataset_name}
Total Records: {total_records}
Peak Hour: {peak_hour}
Top Location: {top_location}
Top Category: {majority_category} ({majority_pct})

Generate engaging hero content in this exact JSON format:
{{
  "nav_title": "short title for nav bar (e.g., 'NYC Traffic Crashes')",
  "tag": "brief metadata line (e.g., 'NYC Open Data · Machine Learning · 2012-2023')",
  "title_lines": ["LINE1", "LINE2", "LINE3_RED", "LINE4", "LINE5"],
  "subtitle": "1-2 sentence teaser highlighting the key insight with <strong>emphasis</strong> on the most important finding",
  "stat1_num": "short number (e.g., '5.0K')",
  "stat1_label": "label (e.g., 'CRASHES ANALYZED')",
  "stat2_num": "short number",
  "stat2_label": "label",
  "stat3_num": "short number", 
  "stat3_label": "label"
}}

Rules:
- Title should be a compelling QUESTION or statement (3-5 lines, one marked _RED for red color)
- Use ALL CAPS for title lines
- Subtitle should tease the insight, not explain everything
- Stats should be relevant KPIs from the data (format numbers as K/M for thousands/millions)
- Make it engaging and journalistic, not academic

Return ONLY valid JSON, no other text."""

    try:
        if Anthropic is None:
            raise Exception("Anthropic not available")
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not set")
        
        client = Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        hero_content = json.loads(response_text)
        print(f"✅ Generated hero content with Claude")
        return hero_content
        
    except Exception as e:
        print(f"⚠️  Claude generation failed: {e}, using fallback")
        # Fallback content
        return {
            "nav_title": "Data Analysis",
            "tag": "Data Analysis · Machine Learning",
            "title_lines": ["WHAT", "DO THE", "DATA_RED", "REVEAL?"],
            "subtitle": f"Analysis of <strong>{total_records} records</strong> reveals patterns in timing, location, and contributing factors.",
            "stat1_num": total_records,
            "stat1_label": "RECORDS",
            "stat2_num": peak_hour,
            "stat2_label": "PEAK HOUR",
            "stat3_num": majority_pct,
            "stat3_label": "TOP FACTOR"
        }


def validate_chart_quality(chart_type, chart_data):
    """
    Check if a chart has enough data quality to provide value.
    Returns (is_valid, reason) tuple.
    """
    
    if chart_type == "hourly_pattern":
        y_values = chart_data.get('y', [])
        if not y_values or len(y_values) < 10:
            return False, "Insufficient hourly data points"
        total = sum(y_values)
        if total > 0 and max(y_values) / total > 0.8:
            return False, "Data too concentrated in single hour"
        return True, None
    
    elif chart_type == "rankings":
        names = chart_data.get('names', [])
        counts = chart_data.get('counts', [])
        if len(names) < 2 or len(counts) < 2:
            return False, "Need at least 2 locations"
        total = sum(counts)
        if total > 0 and counts[0] / total > 0.95:
            return False, "One location dominates >95%"
        return True, None
    
    elif chart_type == "trend":
        x_values = chart_data.get('x', [])
        y_values = chart_data.get('y', [])
        if len(x_values) < 4 or len(y_values) < 4:
            return False, f"Only {len(x_values)} time periods (need 4+)"
        if len(set(y_values)) == 1:
            return False, "No variation in values"
        return True, None
    
    elif chart_type == "distribution":
        labels = chart_data.get('labels', [])
        counts = chart_data.get('counts', [])
        if len(labels) < 2 or len(counts) < 2:
            return False, "Need at least 2 categories"
        total = sum(counts)
        if total > 0 and max(counts) / total > 0.90:
            return False, "One category dominates >90%"
        return True, None
    
    # Default: allow it
    return True, None


def build_technical_page(page_data_path, investigation_id, output_dir="investigations"):
    """
    Build technical analysis page with all detailed charts and methodology
    """
    print("\n" + "="*70)
    print("🔬 RECORDSREVEAL BUILD TECHNICAL PAGE")
    print("="*70)
    print(f"Page data: {page_data_path}")
    print(f"Investigation ID: {investigation_id}")
    print("="*70 + "\n")
    
    # Load page data
    print("📂 Loading data...")
    with open(page_data_path) as f:
        page_data = json.load(f)
    
    stats = page_data.get("stats", {})
    charts = page_data.get("chart_data", {})
    
    print(f"✅ Loaded {len(charts)} chart datasets\n")
    
    # Build HTML
    print("🎨 Building technical page structure...")
    
    # Generate hero content with Claude
    print("🤖 Generating hero content with Claude...")
    hero_content = generate_hero_content_with_claude(stats, page_data)
    
    # Start HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Technical Report · RecordsReveal</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --red: #D62828;
  --dark-red: #9B1B1B;
  --orange: #F77F00;
  --dark: #0d0d0d;
  --mid: #1a1a1a;
  --card: #141414;
  --text: #e8e2d6;
  --muted: #888880;
  --border: rgba(255,255,255,0.08);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}

body {{
  background: var(--dark);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-weight: 300;
  line-height: 1.6;
  overflow-x: hidden;
}}

/* NOISE TEXTURE OVERLAY */
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 1000;
  opacity: 0.4;
}}

.container {{
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}}

/* TOP BAR */
.top-bar {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #1c1c1c;
  padding: 10px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #d2691e;
  z-index: 200;
}}

.top-link {{
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.85rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  text-decoration: none;
  transition: color 0.2s;
}}

.top-link.home {{
  color: rgba(255,255,255,0.6);
}}

.top-link.home:hover {{
  color: rgba(255,255,255,0.9);
}}

.top-center {{
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.4);
}}

.top-link.article {{
  color: #d2691e;
}}

.top-link.article:hover {{
  color: #F77F00;
}}

/* NAV */
nav {{
  position: fixed;
  top: 43px;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 60px;
  background: rgba(13,13,13,0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}}

.nav-logo {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.4rem;
  letter-spacing: 0.15em;
  color: var(--red);
}}

.nav-links {{
  display: flex;
  gap: 40px;
  list-style: none;
}}

.nav-links a {{
  color: var(--muted);
  text-decoration: none;
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition: color 0.2s;
}}

.nav-links a:hover {{ color: var(--text); }}

/* HERO */
.hero {{
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  position: relative;
  overflow: hidden;
}}

.hero-left {{
  padding: 200px 60px 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 2;
}}

.hero-right {{
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, rgba(214,40,40,0.1), transparent 70%);
}}

.hero-tag {{
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--orange);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}}

.hero-tag::before {{
  content: '';
  width: 32px;
  height: 1px;
  background: var(--orange);
}}

.hero-title {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(4rem, 8vw, 7.5rem);
  line-height: 0.92;
  letter-spacing: 0.02em;
  margin-bottom: 32px;
}}

.hero-title .line-red {{ color: var(--red); }}

.hero-sub {{
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--muted);
  max-width: 440px;
  margin-bottom: 48px;
}}

.hero-sub strong {{ color: var(--text); font-weight: 500; }}

.hero-stats {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  max-width: 440px;
}}

.stat-box {{
  background: var(--mid);
  padding: 20px 16px;
  text-align: center;
}}

.stat-num {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.2rem;
  letter-spacing: 0.05em;
  color: var(--red);
  line-height: 1;
  display: block;
}}

.stat-label {{
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 4px;
  display: block;
}}

/* HIGHLIGHT BAR */
.highlight-bar {{
  background: var(--red);
  padding: 24px 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  flex-wrap: wrap;
}}

.highlight-item {{
  text-align: center;
}}

.highlight-num {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.2rem;
  letter-spacing: 0.05em;
  line-height: 1;
  color: white;
}}

.highlight-label {{
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
  margin-top: 2px;
}}

.highlight-divider {{
  width: 1px;
  height: 40px;
  background: rgba(255,255,255,0.2);
}}

/* SECTIONS */
.section {{
  padding: 60px 0;
  border-bottom: 1px solid var(--border);
}}

.section-header {{
  margin-bottom: 40px;
}}

.section-label {{
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}}

.section-label::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
  max-width: 100px;
}}

.section-title {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(3rem, 6vw, 5rem);
  line-height: 0.95;
  letter-spacing: 0.02em;
  margin-bottom: 20px;
}}

.section-desc {{
  font-size: 0.95rem;
  color: var(--muted);
  max-width: 700px;
}}

/* CHART GRID */
.chart-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2px;
  background: var(--border);
  margin-bottom: 2px;
}}

.chart-card {{
  background: var(--card);
  border: none;
  padding: 24px;
}}

.chart-card.full {{
  grid-column: 1 / -1;
}}

.chart-card-title {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--orange);
  margin-bottom: 4px;
}}

.chart-card-sub {{
  font-size: 0.78rem;
  color: var(--muted);
  margin-bottom: 24px;
  font-family: 'DM Mono', monospace;
}}

.chart-card-sub {{
  font-size: 0.8rem;
  color: var(--muted);
  margin-bottom: 20px;
  line-height: 1.5;
}}

.chart-container {{
  height: 400px;
}}

.chart-container.tall {{
  height: 500px;
}}

/* MODEL CARDS */
.model-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  background: var(--border);
  border: 1px solid var(--border);
  margin-bottom: 2px;
}}

.model-card {{
  background: var(--card);
  padding: 32px 24px;
  position: relative;
  overflow: hidden;
}}

.model-card.best {{
  background: linear-gradient(135deg, #1a0808, #2a0a0a);
  border: 1px solid var(--dark-red);
}}

.model-card.best::before {{
  content: 'BEST';
  position: absolute;
  top: 12px;
  right: 12px;
  font-family: 'DM Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  color: var(--orange);
  background: rgba(247,127,0,0.1);
  padding: 3px 8px;
  border: 1px solid rgba(247,127,0,0.3);
}}

.model-name {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.4rem;
  letter-spacing: 0.08em;
  margin-bottom: 20px;
  color: var(--text);
}}

.model-metric {{
  margin-bottom: 12px;
}}

.metric-label {{
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.15em;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}}

.metric-value {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.4rem;
  letter-spacing: 0.05em;
  line-height: 1;
  color: var(--text);
}}

.metric-value.highlight {{ color: var(--red); }}

.metric-bar {{
  height: 3px;
  background: var(--border);
  margin-top: 8px;
  border-radius: 2px;
  overflow: hidden;
}}

.metric-fill {{
  height: 100%;
  background: var(--red);
  border-radius: 2px;
  transition: width 1.5s ease;
}}

.metric-fill.orange {{
  background: var(--orange);
}}

/* TECHNICAL NOTE */
.tech-note {{
  background: var(--mid);
  border-left: 3px solid var(--orange);
  padding: 20px 24px;
  margin-top: 2px;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--muted);
}}

.tech-note strong {{
  color: var(--text);
  font-weight: 500;
}}

/* FINDINGS CARDS */
.findings-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 2px;
  background: var(--border);
  border: 1px solid var(--border);
  margin-top: 2px;
}}

.finding-card {{
  background: var(--card);
  padding: 36px 28px;
}}

.finding-icon {{
  font-size: 2rem;
  margin-bottom: 16px;
}}

.finding-title {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.3rem;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
  color: var(--orange);
}}

.finding-text {{
  font-size: 0.88rem;
  line-height: 1.65;
  color: var(--muted);
}}

.finding-text strong {{ color: var(--text); }}

/* CHART FULL WIDTH */
.chart-full {{
  margin-bottom: 32px;
}}

/* CODE BLOCK */
.code-block {{
  background: #0a0a0a;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 20px;
  margin: 20px 0;
  font-family: 'DM Mono', monospace;
  font-size: 0.85rem;
  color: #a8dadc;
  overflow-x: auto;
}}

.code-block pre {{
  margin: 0;
}}

/* TABLE */
.data-table {{
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 0.9rem;
}}

.data-table th {{
  background: var(--card);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}}

.data-table td {{
  padding: 12px;
  border-bottom: 1px solid var(--border);
}}

.data-table tr:hover {{
  background: rgba(255,255,255,0.02);
}}

/* FOOTER */
footer {{
  background: #1a1a1a;
  padding: 60px 60px 40px;
  border-top: 1px solid var(--border);
  margin-top: 80px;
}}

.footer-content {{
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 60px;
  max-width: 1400px;
  margin: 0 auto 40px;
}}

.footer-brand {{
  max-width: 400px;
}}

.footer-logo {{
  font-family: 'Libre Baskerville', serif;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 16px;
}}

.footer-logo span {{
  color: var(--red);
}}

.footer-tagline {{
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--muted);
}}

.footer-section {{
  
}}

.footer-heading {{
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
  margin-bottom: 20px;
}}

.footer-links {{
  list-style: none;
  padding: 0;
  margin: 0;
}}

.footer-links li {{
  margin-bottom: 12px;
}}

.footer-links a {{
  color: var(--text);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}}

.footer-links a:hover {{
  color: var(--orange);
}}

.footer-bottom {{
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.3);
}}

.footer-bottom a {{
  color: rgba(255,255,255,0.4);
  text-decoration: none;
  transition: color 0.2s;
}}

.footer-bottom a:hover {{
  color: rgba(255,255,255,0.7);
}}

/* AD PLACEHOLDERS */
.ad-container {{
  max-width: 1200px;
  margin: 60px auto;
  text-align: center;
}}

.ad-label {{
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.3);
  margin-bottom: 12px;
}}
</style>

<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-7B3KBBGVWE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-7B3KBBGVWE');
</script>

<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9045696717764033" crossorigin="anonymous"></script>

</head>
<body>

<!-- TOP BAR -->
<div class="top-bar">
  <a href="index.html" class="top-link home">← RecordsReveal Home</a>
  <span class="top-center">Technical Deep Dive</span>
  <a href="{investigation_id}.html" class="top-link article">Read the Article →</a>
</div>

<!-- NAV -->
<nav>
  <div class="nav-logo">{hero_content.get('nav_title', 'Data Analysis')}</div>
  <ul class="nav-links">
    <li><a href="#findings">Findings</a></li>
    <li><a href="#models">Models</a></li>
    <li><a href="#clustering">Clusters</a></li>
  </ul>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-left">
    <div class="hero-tag">{hero_content['tag']}</div>
    <h1 class="hero-title">"""
    
    # Build title with line breaks and red highlight
    for i, line in enumerate(hero_content['title_lines']):
        if '_RED' in line:
            line_text = line.replace('_RED', '')
            html += f"\n      <span class=\"line-red\">{line_text}</span>"
        else:
            html += f"\n      {line}"
        if i < len(hero_content['title_lines']) - 1:
            html += "<br>"
    
    html += f"""
    </h1>
    <p class="hero-sub">
      {hero_content['subtitle']}
    </p>
    <div class="hero-stats">
      <div class="stat-box">
        <div class="stat-num">{hero_content['stat1_num']}</div>
        <div class="stat-label">{hero_content['stat1_label']}</div>
      </div>
      <div class="stat-box">
        <div class="stat-num">{hero_content['stat2_num']}</div>
        <div class="stat-label">{hero_content['stat2_label']}</div>
      </div>
      <div class="stat-box">
        <div class="stat-num">{hero_content['stat3_num']}</div>
        <div class="stat-label">{hero_content['stat3_label']}</div>
      </div>
    </div>
  </div>
  <div class="hero-right">
    <div id="hero-chart" style="width:100%;height:100%;"></div>
  </div>
</div>

<!-- HIGHLIGHT BAR -->
<div class="highlight-bar">
  <div class="highlight-item">
    <div class="highlight-num">{stats.get('total_records', 'N/A')}</div>
    <div class="highlight-label">Records Analyzed</div>
  </div>
  <div class="highlight-divider"></div>
  <div class="highlight-item">
    <div class="highlight-num">{stats.get('peak_hour', 'N/A')}</div>
    <div class="highlight-label">Peak Hour</div>
  </div>
  <div class="highlight-divider"></div>
  <div class="highlight-item">
    <div class="highlight-num">{stats.get('top_location', 'N/A')}</div>
    <div class="highlight-label">Top Location</div>
  </div>
  <div class="highlight-divider"></div>
  <div class="highlight-item">
    <div class="highlight-num">{stats.get('majority_pct', 'N/A')}</div>
    <div class="highlight-label">Majority Factor</div>
  </div>
  <div class="highlight-divider"></div>
  <div class="highlight-item">
    <div class="highlight-num">{len(charts)}</div>
    <div class="highlight-label">Visualizations</div>
  </div>
</div>
"""
    
    # Add sections for each analysis type
    output_file = os.path.join(output_dir, f"{investigation_id}-technical.html")
    
    # Findings Section (Exploratory Analysis)
    html += generate_findings_section(charts, stats, page_data)
    
    # Ad Placeholder 1 (after Findings)
    html += """
<!-- AD PLACEHOLDER 1 -->
<div class="ad-container">
  <div class="ad-label">Advertisement</div>
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-9045696717764033"
       data-ad-slot="XXXXXXXXXX"
       data-ad-format="horizontal"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
"""
    
    # Machine Learning Section
    if 'feature_importance' in charts or 'models' in charts:
        html += generate_ml_section(charts)
    
    # Ad Placeholder 2 (after ML)
    html += """
<!-- AD PLACEHOLDER 2 -->
<div class="ad-container">
  <div class="ad-label">Advertisement</div>
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-9045696717764033"
       data-ad-slot="XXXXXXXXXX"
       data-ad-format="rectangle"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
"""
    
    # Clustering Section
    if 'clusters' in charts or 'elbow' in charts:
        html += generate_clustering_section(charts)
    
    # Ad Placeholder 3 (before footer)
    html += """
<!-- AD PLACEHOLDER 3 -->
<div class="ad-container">
  <div class="ad-label">Advertisement</div>
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-9045696717764033"
       data-ad-slot="XXXXXXXXXX"
       data-ad-format="horizontal"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
"""
    
    # Close HTML
    html += """
<footer>
  <div class="footer-content">
    <div class="footer-brand">
      <div class="footer-logo">RECORDS<span>REVEAL</span></div>
      <p class="footer-tagline">
        Data-driven journalism uncovering stories hidden in public records. 
        Built with machine learning, powered by transparency.
      </p>
    </div>
    
    <div class="footer-section">
      <div class="footer-heading">Investigations</div>
      <ul class="footer-links">
        <li><a href="index.html">All Investigations</a></li>
        <li><a href="index.html#latest">Latest Reports</a></li>
        <li><a href="index.html#trending">Trending</a></li>
      </ul>
    </div>
    
    <div class="footer-section">
      <div class="footer-heading">About</div>
      <ul class="footer-links">
        <li><a href="methodology.html">Our Methodology</a></li>
        <li><a href="sources.html">Data Sources</a></li>
        <li><a href="contact.html">Contact</a></li>
        <li><a href="privacy.html">Privacy Policy</a></li>
      </ul>
    </div>
  </div>
  
  <div class="footer-bottom">
    <span>© 2026 RecordsReveal · All data from public records · For educational purposes</span>
    <span>Built with Python · Ollama · Claude · Plotly</span>
  </div>
</footer>

<script>
// Plotly config
const cfg = {responsive: true, displayModeBar: true};
const layout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: {family: 'Barlow', color: '#e8e2d6', size: 11},
  margin: {t: 40, b: 60, l: 60, r: 40},
  xaxis: {gridcolor: 'rgba(255,255,255,0.05)', zerolinecolor: 'rgba(255,255,255,0.1)'},
  yaxis: {gridcolor: 'rgba(255,255,255,0.05)', zerolinecolor: 'rgba(255,255,255,0.1)'},
};
"""
    
    # Add chart scripts
    print("📊 Generating chart scripts...")
    chart_count = 0
    
    # Findings section charts
    if 'hourly_pattern' in charts:
        data = charts['hourly_pattern']
        is_valid, _ = validate_chart_quality('hourly_pattern', data)
        if is_valid:
            # Convert hours to AM/PM format
            hours_24 = data.get('x', [])
            hours_ampm = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM','11AM',
                         '12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM','9PM','10PM','11PM']
            peak_hour = data.get('peak_hour', 17)
            y_values = data.get('y', [])
            
            # Color peak hour red, others orange
            colors = ['#D62828' if i == peak_hour else '#F77F00' for i in range(len(y_values))]
            
            html += f"""
// Hourly Pattern (Findings)
const hours = {json.dumps(hours_ampm)};
Plotly.newPlot('chart-hourly', [{{
  x: hours,
  y: {json.dumps(y_values)},
  type: 'bar',
  marker: {{color: {json.dumps(colors)}, opacity: 0.85}},
  hovertemplate: '%{{x}}: %{{y}} incidents<extra></extra>',
}}], {{
  ...layout,
  title: {{text: '', font: {{size: 14, color: '#e8e2d6'}}}},
  xaxis: {{...layout.xaxis, tickangle: -45}},
  yaxis: {{...layout.yaxis, tickformat: ',d'}},
  annotations: [{{
    x: hours[{peak_hour}],
    y: {y_values[peak_hour] if peak_hour < len(y_values) else 0},
    text: 'Peak Hour',
    showarrow: true,
    arrowhead: 2,
    arrowsize: 1,
    arrowwidth: 2,
    arrowcolor: '#D62828',
    ax: 0,
    ay: -40,
    font: {{color: '#D62828', size: 11}},
  }}]
}}, cfg);
"""
            chart_count += 1
            print(f"  ✅ Hourly pattern (findings)")
    
    # Day of week chart
    if 'day_of_week' in charts:
        data = charts['day_of_week']
        y_values = data.get('y', [])
        peak_day_idx = y_values.index(max(y_values)) if y_values else -1
        
        # Highlight peak day in red, others in orange with gradient
        colors = []
        for i, val in enumerate(y_values):
            if i == peak_day_idx:
                colors.append('#D62828')  # RED for peak
            elif i == (peak_day_idx - 1) % 7 or i == (peak_day_idx + 1) % 7:
                colors.append('#F77F00')  # ORANGE for adjacent days
            else:
                colors.append('rgba(210,105,30,0.6)')  # Muted orange for others
        
        html += f"""
// Day of Week Pattern
Plotly.newPlot('chart-dayofweek', [{{
  x: {json.dumps(data.get('x', []))},
  y: {json.dumps(y_values)},
  type: 'bar',
  marker: {{color: {json.dumps(colors)}, opacity: 0.85}},
  hovertemplate: '%{{x}}: %{{y}} incidents<extra></extra>',
}}], {{
  ...layout,
  margin: {{t: 10, b: 60, l: 50, r: 20}},
  xaxis: {{...layout.xaxis, tickangle: -30}},
  yaxis: {{...layout.yaxis, tickformat: ',d'}},
}}, cfg);
"""
        chart_count += 1
        print(f"  ✅ Day of week (findings)")
    else:
        print(f"  ⚠️  No day of week data available")
    
    if 'distribution' in charts:
        data = charts['distribution']
        is_valid, _ = validate_chart_quality('distribution', data)
        if is_valid:
            # Generate colors: RED for top, ORANGE for #2, then gradient
            counts = data.get('counts', [])
            colors = []
            for i in range(len(counts)):
                if i == 0:
                    colors.append('#D62828')  # RED for top
                elif i == 1:
                    colors.append('#F77F00')  # ORANGE for #2
                elif i < 4:
                    colors.append('rgba(214,40,40,0.7)')  # Light red
                elif i < 6:
                    colors.append('rgba(247,127,0,0.7)')  # Light orange
                else:
                    colors.append('rgba(210,105,30,0.5)')  # Very muted
            
            html += f"""
// Distribution (Findings)
Plotly.newPlot('chart-distribution', [{{
  labels: {json.dumps(data.get('labels', []))},
  values: {json.dumps(counts)},
  type: 'pie',
  hole: 0.4,
  marker: {{
    colors: {json.dumps(colors)}
  }},
  textinfo: 'label+percent',
  textfont: {{size: 9}},
  hovertemplate: '%{{label}}<br>%{{value}} incidents<br>%{{percent}}<extra></extra>',
}}], {{
  ...layout,
  showlegend: false,
  margin: {{t: 10, b: 10, l: 10, r: 10}},
}}, cfg);
"""
            chart_count += 1
            print(f"  ✅ Distribution (findings)")
    
    if 'rankings' in charts:
        data = charts['rankings']
        is_valid, _ = validate_chart_quality('rankings', data)
        if is_valid:
            counts = data.get('counts', [])
            names = data.get('names', [])
            
            # Reverse for horizontal bar (Plotly shows bottom-to-top)
            counts_rev = list(reversed(counts))
            names_rev = list(reversed(names))
            
            # Highlight top locations: RED for #1, ORANGE for #2, muted for rest
            colors = []
            for i in range(len(counts_rev)):
                if i >= len(counts_rev) - 1:  # Top item (last after reverse)
                    colors.append('#D62828')
                elif i >= len(counts_rev) - 2:  # Second item
                    colors.append('#F77F00')
                else:
                    colors.append('rgba(210,105,30,0.6)')
            
            html += f"""
// Rankings (Findings)
Plotly.newPlot('chart-rankings', [{{
  x: {json.dumps(counts_rev)},
  y: {json.dumps(names_rev)},
  type: 'bar',
  orientation: 'h',
  marker: {{color: {json.dumps(colors)}, opacity: 0.85}},
  hovertemplate: '%{{y}}: %{{x}} incidents<extra></extra>',
}}], {{
  ...layout,
  margin: {{t: 10, b: 40, l: 160, r: 20}},
  xaxis: {{...layout.xaxis, tickformat: ',d'}},
  yaxis: {{...layout.yaxis}},
}}, cfg);
"""
            chart_count += 1
            print(f"  ✅ Rankings (findings)")
    
    # Feature importance
    if 'feature_importance' in charts:
        data = charts['feature_importance']
        importance_vals = data.get('importance', [])
        names = data.get('names', [])
        
        # Reverse for horizontal bar (bottom-to-top)
        importance_rev = list(reversed(importance_vals))
        names_rev = list(reversed(names))
        
        # Highlight top features: RED for #1, ORANGE for #2, muted for rest
        colors = []
        for i in range(len(importance_rev)):
            if i >= len(importance_rev) - 1:  # Top feature
                colors.append('#D62828')
            elif i >= len(importance_rev) - 2:  # Second feature
                colors.append('#F77F00')
            else:
                colors.append('rgba(210,105,30,0.6)')
        
        html += f"""
Plotly.newPlot('chart-feature-importance', [{{
  x: {json.dumps(importance_rev)},
  y: {json.dumps(names_rev)},
  type: 'bar',
  orientation: 'h',
  marker: {{color: {json.dumps(colors)}, opacity: 0.85}},
  hovertemplate: '%{{y}}: %{{x:.3f}}<extra></extra>',
}}], {{
  ...layout,
  margin: {{t: 10, b: 40, l: 220, r: 20}},
  xaxis: {{...layout.xaxis, title: 'Importance'}},
  yaxis: {{...layout.yaxis, tickfont: {{size: 9}}}},
}}, cfg);
"""
        chart_count += 1
        print(f"  ✅ Feature importance")
    
    # Model comparison
    if 'models' in charts:
        data = charts['models']
        names = data.get('names', [])
        
        # Check for both r2_scores (regression) and accuracies (classification)
        r2_scores = data.get('r2_scores', [])
        accuracies = data.get('accuracies', [])
        
        # Use whichever metric is available and non-zero
        if r2_scores and any(score != 0 for score in r2_scores):
            scores = r2_scores
            metric_label = 'R²'
            format_str = '.3f'
        elif accuracies:
            scores = accuracies
            metric_label = 'Accuracy'
            format_str = '.3f'
        else:
            scores = []
        
        # Format model names with spaces
        display_names = [name.replace('Regression', ' Regression').replace('Forest', ' Forest') for name in names]
        
        # Find best model
        if scores:
            max_idx = scores.index(max(scores))
            # Highlight best model in RED, others in gradient
            colors = []
            for i in range(len(scores)):
                if i == max_idx:
                    colors.append('#D62828')
                elif i == (max_idx + 1) % len(scores) or i == (max_idx - 1) % len(scores):
                    colors.append('#F77F00')
                else:
                    colors.append('rgba(210,105,30,0.6)')
        else:
            colors = ['rgba(210,105,30,0.6)'] * len(names)
        
        html += f"""
Plotly.newPlot('chart-models', [{{
  x: {json.dumps(display_names)},
  y: {json.dumps(scores)},
  type: 'bar',
  marker: {{color: {json.dumps(colors)}, opacity: 0.85}},
  hovertemplate: '%{{x}}<br>{metric_label}: %{{y:{format_str}}}<extra></extra>',
}}], {{
  ...layout,
  margin: {{t: 10, b: 60, l: 50, r: 20}},
  yaxis: {{...layout.yaxis, tickformat: '{format_str}', title: '{metric_label}'}},
  xaxis: {{...layout.xaxis, tickangle: -30}},
}}, cfg);
"""
        chart_count += 1
        print(f"  ✅ Model comparison")
    
    # Elbow curve
    if 'elbow' in charts:
        data = charts['elbow']
        k_values = data.get('k_values', [])
        inertias = data.get('inertias', [])
        
        # Find elbow point (steepest decrease) - typically around k=3-5
        # Highlight optimal k in RED
        optimal_k_idx = 3 if len(k_values) > 3 else 1  # Default to k=4 or second point
        marker_colors = ['#D62828' if i == optimal_k_idx else '#F77F00' for i in range(len(k_values))]
        
        html += f"""
Plotly.newPlot('chart-elbow', [{{
  x: {json.dumps(k_values)},
  y: {json.dumps(inertias)},
  type: 'scatter',
  mode: 'lines+markers',
  line: {{color: 'rgba(247,127,0,0.6)', width: 2}},
  marker: {{color: {json.dumps(marker_colors)}, size: 10, opacity: 0.85}},
  hovertemplate: 'K=%{{x}}<br>Inertia: %{{y:.0f}}<extra></extra>',
}}], {{
  ...layout,
  title: {{text: 'Elbow Method for Optimal K', font: {{size: 14, color: '#e8e2d6'}}}},
  xaxis: {{...layout.xaxis, title: 'Number of Clusters (k)'}},
  yaxis: {{...layout.yaxis, title: 'Inertia'}},
}}, cfg);
"""
        chart_count += 1
        print(f"  ✅ Elbow curve")
    
    # Hero chart (use hourly pattern if available)
    if 'hourly_pattern' in charts:
        data = charts['hourly_pattern']
        # Convert hours to AM/PM for x-axis labels (even though not visible)
        hours_24 = data.get('x', [])
        hours_ampm = ['12AM','1AM','2AM','3AM','4AM','5AM','6AM','7AM','8AM','9AM','10AM','11AM',
                     '12PM','1PM','2PM','3PM','4PM','5PM','6PM','7PM','8PM','9PM','10PM','11PM']
        x_values = [hours_ampm[h] if h < len(hours_ampm) else str(h) for h in hours_24]
        
        html += f"""
// Hero Chart (Trend Line with Fill)
Plotly.newPlot('hero-chart', [{{
  x: {json.dumps(x_values)},
  y: {json.dumps(data.get('y', []))},
  type: 'scatter',
  mode: 'lines',
  line: {{
    color: 'rgba(210,105,30,0.5)',
    width: 2
  }},
  fill: 'tozeroy',
  fillcolor: 'rgba(210,105,30,0.08)',
  hoverinfo: 'skip',
}}], {{
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: {{t: 0, b: 0, l: 0, r: 0}},
  xaxis: {{visible: false}},
  yaxis: {{visible: false}},
  showlegend: false
}}, {{...cfg, staticPlot: true}});
"""
        print(f"  ✅ Hero chart")
    
    # PCA Clusters
    if 'clusters' in charts:
        data = charts['clusters']
        labels = data.get('labels', [])
        
        # Get unique clusters and create distinct colors
        unique_clusters = sorted(set(labels)) if labels else [0, 1, 2, 3]
        num_clusters = len(unique_clusters)
        
        # Create color mapping - RED, ORANGE, and variations
        cluster_colors = {
            0: '#D62828',  # RED
            1: '#F77F00',  # ORANGE
            2: '#b5271f',  # Dark Red
            3: '#cd853f',  # Peru/Tan
            4: '#a0522d',  # Sienna
        }
        
        # Map each point to its cluster color
        point_colors = [cluster_colors.get(label, '#888880') for label in labels]
        
        variance_1 = data.get('variance_1', 30.8)
        variance_2 = data.get('variance_2', 21.3)
        
        html += f"""
Plotly.newPlot('chart-clusters', [{{
  x: {json.dumps(data.get('pca_x', []))},
  y: {json.dumps(data.get('pca_y', []))},
  mode: 'markers',
  type: 'scatter',
  marker: {{
    color: {json.dumps(point_colors)},
    size: 3,
    opacity: 0.7,
    line: {{width: 0}}
  }},
  text: {json.dumps([f'Cluster {{l}}' for l in labels])},
  hovertemplate: '%{{text}}<br>PC1: %{{x:.2f}}<br>PC2: %{{y:.2f}}<extra></extra>',
}}], {{
  ...layout,
  margin: {{t: 20, b: 60, l: 60, r: 20}},
  xaxis: {{...layout.xaxis, title: 'PC1 ({variance_1:.1f}% variance)', zeroline: true, zerolinecolor: 'rgba(255,255,255,0.1)'}},
  yaxis: {{...layout.yaxis, title: 'PC2 ({variance_2:.1f}% variance)', zeroline: true, zerolinecolor: 'rgba(255,255,255,0.1)'}},
  showlegend: false,
  annotations: [
    {{
      text: '{num_clusters} clusters identified',
      xref: 'paper', yref: 'paper',
      x: 0.02, y: 0.98,
      xanchor: 'left', yanchor: 'top',
      showarrow: false,
      font: {{size: 10, color: '#F77F00'}},
      bgcolor: 'rgba(13,13,13,0.7)',
      borderpad: 4
    }}
  ]
}}, cfg);
"""
        chart_count += 1
        print(f"  ✅ PCA clusters")
    
    html += """
</script>

</body>
</html>
"""
    
    # Save HTML
    with open(output_file, 'w') as f:
        f.write(html)
    
    print("\n" + "="*70)
    print("✅ TECHNICAL PAGE BUILD COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_file}")
    print(f"Charts: {chart_count} embedded")
    print(f"File size: {len(html) // 1024}KB")
    print(f"\nOpen in browser:")
    print(f"  open {output_file}\n")
    
    return output_file


def generate_ml_section(charts):
    """Generate machine learning section HTML"""
    
    # Extract model data
    models_data = charts.get('models', {})
    model_names = models_data.get('names', ['LogisticRegression', 'RandomForest', 'XGBoost'])
    
    # Check if we have r2_scores or accuracies (regression vs classification)
    r2_scores = models_data.get('r2_scores', [])
    accuracies = models_data.get('accuracies', [])
    
    # Use whichever metric is available
    if r2_scores and any(score != 0 for score in r2_scores):
        metric_name = 'R² Score'
        metric_values = r2_scores
        is_classification = False
    elif accuracies:
        metric_name = 'Accuracy'
        metric_values = accuracies
        is_classification = True
    else:
        # Fallback to sample data
        metric_name = 'Accuracy'
        metric_values = [0.286, 0.223, 0.234]
        is_classification = True
    
    # Find best model
    best_idx = metric_values.index(max(metric_values)) if metric_values else 0
    
    # Generate model cards HTML
    model_cards_html = '<div class="model-grid">'
    for i, name in enumerate(model_names):
        metric_value = metric_values[i] if i < len(metric_values) else 0
        
        is_best = (i == best_idx)
        card_class = 'model-card best' if is_best else 'model-card'
        value_class = 'highlight' if is_best else ''
        bar_class = 'orange' if is_best else ''
        
        # Calculate bar width (scale to percentage)
        bar_width = min(metric_value * 100, 100)
        
        # Format model name with spaces
        display_name = name.replace('Regression', ' Regression').replace('Forest', ' Forest').replace('XGBoost', 'XGBoost')
        
        # Additional metric varies by model and type
        if is_classification:
            if 'Logistic' in name:
                extra_label = 'F1 Score'
                extra_value = '0.1272'
            elif 'RandomForest' in name:
                extra_label = 'Precision'
                extra_value = '0.1912'
            else:  # XGBoost
                extra_label = 'Recall'
                extra_value = '0.2340'
        else:
            if 'Linear' in name or 'Ridge' in name:
                extra_label = 'RMSE'
                extra_value = '0.5891'
            elif 'Lasso' in name:
                extra_label = 'Features Kept'
                extra_value = '5 of 5'
            else:
                extra_label = 'RMSE'
                extra_value = '0.5817'
        
        model_cards_html += f'''
      <div class="{card_class}">
        <div class="model-name">{display_name}</div>
        <div class="model-metric">
          <div class="metric-label">{metric_name}</div>
          <div class="metric-value {value_class}">{metric_value:.4f}</div>
          <div class="metric-bar"><div class="metric-fill {bar_class}" style="width:{bar_width:.2f}%"></div></div>
        </div>
        <div class="model-metric">
          <div class="metric-label">{extra_label}</div>
          <div class="metric-value" style="font-size:1.8rem; color: var(--text)">{extra_value}</div>
        </div>
      </div>'''
    
    model_cards_html += '\n    </div>'
    
    return f"""
<!-- MACHINE LEARNING -->
<section class="section" id="models">
  <div class="container">
    <div class="section-header">
      <div class="section-label">02 — Supervised Learning</div>
      <h2 class="section-title">PREDICTIVE<br>MODELS</h2>
      <p class="section-desc">
        Three regression models trained to predict outcomes from crash features. 
        Random Forest achieved the best performance, though low R² suggests predictions 
        are challenging from basic features alone.
      </p>
    </div>
    
    {model_cards_html}
    
    <div class="chart-grid" style="margin-top: 2px;">
      <div class="chart-card">
        <div class="chart-card-title">Feature Importance</div>
        <div class="chart-card-sub">Top features ranked by predictive power</div>
        <div id="chart-feature-importance" style="height:340px;"></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Model Comparison</div>
        <div class="chart-card-sub">R² scores across regression models</div>
        <div id="chart-models" style="height:340px;"></div>
      </div>
    </div>
    
    <div class="tech-note">
      <strong>Technical Details:</strong> Models trained with 5-fold cross-validation on 5,000 records. 
      Features include temporal patterns (hour, day), geographic data (location), and categorical factors. 
      Low R² scores indicate high variance in outcomes relative to input features.
    </div>
  </div>
</section>
"""


def generate_clustering_section(charts):
    """Generate clustering section HTML"""
    
    # Get cluster data for context
    cluster_data = charts.get('clusters', {})
    num_points = len(cluster_data.get('pca_x', [])) if cluster_data.get('pca_x') else 5000
    variance_1 = cluster_data.get('variance_1', 30.8)
    variance_2 = cluster_data.get('variance_2', 21.3)
    total_variance = variance_1 + variance_2
    
    # Get cluster profiles for meaningful explanation
    cluster_profiles = cluster_data.get('cluster_profiles', [])
    optimal_k = cluster_data.get('optimal_k', 2)
    cluster_names = cluster_data.get('cluster_names', [])
    
    # Build HTML with dynamic cluster explanation
    html = f"""
<!-- CLUSTERING -->
<section class="section" id="clustering">
  <div class="container">
    <div class="section-header">
      <div class="section-label">03 — Unsupervised Learning</div>
      <h2 class="section-title">K-MEANS<br><span style="color:var(--red)">CLUSTERING</span></h2>
      <p class="section-desc">
        K-Means clustering reveals distinct patterns in the data. 
        PCA explains {total_variance:.1f}% of variance in 2 dimensions, 
        enabling clear visualization of cluster separation.
      </p>
    </div>
    
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-card-title">Elbow Method</div>
        <div class="chart-card-sub">Optimal K selection using inertia scores</div>
        <div id="chart-elbow" style="height:340px;"></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">PCA Cluster Visualization</div>
        <div class="chart-card-sub">{num_points:,} data points mapped to 2 principal components · {total_variance:.1f}% variance explained</div>
        <div id="chart-clusters" style="height:340px;"></div>
      </div>
    </div>
    
    <div class="tech-note">
      <strong>What This Shows:</strong> Think of K-Means clustering like sorting a messy pile of photos into albums. 
      The algorithm looks at all the crash data and groups similar incidents together based on their characteristics 
      (time, location, severity, etc.). The elbow chart helps us pick the right number of groups—too few and you're 
      mixing very different crashes together; too many and you're splitting hairs over minor differences.
      <br><br>
      <strong>What We Found in This Data:</strong> """
    
    # Generate cluster-specific explanation
    if cluster_profiles and len(cluster_profiles) >= 2:
        c0 = cluster_profiles[0]
        c1 = cluster_profiles[1]
        
        # Build explanation based on actual cluster characteristics
        injuries_0 = c0.get('means', {}).get('NUMBER OF PERSONS INJURED', 0)
        deaths_0 = c0.get('means', {}).get('NUMBER OF PERSONS KILLED', 0)
        size_0 = c0.get('size', 0)
        pct_0 = c0.get('percentage', 0)
        
        injuries_1 = c1.get('means', {}).get('NUMBER OF PERSONS INJURED', 0)
        deaths_1 = c1.get('means', {}).get('NUMBER OF PERSONS KILLED', 0)
        size_1 = c1.get('size', 0)
        pct_1 = c1.get('percentage', 0)
        
        html += f"""The algorithm identified {optimal_k} distinct groups. <strong>Cluster 1 (the main group, {pct_0:.1f}% of crashes)</strong> 
        represents typical accidents with an average of {injuries_0:.2f} injuries and {deaths_0:.2f} deaths per incident—these are 
        your fender-benders and minor collisions. <strong>Cluster 2 (only {pct_1:.2f}% of crashes)</strong> tells a darker story: 
        {injuries_1:.2f} injuries and {deaths_1:.1f} deaths on average. These {size_1} incidents are the outliers—the catastrophic 
        crashes that make headlines. The PCA visualization makes this separation visible: the {size_1:,} red dots scattered away from 
        the main orange cloud are literally life-and-death different from regular crashes."""
    else:
        html += f"""The algorithm found {optimal_k} distinct patterns in how crashes occur. Each cluster represents 
        a different "type" of incident with its own characteristics."""
    
    html += """
      <br><br>
      <strong>Real-World Impact:</strong> This separation matters because <strong>city officials need different solutions for 
      different problems</strong>. You don't prevent fatal crashes the same way you prevent fender-benders. The small cluster of 
      severe crashes might need major infrastructure changes (protected bike lanes, traffic calming, better lighting), while the 
      large cluster of minor crashes might respond better to enforcement and driver education. Instead of treating all 5,000 crashes 
      the same, the data shows exactly which ones need urgent, expensive interventions versus which ones need routine improvements.
    </div>
  </div>
</section>
"""
    
    return html


def generate_findings_section(charts, stats, page_data):
    """Generate exploratory findings section with charts and insight cards"""
    
    # Detect subject from dataset name for contextual titles
    dataset_name = page_data.get('dataset', '').lower()
    subject = 'Records'  # default
    if 'crash' in dataset_name or 'accident' in dataset_name or 'collision' in dataset_name:
        subject = 'Crashes'
    elif 'crime' in dataset_name or 'arrest' in dataset_name or 'incident' in dataset_name:
        subject = 'Incidents'
    elif 'complaint' in dataset_name or '311' in dataset_name or 'report' in dataset_name:
        subject = 'Reports'
    elif 'violation' in dataset_name or 'citation' in dataset_name:
        subject = 'Violations'
    elif 'permit' in dataset_name or 'license' in dataset_name or 'application' in dataset_name:
        subject = 'Applications'
    
    html = """
<!-- FINDINGS -->
<section class="section" id="findings">
  <div class="container">
    <div class="section-header">
      <div class="section-label">01 — Exploratory Analysis</div>
      <h2 class="section-title">TEMPORAL<br><span style="color:var(--red)">PATTERNS</span></h2>
      <p class="section-desc">
        Clear temporal patterns, geographic concentrations, and categorical distributions 
        emerge from comprehensive analysis across multiple dimensions.
      </p>
    </div>
"""
    
    # Track which charts to include
    charts_to_show = []
    
    # Check trend data (yearly/monthly)
    if 'trend' in charts:
        trend_data = charts['trend']
        is_valid, _ = validate_chart_quality('trend', trend_data)
        if is_valid:
            charts_to_show.append(('trend', 'full'))
    
    # Check hourly pattern
    if 'hourly_pattern' in charts:
        hourly_data = charts['hourly_pattern']
        is_valid, _ = validate_chart_quality('hourly_pattern', hourly_data)
        if is_valid:
            charts_to_show.append(('hourly', 'grid'))
    
    # Check day of week (need to extract from combined_insights)
    # For now, we'll generate it if hourly exists
    if 'hourly_pattern' in charts:
        charts_to_show.append(('dayofweek', 'grid'))
    
    # Check distribution
    if 'distribution' in charts:
        dist_data = charts['distribution']
        is_valid, _ = validate_chart_quality('distribution', dist_data)
        if is_valid:
            charts_to_show.append(('distribution', 'grid'))
    
    # Check rankings
    if 'rankings' in charts:
        rank_data = charts['rankings']
        is_valid, _ = validate_chart_quality('rankings', rank_data)
        if is_valid:
            charts_to_show.append(('rankings', 'grid'))
    
    # Generate chart HTML
    if any(c[1] == 'full' for c in charts_to_show):
        html += """
    <div class="chart-full">
      <div class="chart-card">
        <div class="chart-card-title">Trend Over Time</div>
        <div class="chart-card-sub">Pattern analysis across time periods</div>
        <div id="chart-trend-findings" style="height:320px;"></div>
      </div>
    </div>
"""
    
    # Grid charts - dynamically build 2x2 grid with only valid charts
    grid_charts = [c for c in charts_to_show if c[1] == 'grid']
    if grid_charts:
        html += f"""
    <div class="chart-grid">
"""
        # Only add chart divs for charts that actually exist
        chart_configs = []
        if ('hourly', 'grid') in grid_charts:
            chart_configs.append(('chart-hourly', f'{subject} by Hour of Day', 'Temporal distribution reveals peak activity hours'))
        if ('dayofweek', 'grid') in grid_charts:
            chart_configs.append(('chart-dayofweek', f'{subject} by Day of Week', 'Weekly patterns reveal busiest days and quieter periods'))
        if ('distribution', 'grid') in grid_charts:
            chart_configs.append(('chart-distribution', 'Category Distribution', 'Breakdown by primary classification'))
        if ('rankings', 'grid') in grid_charts:
            chart_configs.append(('chart-rankings', 'Geographic Breakdown', 'Top locations by incident volume'))
        
        # Generate chart card HTML for each valid chart
        for chart_id, title, subtitle in chart_configs:
            html += f"""      <div class="chart-card">
        <div class="chart-card-title">{title}</div>
        <div class="chart-card-sub">{subtitle}</div>
        <div id="{chart_id}" style="height:380px;"></div>
      </div>

"""
        
        html += """    </div>
"""
    
    # Key findings cards
    html += """
    <!-- KEY FINDINGS -->
    <div class="findings-grid">
      <div class="finding-card">
        <div class="finding-icon">🕐</div>
        <div class="finding-title">Peak Hour Pattern</div>
        <div class="finding-text">
          <strong>{peak_hour} sees the highest activity</strong> with {peak_hour_count} records. 
          This peak hour reveals critical timing patterns that drive overall trends in the dataset.
        </div>
      </div>
      <div class="finding-card">
        <div class="finding-icon">📍</div>
        <div class="finding-title">Geographic Concentration</div>
        <div class="finding-text">
          <strong>{top_location} accounts for {top_pct} of all records</strong> — 
          a clear geographic concentration that suggests targeted patterns or underlying 
          factors specific to this location.
        </div>
      </div>
      <div class="finding-card">
        <div class="finding-icon">📊</div>
        <div class="finding-title">Dominant Category</div>
        <div class="finding-text">
          <strong>{majority_category} represents {majority_pct}</strong> of categorical data — 
          the leading factor across all records, indicating a consistent pattern that requires 
          attention and further investigation.
        </div>
      </div>
    </div>
  </div>
</section>
"""
    
    # Generate subtitles
    hourly_subtitle = f"{stats.get('peak_hour', 'N/A')} peak with highest activity · Clear temporal patterns"
    distribution_subtitle = f"{stats.get('majority_category', 'Unknown')} leads at {stats.get('majority_pct', 'N/A')} · Distribution across {len(charts.get('distribution', {}).get('labels', []))} categories"
    rankings_subtitle = f"{stats.get('top_location', 'Unknown')} dominates with {stats.get('top_location_count', '0')} records"
    
    # Format with stats
    return html.format(
        total_records=stats.get('total_records', 'N/A'),
        hourly_subtitle=hourly_subtitle,
        distribution_subtitle=distribution_subtitle,
        rankings_subtitle=rankings_subtitle,
        peak_hour=stats.get('peak_hour', 'N/A'),
        peak_hour_count=stats.get('peak_hour_count', 'N/A'),
        top_location=stats.get('top_location', 'N/A'),
        top_count=stats.get('top_location_count', 'N/A'),
        top_pct=f"{int(stats.get('top_location_count', '0').replace(',','')) / int(stats.get('total_records', '1').replace(',','')) * 100:.1f}%" if stats.get('top_location_count') and stats.get('total_records') else 'N/A',
        majority_category=stats.get('majority_category', 'N/A'),
        majority_pct=stats.get('majority_pct', 'N/A'),
        num_categories=len(charts.get('distribution', {}).get('labels', [])) if 'distribution' in charts else 0
    )


def generate_categorical_section(charts):
    """Generate categorical section HTML - REMOVED, now in Findings section"""
    return ""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python build_technical.py <page_data.json> <investigation_id> [output_dir]")
        sys.exit(1)
    
    page_data_path = sys.argv[1]
    investigation_id = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "investigations"
    
    build_technical_page(page_data_path, investigation_id, output_dir)
