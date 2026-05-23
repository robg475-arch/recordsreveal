#!/usr/bin/env python3
"""
RecordsReveal Amazing HTML Generator
Give Claude COMPLETE freedom to design stunning visualizations
No templates. No constraints. Just amazing.
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
    """Send prompt to Claude API with extended token limit for HTML generation"""
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
                max_tokens=16000,  # Much more tokens for complete HTML with charts
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

def render_amazing_html(investigation_json_path, output_dir="investigations"):
    """
    Let Claude create AMAZING HTML with complete creative freedom
    """
    print("\n" + "╔"+"═"*68+"╗")
    print("║" + " "*15 + "🎨 CLAUDE AMAZING HTML DESIGNER" + " "*20 + "║")
    print("╚"+"═"*68+"╝\n")
    
    print("="*70)
    print("Giving Claude COMPLETE creative freedom to design stunning HTML")
    print("="*70 + "\n")
    
    # Load investigation
    print("📂 Loading investigation...")
    with open(investigation_json_path, 'r') as f:
        investigation = json.load(f)
    
    # Extract all data for Claude
    headline = investigation.get('headline', 'Untitled Investigation')
    lede = investigation.get('lede', '')
    findings = investigation.get('findings', [])
    pull_quotes = investigation.get('pull_quotes', [])
    methodology = investigation.get('methodology', '')
    stat_boxes = investigation.get('stat_boxes', [])
    data_analysis = investigation.get('data_analysis', {})
    
    print(f"✅ Loaded investigation")
    print(f"   Headline: {headline[:60]}...")
    print(f"   Findings: {len(findings)}")
    print(f"   Stats available: {len(stat_boxes)}")
    print(f"   Ollama analysis available: {'ollama_analysis' in data_analysis}\n")
    
    # Create comprehensive prompt for Claude
    claude_prompt = f"""You are a world-class data visualization designer and web developer. 
I'm giving you an investigative journalism piece about dark money in politics, along with all the data analysis.

Your mission: Create the most STUNNING, interactive, professional HTML report possible. 

# THE DATA

**Headline:** {headline}

**Lede:** {lede}

**Key Statistics:**
{json.dumps(stat_boxes, indent=2)}

**Findings:**
{json.dumps(findings, indent=2)}

**Pull Quotes:**
{json.dumps(pull_quotes, indent=2)}

**Raw Data Analysis:**
{data_analysis.get('ollama_analysis', 'Not available')[:3000]}...

# YOUR CHALLENGE

Design a STUNNING single-page HTML report that includes:

1. **Hero Section** with the headline and a dramatic visual treatment
2. **Interactive KPI Dashboard** - Show the key stats as cards/tiles with hover effects
3. **Charts & Graphs** - Use Chart.js or D3.js (via CDN) to visualize:
   - Attack vs Support spending (bar chart or donut)
   - Top spenders (horizontal bar chart)
   - Geographic distribution (could be a map or bar chart by state)
   - Concentration (stacked area or line chart)
   - Any other data you can extract from the findings
4. **Findings Sections** - Beautiful cards with icons, pull quotes as callouts
5. **Interactive Elements** - Tooltips, hover states, smooth scrolling
6. **Professional Design:**
   - Modern color scheme (suggest: dark blues, reds for emphasis, clean whites)
   - Beautiful typography (use Google Fonts)
   - Responsive layout
   - Smooth animations
   - Professional shadows and spacing

# TECHNICAL REQUIREMENTS

- Single HTML file (all CSS inline or in <style>, all JS inline or in <script>)
- Use CDN for libraries (Chart.js, optional: D3.js, Tailwind CSS if you want)
- Must work offline after first load
- Professional, publication-quality
- Mobile responsive
- Fast loading

# DESIGN INSPIRATION

Think: New York Times graphics, The Pudding, FiveThirtyEight data stories.
Make it interactive. Make it beautiful. Make it STUNNING.

# CRITICAL REQUIREMENTS

