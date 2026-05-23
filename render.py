#!/usr/bin/env python3
"""
RecordsReveal HTML Renderer
Converts investigation JSON to beautiful HTML using RecordsReveal design system
Flexible: Works with any number of findings, stat boxes, etc.
"""

import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path

def markdown_to_html(text):
    """Convert simple markdown to HTML (bold, paragraphs)"""
    # Convert **text** to <strong>text</strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # Split into paragraphs and wrap in <p> tags
    paragraphs = text.split('\n\n')
    html_paragraphs = [f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()]
    
    return '\n'.join(html_paragraphs)

def render_html(investigation_json_path, output_dir="investigations"):
    """
    Render investigation JSON to HTML
    """
    print("\n" + "="*70)
    print("🎨 RECORDSREVEAL HTML RENDERER")
    print("="*70)
    print(f"Input: {investigation_json_path}")
    print(f"Output directory: {output_dir}")
    print("="*70 + "\n")
    
    # Load investigation
    print("📂 Loading investigation...")
    with open(investigation_json_path, 'r') as f:
        investigation = json.load(f)
    
    headline = investigation.get('headline', 'Untitled Investigation')
    lede = investigation.get('lede', '')
    findings = investigation.get('findings', [])
    pull_quotes = investigation.get('pull_quotes', [])
    methodology = investigation.get('methodology', '')
    stat_boxes = investigation.get('stat_boxes', [])
    dataset = investigation.get('dataset', 'Unknown')
    
    print(f"✅ Loaded investigation")
    print(f"   Headline: {headline[:60]}...")
    print(f"   Findings: {len(findings)}")
    print(f"   Pull quotes: {len(pull_quotes)}")
    print(f"   Stat boxes: {len(stat_boxes)}\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate investigation ID
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    investigation_id = f"investigation-{timestamp}"
    
    # Build HTML
    print("🎨 Building HTML structure...")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline} | RecordsReveal</title>
  <meta name="description" content="{lede[:150]}...">
  <meta property="og:title" content="{headline}">
  <meta property="og:description" content="{lede[:150]}...">
  <!-- Favicon -->
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-7B3KBBGVWE"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-7B3KBBGVWE');
  </script>
  
  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9045696717764033" crossorigin="anonymous"></script>
  
  <style>
    :root{{
      --paper:#f8f6f1;
      --white:#fff;
      --cream:#f8f6f1;
      --ink:#1a1a1a;
      --ink2:#2a2a2a;
      --ink3:#4a4a4a;
      --red:#b5271f;
      --orange:#d2691e;
      --border:#d4d1c6;
    }}
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:var(--paper);color:var(--ink);font-family:'Barlow',sans-serif;line-height:1.6}}
    a{{color:inherit;text-decoration:none}}
    .site-header{{background:var(--white);border-bottom:3px double var(--border)}}
    .header-top{{display:flex;justify-content:space-between;align-items:center;padding:10px 40px;border-bottom:1px solid var(--border);font-size:11px;color:var(--ink3)}}
    .header-top a{{color:var(--ink3);margin-left:16px}}
    .header-top a:hover{{color:var(--red)}}
    .masthead{{text-align:center;padding:18px 0}}
    .masthead-title{{font-family:'Libre Baskerville',serif;font-size:3rem;font-weight:700;color:var(--ink);letter-spacing:-0.02em}}
    .masthead-tagline{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink3);margin-top:6px}}
    .nav{{background:var(--ink);padding:0 40px}}
    .nav-links{{display:flex;gap:32px;list-style:none}}
    .nav-links a{{display:block;padding:12px 0;font-size:.88rem;font-weight:600;color:var(--white);text-transform:uppercase;letter-spacing:.08em;border-bottom:3px solid transparent}}
    .nav-links a:hover{{border-bottom-color:var(--red)}}
    .container{{max-width:1400px;margin:0 auto;padding:0 40px}}
    .grid{{display:grid;grid-template-columns:1fr 340px;gap:40px;margin:40px 0}}
    .main-content{{background:var(--white);padding:40px;border:1px solid var(--border)}}
    .story-meta{{display:flex;gap:8px;align-items:center;font-size:.8rem;color:var(--ink3);margin-bottom:24px}}
    .story-meta-dot{{width:3px;height:3px;background:var(--ink3);border-radius:50%}}
    .story-headline{{font-family:'Libre Baskerville',serif;font-size:2.2rem;line-height:1.2;font-weight:700;margin-bottom:20px}}
    .article-body{{font-family:'Libre Baskerville',serif;font-size:.98rem;line-height:1.85;color:var(--ink2)}}
    .article-body p{{margin-bottom:1.2em}}
    .article-body strong{{font-family:'Barlow',sans-serif;font-weight:600;color:var(--ink)}}
    .lede{{font-size:1.1rem;line-height:1.75;color:var(--ink);margin-bottom:1.4em}}
    .pull{{border-left:4px solid var(--red);padding:16px 20px;margin:24px 0;background:var(--cream);font-family:'Libre Baskerville',serif;font-style:italic;font-size:1.05rem;line-height:1.5;color:var(--ink)}}
    .stat-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:28px 0;padding:28px;background:var(--cream);border:1px solid var(--border)}}
    .stat-cell{{text-align:center}}
    .stat-big{{font-family:'Barlow Condensed',sans-serif;font-size:2.4rem;font-weight:700;color:var(--red);line-height:1}}
    .stat-label{{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);margin-top:4px;line-height:1.4}}
    .stat-context{{font-size:.75rem;color:var(--ink2);margin-top:4px;font-style:italic;font-family:'Libre Baskerville',serif}}
    .data-block{{background:var(--white);border:1px solid var(--border);padding:28px;margin:28px 0}}
    .data-block-kicker{{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--red);font-weight:600;margin-bottom:4px}}
    .data-block-title{{font-family:'Libre Baskerville',serif;font-size:1.3rem;font-weight:700;margin-bottom:4px}}
    .data-block-sub{{font-size:.8rem;color:var(--ink3);margin-bottom:16px}}
    .methodology{{background:var(--cream);padding:28px;border:1px solid var(--border);margin:28px 0;font-size:.9rem;line-height:1.7}}
    .methodology h3{{font-family:'Barlow',sans-serif;font-size:1rem;font-weight:700;margin-bottom:12px;text-transform:uppercase;letter-spacing:.08em}}
    .ad-placeholder{{background:var(--cream);border:1px solid var(--border);padding:40px 20px;text-align:center;margin:28px 0;color:var(--ink3);font-size:.9rem}}
  </style>
