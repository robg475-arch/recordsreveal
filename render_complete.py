#!/usr/bin/env python3
"""
RecordsReveal Complete Renderer
- Google AdSense placements
- Sidebar (ads, investigation links, data downloads)
- Leonardo.ai hero images
- Professional layout
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Missing packages: pip install anthropic python-dotenv requests")
    sys.exit(1)

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
LEONARDO_API_KEY = os.getenv('LEONARDO_API_KEY')

if not ANTHROPIC_API_KEY:
    print("❌ ANTHROPIC_API_KEY not found in .env")
    sys.exit(1)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def ask_claude(prompt, model="claude-sonnet-4-5-20250929"):
    """Send prompt to Claude"""
    models = [
        "claude-sonnet-4-5-20250929",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620"
    ]
    
    for model_name in models:
        try:
            message = client.messages.create(
                model=model_name,
                max_tokens=12000,
                temperature=1,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text.strip()
        except Exception as e:
            if "not_found_error" not in str(e):
                print(f"❌ Claude error: {e}")
                return None
    return None

def generate_hero_image(investigation, investigation_id):
    """Generate hero image with Leonardo.ai"""
    
    if not LEONARDO_API_KEY:
        print("⚠️  Skipping hero image (no LEONARDO_API_KEY)")
        return None
    
    headline = investigation.get('headline', '')
    
    # Create prompt based on investigation content
    prompt = f"""Sophisticated editorial illustration for data journalism investigation. 
Modern minimalist style. Abstract geometric data visualization elements. 
Dark professional background with cream, red, and orange accent colors. 
Clean, professional, suitable for serious investigative journalism.
Topic: {headline[:100]}
Style: NYT graphics, The Pudding, FiveThirtyEight aesthetic."""
    
    print(f"\n🎨 Generating hero image with Leonardo.ai...")
    
    headers = {
        "authorization": f"Bearer {LEONARDO_API_KEY}",
        "content-type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "num_images": 1,
        "width": 1024,
        "height": 768,
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3"
    }
    
    try:
        # Generate
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        generation_id = response.json()["sdGenerationJob"]["generationId"]
        
        print(f"   Generation started: {generation_id}")
        print("   Waiting for image...")
        
        # Poll for completion
        for attempt in range(30):  # 30 attempts = ~2.5 minutes
            time.sleep(5)
            status_response = requests.get(
                f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                headers=headers,
                timeout=10
            )
            
            if status_response.ok:
                data = status_response.json()
                images = data.get("generations_by_pk", {}).get("generated_images", [])
                if images:
                    image_url = images[0]["url"]
                    
                    # Download
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # Save
                    os.makedirs("images/heroes", exist_ok=True)
                    img_path = f"images/heroes/{investigation_id}.jpg"
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(f"   ✅ Hero image saved: {img_path}")
                    return img_path
        
        print("   ⚠️  Timeout waiting for image")
        return None
        
    except Exception as e:
        print(f"   ⚠️  Image generation failed: {e}")
        return None

def generate_visualization(investigation):
    """Ask Claude to generate visualization content with sidebar-aware layout"""
    
    headline = investigation.get('headline', '')
    lede = investigation.get('lede', '')
    findings = investigation.get('findings', [])
    stat_boxes = investigation.get('stat_boxes', [])
    
    prompt = f"""You are a world-class data visualization designer.

Create STUNNING visualization content for this investigation:

**Headline:** {headline}
**Lede:** {lede}
**Statistics:** {json.dumps(stat_boxes, indent=2)}
**Findings:** {json.dumps(findings, indent=2)}

# LAYOUT REQUIREMENTS

The page has a SIDEBAR on the right (300px wide). Your content goes in the MAIN column (left side).

Generate HTML/CSS/JS for these sections:

1. **Hero Section** - Dramatic headline, lede, and hero image placeholder
   - Include: <img id="hero-image" src="" alt="Investigation Hero" />
   - We'll inject the actual image path later

2. **KPI Dashboard** - Interactive stat cards (use stat_boxes data)
   - Grid layout that works with sidebar
   - Hover effects
   
3. **AdSense Placement #1** - After KPIs, before charts
   - Add: <div class="ad-placement" id="ad-top"></div>

4. **INTERLEAVED Findings + Charts** - Mix findings and visualizations
   - Finding 1 → Chart 1
   - AdSense Placement #2: <div class="ad-placement" id="ad-middle"></div>
   - Finding 2 → Chart 2
   - Finding 3 → Chart 3
   - Finding 4 → Chart 4
   - This breaks up the page and keeps readers engaged
   - Charts should directly support the finding above them
   
5. **AdSense Placement #3** - After all findings/charts
   - Add: <div class="ad-placement" id="ad-bottom"></div>

# DESIGN REQUIREMENTS

