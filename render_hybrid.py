#!/usr/bin/env python3
"""
RecordsReveal Hybrid Renderer
Combines Claude's amazing visualizations with consistent site template
Best of both worlds: Creative freedom + Brand consistency
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Missing required packages. Install with:")
    print("   pip install anthropic python-dotenv")
    sys.exit(1)

# Load Claude API key
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print(f"❌ ANTHROPIC_API_KEY not found in {env_path}")
    sys.exit(1)

client = Anthropic(api_key=api_key)

def ask_claude(prompt, model="claude-sonnet-4-5-20250929"):
    """Send prompt to Claude API"""
    models_to_try = [
        "claude-sonnet-4-5-20250929",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620"
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            message = client.messages.create(
                model=model_name,
                max_tokens=12000,  # Enough for visualization section
                temperature=1,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            last_error = e
            if "not_found_error" in str(e):
                continue
            else:
                break
    
    print(f"❌ Claude API error: {last_error}")
    return None

def generate_visualization_content(investigation):
    """
    Ask Claude to generate JUST the visualization content
    (Hero, KPIs, Charts, Findings - but NOT header/footer)
    """
    
    headline = investigation.get('headline', 'Untitled Investigation')
    lede = investigation.get('lede', '')
    findings = investigation.get('findings', [])
    pull_quotes = investigation.get('pull_quotes', [])
    stat_boxes = investigation.get('stat_boxes', [])
    data_analysis = investigation.get('data_analysis', {})
    
    prompt = f"""You are a world-class data visualization designer.

Create STUNNING visualization content for this investigation:

**Headline:** {headline}

**Lede:** {lede}

**Statistics:**
{json.dumps(stat_boxes, indent=2)}

**Findings:**
{json.dumps(findings, indent=2)}

**Pull Quotes:**
{json.dumps(pull_quotes, indent=2)}

# WHAT TO CREATE

Generate beautiful HTML/CSS/JS for these sections ONLY:

1. **Hero Section** - Dramatic headline treatment with the investigation title
2. **KPI Dashboard** - Interactive cards showing the key stats (use the stat_boxes data)
3. **Charts** - 4 Chart.js visualizations with REAL DATA extracted from findings:
   - Attack vs Support (doughnut chart)
   - Party spending breakdown (bar chart)  
   - Top spenders or geographic (horizontal bars)
   - Trend or distribution (your choice based on data)
4. **Findings Cards** - Each of the {len(findings)} findings as beautiful cards with pull quotes

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

Make it AMAZING."""

    print("🎨 Asking Claude to design visualization content...")
    content = ask_claude(prompt)
    
    if not content:
        return None
    
    # Clean up markdown code blocks
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    # Validate
    if "<html" in content.lower() or "<!doctype" in content.lower():
        print("⚠️  WARNING: Claude included full HTML structure, extracting body content...")
        # Try to extract just the body content
        import re
        body_match = re.search(r'<body[^>]*>(.*)</body>', content, re.DOTALL)
        if body_match:
            content = body_match.group(1)
    
    chart_count = content.count("new Chart(") + content.count("new Chart ")
    print(f"✅ Generated visualization content")
    print(f"   - Chart initializations: {chart_count}")
    print(f"   - Size: {len(content)/1024:.1f}KB")
    
    return content

def create_site_template(investigation, viz_content, investigation_id):
    """
    Wrap Claude's amazing visualization in consistent RecordsReveal template
    """
    
    headline = investigation.get('headline', 'Untitled Investigation')
    dataset = investigation.get('dataset', 'Unknown')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline} | RecordsReveal</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="../assets/favicon.png">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@600;700&family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
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
        /* CONSISTENT SITE TEMPLATE STYLES */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --paper: #f8f6f1;
            --ink: #1a1a1a;
            --red: #b5271f;
            --border: #ddd9ce;
        }}
        
        .site-header {{
            background: white;
            border-bottom: 3px double var(--border);
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 40px;
            border-bottom: 1px solid var(--border);
            font-size: 11px;
            color: #888;
        }}
        
        .header-top a {{
            color: #888;
            margin-left: 16px;
            text-decoration: none;
        }}
        
        .header-top a:hover {{
            color: var(--red);
        }}
        
        .masthead {{
            text-align: center;
            padding: 20px 40px 16px;
        }}
        
        .site-name {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: clamp(2rem, 5vw, 3.8rem);
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        
        .site-name span {{
            color: var(--red);
        }}
        
        .site-tagline {{
            font-family: 'Libre Baskerville', serif;
            font-style: italic;
            font-size: 0.85rem;
            color: #888;
            margin-top: 8px;
        }}
        
        footer {{
            background: #1a1a1a;
            color: white;
            padding: 60px 40px 40px;
            margin-top: 80px;
        }}
        
        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 60px;
        }}
        
        .footer-logo {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 16px;
        }}
        
        .footer-logo span {{
            color: var(--red);
        }}
        
        .footer-about {{
            font-size: 0.9rem;
            line-height: 1.6;
            color: #999;
        }}
        
        .footer-section h4 {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }}
        
        .footer-links {{
            list-style: none;
        }}
        
        .footer-links li {{
            margin-bottom: 10px;
        }}
        
        .footer-links a {{
            color: #999;
            text-decoration: none;
            font-size: 0.9rem;
        }}
        
        .footer-links a:hover {{
            color: white;
        }}
        
        .footer-bottom {{
            text-align: center;
            padding-top: 40px;
            margin-top: 40px;
            border-top: 1px solid #333;
            color: #666;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

<!-- CONSISTENT SITE HEADER -->
<header class="site-header">
    <div class="header-top">
        <span>RecordsReveal · Independent Data Investigations</span>
        <div>
            <a href="../index.html">Home</a>
            <a href="../investigations.html">All Investigations</a>
            <a href="../about.html">About</a>
        </div>
    </div>
    <div class="masthead">
        <div class="site-name">RECORDS<span>REVEAL</span></div>
        <div class="site-tagline">Data-Driven Investigations Since 2025</div>
    </div>
</header>

<!-- CLAUDE'S AMAZING VISUALIZATION CONTENT -->
{viz_content}

<!-- CONSISTENT SITE FOOTER -->
<footer>
    <div class="footer-content">
        <div>
            <div class="footer-logo">RECORDS<span>REVEAL</span></div>
            <p class="footer-about">
                Independent investigative data journalism. We analyze public government records 
                and publish findings in plain English. Built on Python, machine learning, and a 
                commitment to transparency.
            </p>
        </div>
        
        <div class="footer-section">
            <h4>Investigations</h4>
            <ul class="footer-links">
                <li><a href="../index.html">Latest</a></li>
                <li><a href="../investigations.html">All Investigations</a></li>
                <li><a href="../methodology.html">Methodology</a></li>
            </ul>
        </div>
        
        <div class="footer-section">
            <h4>About</h4>
            <ul class="footer-links">
                <li><a href="../about.html">About Us</a></li>
                <li><a href="../contact.html">Contact</a></li>
                <li><a href="../privacy.html">Privacy Policy</a></li>
            </ul>
        </div>
    </div>
    
    <div class="footer-bottom">
        © 2026 RecordsReveal.com · All data sourced from public records · 
        Built with Python & Claude AI
    </div>
</footer>

</body>
</html>"""
    
    return html