</head>
<body>

<header class="site-header">
  <div class="header-top">
    <span>RecordsReveal · Independent Data Investigations</span>
    <div>
      <a href="../index.html">Home</a>
      <a href="../about.html">About</a>
      <a href="../investigations.html">All Investigations</a>
    </div>
  </div>
  <div class="masthead">
    <div class="masthead-title">RecordsReveal</div>
    <div class="masthead-tagline">Data-Driven Investigations · Since 2025</div>
  </div>
  <nav class="nav">
    <ul class="nav-links">
      <li><a href="../index.html">Latest</a></li>
      <li><a href="../investigations.html">All Investigations</a></li>
      <li><a href="../methodology.html">Methodology</a></li>
    </ul>
  </nav>
</header>

<div class="container">
  <div class="grid">
    <main class="main-content">
      
      <div class="story-meta">
        <span>Investigation</span>
        <span class="story-meta-dot"></span>
        <span>Published {datetime.now().strftime("%B %d, %Y")}</span>
        <span class="story-meta-dot"></span>
        <span>Data Analysis</span>
      </div>

      <h1 class="story-headline">{headline}</h1>

      <div class="article-body">
        <p class="lede">{lede}</p>
      </div>
"""
    
    # Add stat boxes if available
    if stat_boxes:
        html += """
      <!-- STAT ROW -->
      <div class="stat-row">
"""
        for stat_box in stat_boxes[:6]:  # Max 6 stat boxes
            html += f"""        <div class="stat-cell">
          <div class="stat-big">{stat_box.get('value', 'N/A')}</div>
          <div class="stat-label">{stat_box.get('label', '')}</div>
          <div class="stat-context">{stat_box.get('context', '')}</div>
        </div>
"""
        html += """      </div>
"""
    
    # Add findings
    for i, finding in enumerate(findings):
        html += f"""
      <!-- FINDING #{i+1} -->
      <div class="data-block">
        <div class="data-block-kicker">Finding #{i+1}</div>
        <h2 class="data-block-title">{finding.get('title', f'Finding {i+1}')}</h2>
        <div class="data-block-sub">Key Stat: {finding.get('key_stat', 'N/A')}</div>
        <div class="article-body" style="margin-bottom:20px">
          {markdown_to_html(finding.get('body', ''))}
        </div>
      </div>
"""
        
        # Add pull quote after some findings
        if i < len(pull_quotes):
            html += f"""
      <div class="pull">
        "{pull_quotes[i]}"
      </div>
"""
        
        # Add ad after 2nd finding
        if i == 1:
            html += """
      <!-- Ad Placement -->
      <div class="ad-placeholder">
        [Advertisement]
      </div>
"""
    
    # Add methodology
    if methodology:
        html += f"""
      <!-- METHODOLOGY -->
      <div class="methodology">
        <h3>Methodology</h3>
        {markdown_to_html(methodology)}
        <p style="margin-top:12px;font-size:.85rem;color:var(--ink3)">
          Dataset: <code>{dataset}</code>
        </p>
      </div>
"""
    
    # Close main content and add sidebar placeholder
    html += """
    </main>

    <aside class="sidebar">
      <div class="data-block">
        <div class="data-block-kicker">About This Investigation</div>
        <h3 class="data-block-title">Data-Driven Journalism</h3>
        <div class="data-block-sub">Independent Analysis</div>
        <p style="font-size:.9rem;line-height:1.6;margin-top:12px">
          RecordsReveal uses open data and AI-assisted analysis to investigate 
          stories hidden in public records. All findings are based on verifiable data sources.
        </p>
      </div>

      <!-- Ad Sidebar -->
      <div class="ad-placeholder" style="margin-top:20px">
        [Advertisement]
      </div>
    </aside>
  </div>
</div>

</body>
</html>
"""
    
    # Save HTML
    output_file = os.path.join(output_dir, f"{investigation_id}.html")
    with open(output_file, 'w') as f:
        f.write(html)
    
    file_size_kb = len(html) / 1024
    
    print("="*70)
    print("✅ HTML RENDERING COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_file}")
    print(f"File size: {file_size_kb:.1f}KB")
    print(f"Findings rendered: {len(findings)}")
    print(f"Stat boxes: {len(stat_boxes)}")
    print(f"Pull quotes: {len(pull_quotes)}")
    
    print(f"\n📖 Open in browser:")
    print(f"  open {output_file}\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python render.py <investigation_json> [output_dir]")
        print("\nExample:")
        print("  python render.py investigation_output/investigation-20260523-090450.json")
        print("\nThis will:")
        print("  1. Load investigation JSON")
        print("  2. Apply RecordsReveal HTML template")
        print("  3. Output ready-to-publish HTML")
        sys.exit(1)
    
    investigation_json = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "investigations"
    
    if not os.path.exists(investigation_json):
        print(f"❌ Error: File not found: {investigation_json}")
        sys.exit(1)
    
    render_html(investigation_json, output_dir)

if __name__ == "__main__":
    main()
