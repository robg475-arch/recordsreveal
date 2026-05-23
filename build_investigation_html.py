#!/usr/bin/env python3
"""
RecordsReveal Investigation HTML Builder
=========================================

Generates complete investigation HTML from AI-generated article content.

Takes full_article.json and generates publication-ready HTML with:
- AI-written headlines, ledes, and findings
- Embedded Plotly visualizations
- RecordsReveal newspaper styling
- Social media meta tags
- AdSense placements

Usage:
    python3 build_investigation_html.py \\
        full_article.json \\
        visualizations/ \\
        --output investigation-004.html \\
        --investigation-number 004 \\
        --category "Crime" \\
        --theme-color "#8b4513"

Author: RecordsReveal Data Team
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_plotly_script(viz_file):
    """Extract Plotly.newPlot script from visualization HTML"""
    with open(viz_file, 'r') as f:
        content = f.read()
    
    # Extract the div id
    div_match = re.search(r'<div id="([^"]+)"', content)
    if not div_match:
        return None, None
    
    div_id = div_match.group(1)
    
    # Extract the Plotly.newPlot call
    script_match = re.search(r'Plotly\.newPlot\s*\(\s*"[^"]+",\s*(\[.*?\]),\s*(\{.*?\}),\s*(\{.*?\})\s*\)', content, re.DOTALL)
    if not script_match:
        return None, None
    
    data = script_match.group(1)
    layout = script_match.group(2)
    config = script_match.group(3)
    
    return div_id, (data, layout, config)


def format_number(num):
    """Format numbers for display (1000 -> 1.0K, 1000000 -> 1.0M)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))


def generate_html(article_data, viz_dir, inv_number, category, theme_color):
    """Generate complete investigation HTML"""
    
    ai = article_data.get('ai_content', {})
    hero = article_data.get('hero', {})
    methodology = article_data.get('methodology', {})
    findings = ai.get('findings', [])
    
    # Format numbers for hero banner
    total_records_formatted = format_number(hero.get('total_records', 0))
    model_accuracy = round(hero.get('model_r2', 0) * 100, 1)
    num_clusters = hero.get('num_clusters', 0)
    
    # Read visualization files
    charts = {}
    viz_path = Path(viz_dir)
    if viz_path.exists():
        for chart_file in viz_path.glob("*.html"):
            chart_name = chart_file.stem
            div_id, script_parts = extract_plotly_script(chart_file)
            if div_id and script_parts:
                charts[chart_name] = {
                    'div_id': div_id,
                    'data': script_parts[0],
                    'layout': script_parts[1],
                    'config': script_parts[2]
                }
    
    # Build HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ai.get('headline', 'Investigation')} — RecordsReveal</title>