- Width: Assume main content is ~800px (sidebar takes 300px + gap)
- Modern, professional design
- Chart.js 4.x via CDN
- All CSS inline in <style> tags
- All JS inline in <script> tags
- Mobile responsive (sidebar stacks below on mobile)
- Smooth animations

# CRITICAL

Return ONLY HTML content sections.
Do NOT include <!DOCTYPE>, <html>, <head>, <body>, header, footer.
Start with <style> for your sections, then content, then <script> for charts.

Include the 3 AdSense placements and hero image placeholder exactly as specified.

Make it AMAZING."""

    print("🎨 Asking Claude to design visualization...")
    content = ask_claude(prompt)
    
    if not content:
        return None
    
    # Clean markdown
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    chart_count = content.count("new Chart(") + content.count("new Chart ")
    ad_count = content.count('class="ad-placement"')
    
    print(f"✅ Visualization generated")
    print(f"   - Charts: {chart_count}")
    print(f"   - Ad placements: {ad_count}")
    
    return content

def create_complete_page(investigation, viz_content, investigation_id, hero_image_path):
    """Create complete page with template, sidebar, ads"""
    
    headline = investigation.get('headline', '')
    dataset = investigation.get('dataset', '')
    
    # Inject hero image into viz content if we have one
    if hero_image_path and 'id="hero-image"' in viz_content:
        viz_content = viz_content.replace(
            'src=""',
            f'src="../{hero_image_path}"'
        )
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{headline} | RecordsReveal</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="../assets/favicon.png">
    
    <!-- Fonts -->
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
        
        /* Site Header */
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
            font-size: 11px;
            color: #888;
            border-bottom: 1px solid var(--border);
        }}
        
        .header-top a {{
            color: #888;
            text-decoration: none;
            margin-left: 16px;
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
        
        /* Main Layout */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .page-layout {{
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 40px;
            margin: 40px 0;
        }}
        
        @media (max-width: 1024px) {{
            .page-layout {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Sidebar - scrolls with main content, no sticky */
        .sidebar {{
            /* Removed sticky positioning for synchronized scrolling */
        }}
        
        .sidebar-section {{
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        
        .sidebar-title {{
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 16px;
            color: var(--red);
        }}
        
        .sidebar-ad {{
            background: var(--paper);
            border: 1px dashed var(--border);
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 0.85rem;
        }}
        
        .investigation-link {{
            display: block;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
            color: var(--ink);
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}
        
        .investigation-link:hover {{
            color: var(--red);
        }}
        
        .investigation-link:last-child {{
            border-bottom: none;
        }}
        
        .download-btn {{
            display: block;
            width: 100%;
            padding: 12px;
            background: var(--red);
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: background 0.2s;
        }}
        
        .download-btn:hover {{
            background: #8b1f19;
        }}
        
        /* Data science callout */
        .sidebar-section:has(.download-btn[style*="d2691e"]) {{
            background: #fff9f0;
            border: 2px solid var(--orange);
        }}
        
        /* Ad Placements */
        .ad-placement {{
            background: var(--paper);
            border: 1px dashed var(--border);
            min-height: 250px;
            margin: 40px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 0.9rem;
        }}
        
        /* Footer */
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

<!-- Site Header -->
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

<!-- Main Content -->
<div class="container">
    <div class="page-layout">
        
        <!-- Main Column (Claude's visualization content) -->
        <main>
            {viz_content}
        </main>
        
        <!-- Sidebar -->
        <aside class="sidebar">
            
            <!-- Ad Block -->
            <div class="sidebar-section">
                <div class="sidebar-title">Advertisement</div>
                <div class="sidebar-ad">
                    <!-- AdSense Sidebar Ad -->
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-9045696717764033"
                         data-ad-slot="sidebar"
                         data-ad-format="auto"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
                </div>
            </div>
            
            <!-- More Investigations -->
            <div class="sidebar-section">
                <div class="sidebar-title">More Investigations</div>
                <a href="../investigations/bird-strikes.html" class="investigation-link">
                    35 Years of FAA Bird Strike Data
                </a>
                <a href="../investigations/hollywood.html" class="investigation-link">
                    Hollywood's Box Office Formula
                </a>
                <a href="../investigations/car-crashes.html" class="investigation-link">
                    2M NYC Traffic Crashes Analyzed
                </a>
            </div>
            
            <!-- Data Science Deep Dive -->
            <div class="sidebar-section">
                <div class="sidebar-title">🔬 For Data Nerds</div>
                <a href="dark-money-data-analysis.html" class="download-btn" style="background: #d2691e; margin-bottom: 12px;">
                    📊 Statistical Analysis
                </a>
                <p style="font-size: 0.85rem; color: #666; line-height: 1.5;">
                    See all formulas, calculations, and statistical tests behind this investigation.
                </p>
            </div>
            
            <!-- Download Data -->
            <div class="sidebar-section">
                <div class="sidebar-title">Download Data</div>
                <a href="../{dataset}" class="download-btn" download>
                    📊 Download Raw CSV
                </a>
            </div>
            
            <!-- Share -->
            <div class="sidebar-section">
                <div class="sidebar-title">Share This</div>
                <div style="display: flex; gap: 8px; flex-direction: column;">
                    <button onclick="shareTwitter()" style="padding: 10px; background: #1DA1F2; color: white; border: none; border-radius: 4px; cursor: pointer;">Share on X</button>
                    <button onclick="shareFacebook()" style="padding: 10px; background: #1877F2; color: white; border: none; border-radius: 4px; cursor: pointer;">Share on Facebook</button>
                    <button onclick="copyLink()" style="padding: 10px; background: #666; color: white; border: none; border-radius: 4px; cursor: pointer;">Copy Link</button>
                </div>
            </div>
            
        </aside>
        
    </div>
</div>

<!-- Footer -->
<footer>
    <div class="footer-content">
        <div>
            <div class="footer-logo">RECORDS<span>REVEAL</span></div>
            <p class="footer-about">
                Independent investigative data journalism. We analyze public government 
                records and publish findings in plain English. Built on Python, machine 
                learning, and a commitment to transparency.
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

<script>
// Share functions
function shareTwitter() {{
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://twitter.com/intent/tweet?text=${{text}}&url=${{url}}`, '_blank');
}}

function shareFacebook() {{
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${{url}}`, '_blank');
}}

function copyLink() {{
    navigator.clipboard.writeText(window.location.href).then(() => {{
        alert('Link copied to clipboard!');
    }});
}}
</script>

</body>
</html>"""
    
    return html