1. **COMPLETE HTML**: Must end with </body></html> - no truncation
2. **WORKING CHARTS**: Include ALL JavaScript to initialize Chart.js with REAL DATA from the findings
3. **SELF-CONTAINED**: Single file, all CSS/JS inline, works offline
4. **TESTED STRUCTURE**: Proper HTML5 structure with all closing tags

# CHART DATA TO USE

Extract numbers from the findings and stats to populate charts. For example:
- Attack vs Support: $1.17B vs $679M
- Party breakdown: DEM vs REP spending
- Top spenders: Use the stat boxes
- Geographic: Top states if mentioned
- Concentration: Top 10 districts data

You MUST include the Chart.js initialization JavaScript in <script> tags before </body>.

# OUTPUT FORMAT

Return ONLY the complete HTML. No explanations. No markdown wrapper.
Start with: <!DOCTYPE html>
End with: </html>

The HTML must be production-ready and work perfectly when opened in a browser.

MAKE IT AMAZING. CHECK YOUR WORK."""

    print("🎨 Asking Claude to design stunning HTML...")
    print("   (This may take 30-60 seconds for full HTML generation)\n")
    
    html = ask_claude(claude_prompt)
    
    if not html:
        print("❌ Failed to generate HTML")
        return None
    
    # Clean up response
    html = html.strip()
    if html.startswith("```html"):
        html = html[7:]
    if html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]
    html = html.strip()
    
    # Validate HTML is complete
    if not html.endswith("</html>"):
        print("\n⚠️  WARNING: HTML appears incomplete (doesn't end with </html>)")
        print("   Last 200 chars:", html[-200:])
        return None
    
    if "</body>" not in html:
        print("\n⚠️  WARNING: HTML missing </body> tag")
        return None
    
    if "<script>" not in html.lower() or "chart" not in html.lower():
        print("\n⚠️  WARNING: HTML may be missing chart JavaScript")
    
    # Count charts
    chart_count = html.count("new Chart(") + html.count("new Chart ")
    canvas_count = html.count("<canvas")
    
    print(f"\n✅ HTML validation:")
    print(f"   - Properly closed: {'</html>' in html}")
    print(f"   - Canvas elements: {canvas_count}")
    print(f"   - Chart initializations: {chart_count}")
    
    if canvas_count > 0 and chart_count == 0:
        print("\n⚠️  WARNING: Found canvas elements but no Chart.js initialization!")
        print("   The charts will appear as empty boxes.")
        return None
    
    # Save HTML
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_dir, f"amazing-{timestamp}.html")
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    file_size_kb = len(html) / 1024
    
    print("╔"+"═"*68+"╗")
    print("║" + " "*20 + "✅ AMAZING HTML GENERATED!" + " "*21 + "║")
    print("╚"+"═"*68+"╝\n")
    print(f"📁 Output: {output_file}")
    print(f"📏 Size: {file_size_kb:.1f}KB")
    print(f"💰 Cost: ~$0.02-0.05 (Claude HTML generation)")
    print(f"\n🎨 Claude designed:")
    print(f"   - Hero section")
    print(f"   - Interactive KPI dashboard")
    print(f"   - Charts & visualizations")
    print(f"   - Beautiful findings cards")
    print(f"   - Professional styling")
    
    print(f"\n🚀 Open in browser:")
    print(f"   open {output_file}\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_amazing.py <investigation_json>")
        print("\nExample:")
        print("  python render_amazing.py investigation_output/investigation-*.json")
        print("\nThis will:")
        print("  - Give Claude COMPLETE creative freedom")
        print("  - Generate stunning HTML with charts, KPIs, interactions")
        print("  - No templates, no constraints")
        print("  - Just amazing data visualization")
        sys.exit(1)
    
    investigation_json = sys.argv[1]
    
    if not os.path.exists(investigation_json):
        print(f"❌ Error: File not found: {investigation_json}")
        sys.exit(1)
    
    render_amazing_html(investigation_json)

if __name__ == "__main__":
    main()