def render_hybrid(investigation_json_path, output_dir="investigations"):
    """
    Hybrid approach: Claude's amazing visualizations + consistent template
    """
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*10 + "🎨 HYBRID RENDERER: Best of Both Worlds" + " "*14 + "║")
    print("╚"+"═"*68+"╝\n")
    
    print("="*70)
    print("Claude designs amazing visualizations")
    print("Template provides consistent branding")
    print("="*70 + "\n")
    
    # Load investigation
    print("📂 Loading investigation...")
    with open(investigation_json_path, 'r') as f:
        investigation = json.load(f)
    
    headline = investigation.get('headline', 'Untitled')
    findings = investigation.get('findings', [])
    stat_boxes = investigation.get('stat_boxes', [])
    
    print(f"✅ Loaded: {headline[:60]}...")
    print(f"   Findings: {len(findings)}")
    print(f"   Stats: {len(stat_boxes)}\n")
    
    # Step 1: Claude generates visualization content
    print("STEP 1: Claude designs visualization content...")
    viz_content = generate_visualization_content(investigation)
    
    if not viz_content:
        print("❌ Failed to generate visualization content")
        return None
    
    print("✅ Visualization content generated\n")
    
    # Step 2: Wrap in consistent template
    print("STEP 2: Wrapping in RecordsReveal template...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    investigation_id = f"investigation-{timestamp}"
    
    html = create_site_template(investigation, viz_content, investigation_id)
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{investigation_id}.html")
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    file_size_kb = len(html) / 1024
    
    print("✅ Template applied\n")
    print("╔"+"═"*68+"╗")
    print("║" + " "*20 + "✅ HYBRID RENDERING COMPLETE!" + " "*17 + "║")
    print("╚"+"═"*68+"╝\n")
    print(f"📁 Output: {output_file}")
    print(f"📏 Size: {file_size_kb:.1f}KB")
    print(f"💰 Cost: ~$0.02-0.04 (Claude visualization design)")
    
    print(f"\n✨ BEST OF BOTH WORLDS:")
    print(f"   ✅ Claude's amazing charts & KPIs")
    print(f"   ✅ Consistent RecordsReveal branding")
    print(f"   ✅ Repeatable across all investigations")
    print(f"   ✅ Professional header & footer")
    
    print(f"\n🚀 Open in browser:")
    print(f"   open {output_file}\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_hybrid.py <investigation_json>")
        print("\nExample:")
        print("  python render_hybrid.py investigation_output/investigation-*.json")
        print("\nThis creates:")
        print("  - Claude's amazing visualizations (KPIs, charts, findings)")
        print("  - Wrapped in consistent RecordsReveal template")
        print("  - Best of both worlds: Creativity + Consistency")
        sys.exit(1)
    
    investigation_json = sys.argv[1]
    
    if not os.path.exists(investigation_json):
        print(f"❌ Error: File not found: {investigation_json}")
        sys.exit(1)
    
    render_hybrid(investigation_json)

if __name__ == "__main__":
    main()