<meta name="description" content="{ai.get('subhead', '')}">
<meta property="og:title" content="{ai.get('og_title', ai.get('headline', ''))}">
<meta property="og:description" content="{ai.get('og_description', ai.get('subhead', ''))}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9045696717764033" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --ink:#1c1c1c;--ink2:#4a4a4a;--ink3:#888;--paper:#f8f6f1;--white:#fff;
  --cream:#f0ece3;--red:#b5271f;--red2:#d4302a;--orange:{theme_color};--border:#ddd9ce;--border2:#c8c3b5;
}}
body{{background:var(--paper);color:var(--ink);font-family:'Barlow',sans-serif;line-height:1.6}}
a{{color:inherit;text-decoration:none}}
.site-header{{background:var(--white);border-bottom:3px double var(--border)}}
.header-top{{display:flex;justify-content:space-between;align-items:center;padding:10px 40px;border-bottom:1px solid var(--border);font-size:11px;color:var(--ink3)}}
.header-top a{{color:var(--ink3);margin-left:16px}}
.header-top a:hover{{color:var(--red)}}
.masthead{{text-align:center;padding:20px 40px 16px}}
.site-name{{font-family:'Barlow Condensed',sans-serif;font-size:clamp(2rem,5vw,3.8rem);font-weight:700;letter-spacing:.04em;text-transform:uppercase}}
.site-name span{{color:var(--red)}}
.site-rule{{width:100%;height:2px;background:var(--ink);margin:10px 0 8px;position:relative}}
.site-rule::after{{content:'';position:absolute;top:4px;left:0;right:0;height:1px;background:var(--ink)}}
.site-tagline{{font-family:'Libre Baskerville',serif;font-style:italic;font-size:.85rem;color:var(--ink3)}}
.header-nav{{display:flex;justify-content:center;border-top:1px solid var(--border);margin-top:14px}}
.header-nav a{{padding:7px 20px;font-size:10px;letter-spacing:.15em;text-transform:uppercase;font-weight:600;color:var(--ink2);border-right:1px solid var(--border);transition:all .15s}}
.header-nav a:last-child{{border-right:none}}
.header-nav a:hover,.header-nav a.active{{background:var(--ink);color:white}}
.ad-bar{{background:var(--cream);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:10px;text-align:center}}
.ad-label{{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink3);margin-bottom:4px}}
.container{{max-width:1160px;margin:0 auto;padding:0 40px}}
.layout{{display:grid;grid-template-columns:1fr 300px;gap:48px;padding:40px 0}}
.hero-banner{{background:var(--ink);padding:32px 40px;margin-bottom:20px;display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:linear-gradient(135deg,#1c1c1c,#2a1a0a)}}
.hero-stat{{background:rgba(255,255,255,.04);padding:20px 16px;text-align:center}}
.hero-stat-num{{font-family:'Barlow Condensed',sans-serif;font-size:2.2rem;font-weight:700;color:var(--orange);line-height:1;display:block}}
.hero-stat-label{{font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-top:4px}}
.story-hero{{border-bottom:2px solid var(--ink);padding-bottom:32px;margin-bottom:32px}}
.story-tag{{display:inline-block;background:var(--red);color:white;font-size:9px;letter-spacing:.15em;text-transform:uppercase;padding:3px 8px;margin-bottom:10px;font-weight:600}}
.story-kicker{{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--red);font-weight:600;margin-bottom:8px}}
.story-headline{{font-family:'Libre Baskerville',serif;font-size:clamp(1.7rem,3.5vw,2.5rem);font-weight:700;line-height:1.15;color:var(--ink);margin-bottom:12px}}
.story-dek{{font-family:'Libre Baskerville',serif;font-style:italic;font-size:.98rem;line-height:1.65;color:var(--ink2);margin-bottom:14px;max-width:640px}}
.story-meta{{font-size:10px;letter-spacing:.08em;color:var(--ink3);display:flex;align-items:center;gap:10px}}
.story-meta-dot{{width:3px;height:3px;border-radius:50%;background:var(--ink3)}}
.article-body{{font-family:'Libre Baskerville',serif;font-size:.98rem;line-height:1.85;color:var(--ink2)}}
.article-body p{{margin-bottom:1.2em}}
.article-body strong{{font-family:'Barlow',sans-serif;font-weight:600;color:var(--ink)}}
.lede{{font-size:1.1rem;line-height:1.75;color:var(--ink);margin-bottom:1.4em}}
.pull{{border-left:4px solid var(--red);padding:16px 20px;margin:24px 0;background:var(--cream);font-family:'Libre Baskerville',serif;font-style:italic;font-size:1.05rem;line-height:1.5;color:var(--ink)}}
.data-block{{background:var(--white);border:1px solid var(--border);padding:28px;margin:28px 0}}
.data-block-kicker{{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--red);font-weight:600;margin-bottom:4px}}
.data-block-title{{font-family:'Libre Baskerville',serif;font-size:1.3rem;font-weight:700;margin-bottom:4px}}
.data-block-sub{{font-size:.8rem;color:var(--ink3);font-style:italic;margin-bottom:20px;font-family:'Libre Baskerville',serif}}
.share-bar{{display:flex;gap:8px;align-items:center;margin:20px 0;padding:14px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}}
.share-label{{font-size:.72rem;letter-spacing:.15em;text-transform:uppercase;color:var(--ink3);margin-right:8px}}
.share-btn{{padding:6px 14px;border:1px solid var(--border);font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;background:white;color:var(--ink2);transition:all .15s;font-family:'Barlow',sans-serif}}
.share-btn:hover{{background:var(--ink);color:white;border-color:var(--ink)}}
.share-btn.x{{background:#000;color:white;border-color:#000}}
.share-btn.fb{{background:#1877f2;color:white;border-color:#1877f2}}
.sidebar-block{{margin-bottom:28px;border-top:2px solid var(--ink);padding-top:14px}}
.sidebar-title{{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:var(--ink);margin-bottom:14px}}
.sidebar-story{{padding:10px 0;border-bottom:1px solid var(--border);cursor:pointer}}
.sidebar-story:last-child{{border-bottom:none}}
.sidebar-story-kicker{{font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;color:var(--red);font-weight:600}}
.sidebar-story-hed{{font-size:.82rem;line-height:1.35;color:var(--ink2);margin-top:2px;transition:color .15s}}
.sidebar-story:hover .sidebar-story-hed{{color:var(--red)}}
.newsletter{{background:var(--ink);color:white;padding:20px;margin-bottom:24px}}
.newsletter h3{{font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}}
.newsletter p{{font-size:.78rem;color:rgba(255,255,255,.6);margin-bottom:14px;line-height:1.5}}
.newsletter input{{width:100%;padding:8px 10px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.08);color:white;font-size:.82rem;margin-bottom:8px;outline:none;font-family:'Barlow',sans-serif}}
.newsletter input::placeholder{{color:rgba(255,255,255,.35)}}
.newsletter button{{width:100%;padding:9px;background:var(--red);color:white;border:none;font-family:'Barlow Condensed',sans-serif;font-size:.82rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;cursor:pointer}}
.newsletter button:hover{{background:var(--red2)}}
.ad-sidebar{{background:var(--cream);border:1px dashed var(--border2);padding:10px;text-align:center;margin-bottom:20px}}
footer{{background:var(--ink);color:rgba(255,255,255,.4);text-align:center;padding:32px 40px;border-top:3px solid var(--red);font-size:.78rem;margin-top:60px}}
footer a{{color:rgba(255,255,255,.6)}}
footer a:hover{{color:var(--red)}}
@media(max-width:900px){{
  .layout{{grid-template-columns:1fr}}
  .sidebar{{display:none}}
  .hero-banner{{grid-template-columns:repeat(2,1fr)}}
  .container{{padding:0 20px}}
}}
</style>
</head>
<body>

<header class="site-header">
  <div class="header-top">
    <span>RecordsReveal · Independent Data Investigations</span>
    <div>
      <a href="../index.html">Home</a>
      <a href="../about/index.html">About</a>
      <a href="../privacy/index.html">Privacy</a>
    </div>
  </div>
  <div class="masthead">
    <a href="../index.html"><div class="site-name">Records<span>Reveal</span></div></a>
    <div class="site-rule"></div>
    <div class="site-tagline">What the public data actually shows — and what they'd rather you didn't know</div>
  </div>
  <nav class="header-nav">
    <a href="../index.html">Home</a>
    <a href="bird-strikes.html">Aviation</a>
    <a href="hollywood.html">Entertainment</a>
    <a href="car-crashes.html">Safety</a>
    <a href="#" class="active">{category}</a>
    <a href="../about/index.html">About</a>
  </nav>
</header>

<div class="ad-bar">
  <div class="ad-label">Advertisement</div>
  <ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px" data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>

<div class="hero-banner">
  <div class="hero-stat"><span class="hero-stat-num">{total_records_formatted}</span><div class="hero-stat-label">Records Analyzed</div></div>
  <div class="hero-stat"><span class="hero-stat-num">{model_accuracy}%</span><div class="hero-stat-label">Model Accuracy</div></div>
  <div class="hero-stat"><span class="hero-stat-num">{num_clusters}</span><div class="hero-stat-label">Clusters Found</div></div>
  <div class="hero-stat"><span class="hero-stat-num">{methodology.get('best_model', 'ML').split()[0]}</span><div class="hero-stat-label">Best Model</div></div>
</div>

<div class="container">
  <div class="layout">
    <main>

      <!-- HERO STORY -->
      <div class="story-hero">
        <div class="story-tag">Investigation #{inv_number} · Live Now</div>
        <div class="story-kicker">{category} Data Analysis</div>
        <h1 class="story-headline">{ai.get('headline', 'Investigation Results')}</h1>
        <p class="story-dek">{ai.get('subhead', '')}</p>
        <div class="story-meta">
          <span>RecordsReveal Data Team</span>
          <span class="story-meta-dot"></span>
          <span id="pub-date">{datetime.now().strftime('%B %Y')}</span>
          <span class="story-meta-dot"></span>
          <span>12 min read</span>
          <span class="story-meta-dot"></span>
          <span style="color:var(--red);font-weight:600">{total_records_formatted} records analyzed</span>
        </div>
      </div>

      <!-- ARTICLE INTRO -->
      <div class="article-body">
        <p class="lede">{ai.get('lede', '')}</p>
        <p>{ai.get('intro_paragraph_2', '')}</p>
        <p>{ai.get('intro_paragraph_3', '')}</p>
      </div>

'''

    # Add findings
    for i, finding in enumerate(findings[:3], 1):
        # Add share bar after first finding
        if i == 2:
            html += '''
      <!-- SHARE BAR -->
      <div class="share-bar">
        <span class="share-label">Share this story</span>
        <button class="share-btn x" onclick="shareX()">Post on X</button>
        <button class="share-btn fb" onclick="shareFB()">Share on Facebook</button>
        <button class="share-btn" onclick="copyLink()">Copy Link</button>
      </div>

'''
        
        html += f'''      <!-- FINDING #{i} -->
      <div class="data-block">
        <div class="data-block-kicker">Finding #{i}</div>
        <h2 class="data-block-title">{finding.get('title', '')}</h2>
        <p class="data-block-sub">Machine learning analysis · {total_records_formatted} records</p>
        <div class="article-body" style="margin-bottom:20px">
'''
        
        # Split description into paragraphs
        description = finding.get('description', '')
        paragraphs = description.split('\n\n')
        for para in paragraphs:
            if para.strip():
                html += f'          <p>{para.strip()}</p>\n'
        
        html += f'''        </div>
'''
        
        # Add chart if available (prioritize domain-specific charts)
        # Try domain charts first, fall back to ML charts
        chart_priority = {
            1: ['hourly_pattern', 'day_of_week', 'model_comparison'],
            2: ['geographic_breakdown', 'category_breakdown_1', 'correlation_heatmap'],
            3: ['category_breakdown_2', 'metric_comparison', 'cluster_plot']
        }
        
        chart_name = None
        if i in chart_priority:
            for candidate in chart_priority[i]:
                if candidate in charts:
                    chart_name = candidate
                    break
        
        if chart_name:
            chart = charts[chart_name]
            html += f'''        <div id="chart-finding-{i}" style="height:400px;margin:20px 0"></div>
'''
        
        # Add pull quote
        if finding.get('pull_quote'):
            html += f'''        <div class="pull">
          <p>{finding.get('pull_quote')}</p>
        </div>
'''
        
        html += '      </div>\n\n'
        
        # Add ad after second finding
        if i == 2:
            html += '''      <!-- AD RECTANGLE -->
      <div class="ad-bar" style="margin:8px 0 24px">
        <div class="ad-label">Advertisement</div>
        <ins class="adsbygoogle" style="display:inline-block;width:336px;height:280px" data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
      </div>

'''

    # Add final share bar and methodology
    html += f'''      <!-- FINAL SHARE -->
      <div class="share-bar">
        <span class="share-label">Found this useful? Share it</span>
        <button class="share-btn x" onclick="shareX()">Post on X</button>
        <button class="share-btn fb" onclick="shareFB()">Share on Facebook</button>
        <button class="share-btn" onclick="copyLink()">Copy Link</button>
      </div>

      <!-- CONCLUSION -->
      <div class="article-body">
        <p>{ai.get('conclusion', '')}</p>
      </div>

      <!-- METHODOLOGY NOTE -->
      <div class="data-block" style="background:var(--cream)">
        <div class="data-block-kicker">Methodology</div>
        <h3 style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px">How We Did This</h3>
        <div class="article-body" style="font-size:.85rem">
          <p><strong>Dataset:</strong> {hero.get('total_records', 0):,} records analyzed using machine learning.</p>
          <p><strong>Model:</strong> {methodology.get('best_model', 'Multiple models')} achieved R²={methodology.get('r2_score', 0):.4f} on {methodology.get('task_type', 'prediction')} task.</p>
          <p><strong>Features:</strong> {hero.get('total_features', 0)} variables analyzed. K-Means clustering identified {hero.get('num_clusters', 0)} distinct patterns.</p>
          <p><strong>Tools:</strong> Python · pandas · scikit-learn · Plotly · Claude AI.</p>
        </div>
      </div>

    </main>

    <!-- SIDEBAR -->
    <aside class="sidebar">

      <div class="ad-sidebar">
        <div class="ad-label">Advertisement</div>
        <ins class="adsbygoogle" style="display:inline-block;width:300px;height:250px" data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
      </div>

      <div class="newsletter">
        <h3>Get the next investigation</h3>
        <p>New data stories monthly. No spam.</p>
        <input type="email" placeholder="your@email.com">
        <button>Subscribe Free →</button>
      </div>

      <div class="sidebar-block">
        <div class="sidebar-title">All Investigations</div>
        <div class="sidebar-story" onclick="location.href='bird-strikes.html'">
          <div class="sidebar-story-kicker">Live Now · Aviation</div>
          <div class="sidebar-story-hed">35 years of FAA data reveals who's responsible for bird strikes</div>
        </div>
        <div class="sidebar-story" onclick="location.href='hollywood.html'">
          <div class="sidebar-story-kicker">Live Now · Entertainment</div>
          <div class="sidebar-story-hed">Hollywood has a formula. We reverse-engineered it.</div>
        </div>
        <div class="sidebar-story" onclick="location.href='car-crashes.html'">
          <div class="sidebar-story-kicker">Live Now · Safety</div>
          <div class="sidebar-story-hed">2M NYC crashes reveal the deadliest hour of your day</div>
        </div>
      </div>

      <div class="ad-sidebar">
        <div class="ad-label">Advertisement</div>
        <ins class="adsbygoogle" style="display:inline-block;width:300px;height:250px" data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
      </div>

    </aside>
  </div>
</div>

<footer>
  <p>© 2026 RecordsReveal.com · <a href="../index.html">Home</a> · <a href="../about/index.html">About</a> · <a href="../privacy/index.html">Privacy</a> · For informational purposes</p>
</footer>

<script>
// SHARE FUNCTIONS
const URL = encodeURIComponent(window.location.href);
const TEXT = encodeURIComponent('{ai.get("og_title", ai.get("headline", ""))[:100]}');
function shareX(){{ window.open(`https://twitter.com/intent/tweet?text=${{TEXT}}&url=${{URL}}`,'_blank'); }}
function shareFB(){{ window.open(`https://www.facebook.com/sharer/sharer.php?u=${{URL}}`,'_blank'); }}
function copyLink(){{ navigator.clipboard.writeText(window.location.href).then(()=>{{ document.querySelectorAll('.share-btn').forEach(b=>{{if(b.textContent.includes('Copy')){{b.textContent='Copied!';setTimeout(()=>b.textContent='Copy Link',2000);}}}}); }}); }}

// RENDER CHARTS
'''
    
    # Add chart rendering code for embedded charts
    chart_priority = {
        1: ['hourly_pattern', 'day_of_week', 'model_comparison'],
        2: ['geographic_breakdown', 'category_breakdown_1', 'correlation_heatmap'],
        3: ['category_breakdown_2', 'metric_comparison', 'cluster_plot']
    }
    
    for i, candidates in chart_priority.items():
        chart_name = None
        for candidate in candidates:
            if candidate in charts:
                chart_name = candidate
                break
        
        if chart_name:
            chart = charts[chart_name]
            html += f'''
if(document.getElementById('chart-finding-{i}')){{
  Plotly.newPlot('chart-finding-{i}', 
    {chart['data']}, 
    {chart['layout']}, 
    {chart['config']}
  );
}}
'''
    
    html += '''</script>
</body>
</html>
'''
    
    return html


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 build_investigation_html.py <full_article.json> <visualizations_dir> [options]")
        print("\nOptions:")
        print("  --output <filename>            Output HTML filename (default: investigation.html)")
        print("  --investigation-number <num>   Investigation number (default: 004)")
        print("  --category <name>              Category name (default: Data)")
        print("  --theme-color <hex>            Theme color hex code (default: #d2691e)")
        print("\nExample:")
        print("  python3 build_investigation_html.py \\")
        print("    analysis_results/full_article.json \\")
        print("    analysis_results/visualizations/ \\")
        print("    --output investigation-004.html \\")
        print("    --investigation-number 004 \\")
        print("    --category 'Crime' \\")
        print("    --theme-color '#8b4513'")
        sys.exit(1)
    
    article_path = Path(sys.argv[1])
    viz_dir = Path(sys.argv[2])
    
    # Parse options
    output_file = "investigation.html"
    inv_number = "004"
    category = "Data"
    theme_color = "#d2691e"
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--investigation-number' and i + 1 < len(sys.argv):
            inv_number = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--theme-color' and i + 1 < len(sys.argv):
            theme_color = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Validate files
    if not article_path.exists():
        print(f"❌ Article file not found: {article_path}")
        sys.exit(1)
    
    if not viz_dir.exists():
        print(f"⚠️  Visualizations directory not found: {viz_dir}")
        print("   Continuing without charts...")
    
    print("=" * 60)
    print("RecordsReveal HTML Builder")
    print("=" * 60)
    
    # Load article data
    print(f"\n📂 Loading article data...")
    article_data = load_json(article_path)
    print(f"   ✅ {article_path}")
    
    # Generate HTML
    print(f"\n🔨 Building HTML...")
    html = generate_html(article_data, viz_dir, inv_number, category, theme_color)
    
    # Save output
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"\n✅ Investigation HTML created:")
    print(f"   {output_path.absolute()}")
    
    # Show stats
    ai_content = article_data.get('ai_content', {})
    findings_count = len(ai_content.get('findings', []))
    word_count = sum(len(f.get('description', '').split()) for f in ai_content.get('findings', []))
    
    print(f"\n📊 Content stats:")
    print(f"   Headline: {len(ai_content.get('headline', ''))} chars")
    print(f"   Findings: {findings_count} sections")
    print(f"   Total words: {word_count + len(ai_content.get('lede', '').split()) + len(ai_content.get('intro_paragraph_2', '').split())}")
    print(f"   Investigation #: {inv_number}")
    print(f"   Category: {category}")
    print(f"   Theme color: {theme_color}")
    
    print("\n" + "=" * 60)
    print("✅ HTML GENERATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open the HTML file in your browser to review")
    print("2. Make any manual edits to headlines/prose")
    print("3. Move to investigations/ directory when ready")
    print("4. Run update_homepage.py to add to index.html")


if __name__ == "__main__":
    main()