def render_complete(investigation_json_path, output_dir="investigations"):
    """Complete rendering with all features"""
    
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*10 + "🎨 COMPLETE RENDERER - All Features" + " "*18 + "║")
    print("╚"+"═"*68+"╝\n")
    
    # Load investigation
    print("📂 Loading investigation...")
    with open(investigation_json_path, 'r') as f:
        data = json.load(f)
    
    # Handle both old and new JSON formats
    if 'investigation' in data:
        investigation = data['investigation']  # New format from investigate.py v2
    else:
        investigation = data  # Old format
    
    headline = investigation.get('headline', '')[:60]
    findings_count = len(investigation.get('findings', []))
    
    print(f"✅ Loaded: {headline}...")
    print(f"   Findings: {findings_count}\n")
    
    # Generate investigation ID
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    investigation_id = f"investigation-{timestamp}"
    
    # Step 1: Generate hero image
    print("STEP 1: Generate hero image (Leonardo.ai)...")
    hero_image = generate_hero_image(investigation, investigation_id)
    
    # Step 2: Generate visualization
    print("\nSTEP 2: Generate visualization (Claude)...")
    viz_content = generate_visualization(investigation)
    
    if not viz_content:
        print("❌ Visualization failed")
        return None
    
    # Step 3: Create complete page
    print("\nSTEP 3: Assemble complete page...")
    html = create_complete_page(investigation, viz_content, investigation_id, hero_image)
    
    # Save
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{investigation_id}.html")
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    size_kb = len(html) / 1024
    
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*18 + "✅ COMPLETE RENDERING DONE!" + " "*19 + "║")
    print("╚"+"═"*68+"╝\n")
    print(f"📁 Output: {output_file}")
    print(f"📏 Size: {size_kb:.1f}KB")
    print(f"🖼️  Hero image: {hero_image or 'Not generated'}")
    print(f"💰 Cost: ~$0.02-0.08")
    
    print(f"\n✨ FEATURES INCLUDED:")
    print(f"   ✅ Hero image (Leonardo.ai)")
    print(f"   ✅ 3 AdSense placements in content")
    print(f"   ✅ Sidebar with ads")
    print(f"   ✅ Links to other investigations")
    print(f"   ✅ Data download button")
    print(f"   ✅ Share buttons")
    print(f"   ✅ Professional header/footer")
    
    print(f"\n🚀 Open in browser:")
    print(f"   open {output_file}\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_complete.py <investigation_json>")
        print("\nExample:")
        print("  python render_complete.py investigation_output/investigation-*.json")
        print("\nFeatures:")
        print("  - Leonardo.ai hero images")
        print("  - Google AdSense placements")
        print("  - Sidebar with ads, links, data download")
        print("  - Professional layout")
        sys.exit(1)
    
    investigation_json = sys.argv[1]
    
    if not os.path.exists(investigation_json):
        print(f"❌ Error: File not found: {investigation_json}")
        sys.exit(1)
    
    render_complete(investigation_json)

if __name__ == "__main__":
    main()
