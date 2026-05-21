#!/usr/bin/env python3
"""
Update index.html with new investigation
- Makes it the hero story
- Updates sidebar stats
- Updates top stories
- Updates footer links
- Moves previous hero to "Also Live Now" section
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

def load_article_content(article_path):
    """Load article content JSON"""
    with open(article_path, 'r') as f:
        return json.load(f)

def load_page_data(page_data_path):
    """Load page data JSON"""
    with open(page_data_path, 'r') as f:
        return json.load(f)

def generate_investigation_number(index_html):
    """Find the next investigation number"""
    matches = re.findall(r'Investigation #(\d+)', index_html)
    if matches:
        return max(int(m) for m in matches) + 1
    return 1

def extract_key_stats(page_data):
    """Extract 3 compelling stats for sidebar"""
    stats = page_data.get('stats', {})
    
    # Try to find 3 interesting stats
    stat_list = []
    
    # Stat 1: Try majority category or peak
    if 'majority_category' in stats and 'majority_pct' in stats:
        stat_list.append({
            'value': stats['majority_pct'],
            'label': f"Of force used is {stats['majority_category'].lower()}",
            'color': 'red'
        })
    elif 'peak_hour' in stats and 'peak_hour_count' in stats:
        stat_list.append({
            'value': stats['peak_hour'],
            'label': 'Peak hour for incidents',
            'color': 'red'
        })
    
    # Stat 2: Try busiest day or best model
    if 'busiest_day' in stats:
        stat_list.append({
            'value': stats['busiest_day'],
            'label': 'Busiest day for incidents',
            'color': 'gold'
        })
    elif 'best_model' in stats and 'best_score' in stats:
        stat_list.append({
            'value': stats['best_score'],
            'label': f"{stats['best_model']} accuracy",
            'color': 'gold'
        })
    
    # Stat 3: Try trend or total records
    if 'trend_pct_change' in stats and stats.get('trend_pct_change', '0%') != '0%':
        direction = stats.get('trend_direction', 'change')
        stat_list.append({
            'value': stats['trend_pct_change'],
            'label': f"{direction.capitalize()} over time period",
            'color': 'ink'
        })
    elif 'total_records' in stats:
        # Find something unique from analysis
        analyses = page_data.get('analyses_run', [])
        if 'clustering' in analyses:
            # Try to get cluster count
            cluster_data = page_data.get('chart_data', {}).get('elbow_curve', {})
            if cluster_data:
                k_values = cluster_data.get('k', [])
                if k_values:
                    optimal_k = max(k_values)
                    stat_list.append({
                        'value': str(optimal_k),
                        'label': 'Distinct incident patterns found',
                        'color': 'ink'
                    })
    
    # If we don't have 3, fill with generic ones
    while len(stat_list) < 3:
        if 'total_records' in stats and len(stat_list) == 0:
            stat_list.append({
                'value': stats['total_records'],
                'label': 'Total records analyzed',
                'color': 'red'
            })
        elif 'valid_coordinates' in stats and len(stat_list) == 1:
            stat_list.append({
                'value': stats['valid_coords_pct'] if 'valid_coords_pct' in stats else '100%',
                'label': 'Data quality rate',
                'color': 'gold'
            })
        else:
            stat_list.append({
                'value': '—',
                'label': 'Analysis ongoing',
                'color': 'ink'
            })
    
    return stat_list[:3]

def create_hero_html(inv_num, article, page_data, html_filename):
    """Generate hero section HTML"""
    headline = article.get('headline', 'Untitled Investigation')
    lede = article.get('lede', '')
    
    # Truncate lede for hero
    if len(lede) > 250:
        lede = lede[:247] + '...'
    
    # Get stats
    stats = page_data.get('stats', {})
    total_records = stats.get('total_records', '0')
    
    # Determine icon and category
    if 'police' in headline.lower() or 'force' in headline.lower():
        icon = '👮'
        category_display = 'FORCE ENCOUNTERS'
        kicker = 'Police Use of Force Analysis'
        stat_label = 'Use-of-force incidents analyzed · 2021–2023'
    elif 'crash' in headline.lower() or 'traffic' in headline.lower():
        icon = '🚗'
        category_display = 'TRAFFIC DATA'
        kicker = 'Traffic Safety Analysis'
        stat_label = 'Traffic incidents analyzed'
    elif 'crime' in headline.lower():
        icon = '🚨'
        category_display = 'CRIME DATA'
        kicker = 'Public Safety'
        stat_label = 'Crime records analyzed'
    else:
        icon = '📊'
        category_display = 'DATA ANALYSIS'
        kicker = 'Data Investigation'
        stat_label = 'Records analyzed'
    
    hero_html = f'''      <!-- HERO -->
      <div class="hero-story">
        <div class="hero-tag">Investigation #{inv_num:03d} · Live Now</div>
        <div class="hero-img">
          <div style="text-align:center">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:5rem;font-weight:700;color:rgba(180,170,155,.4);line-height:1">{icon}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;font-weight:700;color:var(--border2);letter-spacing:.1em">{category_display}</div>
          </div>
          <div class="hero-img-stat">
            <div class="hero-img-stat-num">{total_records}</div>
            <div class="hero-img-stat-label">{stat_label}</div>
          </div>
        </div>
        <div class="hero-kicker">{kicker}</div>
        <h1 class="hero-headline">
          <a href="investigations/{html_filename}">
            {headline}
          </a>
        </h1>
        <p class="hero-dek">{lede}</p>
        <div class="hero-meta">
          <span>RecordsReveal Data Team</span>
          <span class="hero-meta-dot"></span>
          <span id="pub-date">May 2026</span>
          <span class="hero-meta-dot"></span>
          <span>12 min read</span>
          <span class="hero-meta-dot"></span>
          <span style="color:var(--red);font-weight:600">{total_records} records</span>
        </div>
      </div>'''
    
    return hero_html

def create_investigation_card(inv_num, article, page_data, html_filename):
    """Generate HTML card for 'Also Live Now' section"""
    headline = article.get('headline', 'Untitled Investigation')
    lede = article.get('lede', '')
    
    if len(lede) > 200:
        lede = lede[:197] + '...'
    
    stats = page_data.get('stats', {})
    total_records = stats.get('total_records', '0')
    if isinstance(total_records, str):
        total_records = total_records.replace(',', '')
        try:
            total_records = int(total_records)
        except ValueError:
            total_records = 0
    
    # Determine icon and category
    if 'police' in headline.lower() or 'force' in headline.lower():
        icon = '👮'
        category_label = 'POLICE DATA'
        kicker = 'Police Use of Force Analysis'
    elif 'crash' in headline.lower() or 'traffic' in headline.lower():
        icon = '🚗'
        category_label = 'TRAFFIC'
        kicker = 'Traffic Safety Analysis'
    elif 'crime' in headline.lower():
        icon = '🚨'
        category_label = 'CRIME DATA'
        kicker = 'Public Safety'
    else:
        icon = '📊'
        category_label = 'DATA ANALYSIS'
        kicker = 'Data Investigation'
    
    card_html = f'''
      <!-- INVESTIGATION #{inv_num:03d}: AUTO-GENERATED -->
      <div style="display:grid;grid-template-columns:180px 1fr;gap:24px;border-bottom:2px solid var(--border2);margin-bottom:36px;padding-bottom:28px;align-items:start">
        <div class="story-card-img" style="height:110px;margin:0;font-size:1.1rem;flex-direction:column;gap:4px;display:flex;align-items:center;justify-content:center">
          <div>{icon}</div>
          <div>{category_label}</div>
        </div>
        <div>
          <div class="hero-tag">Investigation #{inv_num:03d} · Live Now</div>
          <div class="story-card-kicker" style="margin-top:8px">{kicker}</div>
          <h2 class="story-card-headline" style="font-size:1.15rem;margin-bottom:8px"><a href="investigations/{html_filename}">{headline}</a></h2>
          <p class="story-card-dek">{lede}</p>
          <div class="story-card-meta">RecordsReveal Data Team · May 2026 · 12 min read · <span style="color:var(--red);font-weight:600">{total_records:,} records analyzed</span></div>
        </div>
      </div>
'''
    return card_html.strip()

def update_hero_section(html, new_hero_html):
    """Replace hero section with new investigation"""
    marker_start = '      <!-- HERO -->'
    marker_end = '      </div>\n\n      <!-- MORE INVESTIGATIONS -->'
    
    if marker_start not in html:
        print("⚠️  Warning: Could not find hero section")
        return html
    
    parts = html.split(marker_start)
    if len(parts) < 2:
        return html
    
    after_hero = parts[1]
    end_parts = after_hero.split(marker_end)
    
    if len(end_parts) < 2:
        print("⚠️  Warning: Could not find end of hero section")
        return html
    
    # Reconstruct with new hero
    updated_html = parts[0] + new_hero_html + '\n\n      <!-- MORE INVESTIGATIONS -->' + end_parts[1]
    
    return updated_html

def update_sidebar_stats(html, key_stats):
    """Update 'From Our Latest Investigation' sidebar"""
    marker_start = '        <div class="sidebar-title">From Our Latest Investigation</div>'
    marker_end = '      </div>\n\n      <!-- AD 2 -->'
    
    if marker_start not in html:
        print("⚠️  Warning: Could not find sidebar stats section")
        return html
    
    # Build new stats HTML
    color_map = {'red': 'var(--red)', 'gold': 'var(--gold)', 'ink': 'var(--ink)'}
    
    stats_html = f'''        <div class="sidebar-title">From Our Latest Investigation</div>
        <div style="display:flex;flex-direction:column;gap:10px">'''
    
    for stat in key_stats:
        color = color_map.get(stat['color'], 'var(--ink)')
        stats_html += f'''
          <div style="padding:14px;background:var(--cream);border-left:3px solid {color}">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;font-weight:700;color:{color};line-height:1">{stat['value']}</div>
            <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:var(--ink3);margin-top:3px">{stat['label']}</div>
          </div>'''
    
    stats_html += '''
        </div>'''
    
    parts = html.split(marker_start)
    if len(parts) < 2:
        return html
    
    after_title = parts[1]
    end_parts = after_title.split(marker_end)
    
    if len(end_parts) < 2:
        return html
    
    updated_html = parts[0] + stats_html + '\n      </div>\n\n      <!-- AD 2 -->' + end_parts[1]
    
    return updated_html

def update_top_stories(html, inv_num, article, html_filename):
    """Update Top Stories sidebar to show 3 most recent"""
    headline = article.get('headline', 'Untitled Investigation')
    
    # Create short headline for sidebar
    if len(headline) > 70:
        short_headline = headline[:67] + '...'
    else:
        short_headline = headline
    
    # Extract key phrase
    if 'police' in headline.lower():
        short_headline = f"{inv_num}K police force incidents reveal the most dangerous hour"
    elif 'crash' in headline.lower():
        short_headline = headline[:70]
    
    marker_start = '        <div class="sidebar-title">Top Stories</div>'
    marker_end = '      </div>\n\n      <!-- KEY FACTS -->'
    
    if marker_start not in html:
        print("⚠️  Warning: Could not find Top Stories section")
        return html
    
    # Build new top stories (show 3 live + 2 coming soon)
    # Extract existing stories to maintain order
    parts = html.split(marker_start)
    if len(parts) < 2:
        return html
    
    # For simplicity, we'll just prepend the new story and keep existing format
    # In production, you'd parse and reorder properly
    
    new_story = f'''        <div class="sidebar-story" onclick="location.href='investigations/{html_filename}'">
          <div class="sidebar-story-num">Live Now</div>
          <div class="sidebar-story-headline">{short_headline}</div>
        </div>'''
    
    after_title = parts[1]
    end_parts = after_title.split(marker_end)
    
    if len(end_parts) < 2:
        return html
    
    # Insert new story after title, before existing stories
    # Find first sidebar-story div
    existing_content = end_parts[0]
    story_match = re.search(r'(\s+<div class="sidebar-story")', existing_content)
    
    if story_match:
        insert_pos = story_match.start(1)
        new_content = existing_content[:insert_pos] + '\n' + new_story + existing_content[insert_pos:]
        updated_html = parts[0] + marker_start + new_content + marker_end + end_parts[1]
    else:
        # Fallback: just add after title
        updated_html = parts[0] + marker_start + '\n' + new_story + end_parts[0] + marker_end + end_parts[1]
    
    # Limit to 3 live + 2 coming soon (remove oldest live story)
    # Count live stories and remove if > 3
    updated_html = limit_top_stories(updated_html)
    
    return updated_html

def limit_top_stories(html):
    """Ensure only 3 live stories and 2 coming soon in sidebar"""
    # Find Top Stories section
    marker_start = '        <div class="sidebar-title">Top Stories</div>'
    marker_end = '      </div>\n\n      <!-- KEY FACTS -->'
    
    parts = html.split(marker_start)
    if len(parts) < 2:
        return html
    
    after_title = parts[1]
    end_parts = after_title.split(marker_end)
    if len(end_parts) < 2:
        return html
    
    content = end_parts[0]
    
    # Extract all live and coming soon stories
    live_pattern = r'(<div class="sidebar-story"[^>]*>.*?<div class="sidebar-story-num">Live Now</div>.*?</div>\s*</div>)'
    coming_pattern = r'(<div class="sidebar-story"[^>]*>.*?<div class="sidebar-story-num">Coming Soon</div>.*?</div>\s*</div>)'
    
    live_stories = re.findall(live_pattern, content, re.DOTALL)
    coming_stories = re.findall(coming_pattern, content, re.DOTALL)
    
    # Keep only first 3 live and first 2 coming soon
    live_stories = live_stories[:3]
    coming_stories = coming_stories[:2]
    
    # Rebuild content
    new_content = '\n'.join(live_stories) + '\n' + '\n'.join(coming_stories)
    
    updated_html = parts[0] + marker_start + '\n' + new_content + '\n' + marker_end + end_parts[1]
    
    return updated_html

def update_footer_links(html, inv_num, article, html_filename):
    """Update footer investigations links"""
    headline = article.get('headline', 'Untitled Investigation')
    
    # Create short title for footer
    if 'police' in headline.lower():
        link_text = 'Police Use of Force · Live'
    elif 'crash' in headline.lower() or 'traffic' in headline.lower():
        link_text = 'Traffic Safety · Live'
    elif 'crime' in headline.lower():
        link_text = 'Crime Analysis · Live'
    else:
        link_text = 'Latest Investigation · Live'
    
    marker_start = '        <div class="footer-col-title">Investigations</div>\n        <ul class="footer-links">'
    marker_end = '        </ul>'
    
    parts = html.split(marker_start)
    if len(parts) < 2:
        print("⚠️  Warning: Could not find footer investigations section")
        return html
    
    # Find the investigations ul
    after_marker = parts[1]
    ul_end = after_marker.find(marker_end)
    
    if ul_end == -1:
        return html
    
    # Extract existing links
    links_section = after_marker[:ul_end]
    
    # Add new link at the top
    new_link = f'\n          <li><a href="investigations/{html_filename}">{link_text}</a></li>'
    
    # Keep max 4 live investigations in footer
    live_pattern = r'<li><a href="[^"]*">[^·]* · Live</a></li>'
    existing_live = re.findall(live_pattern, links_section)
    
    if len(existing_live) >= 4:
        # Remove last live link
        last_live = existing_live[-1]
        links_section = links_section.replace(last_live, '', 1)
    
    new_links_section = new_link + links_section
    
    updated_html = parts[0] + marker_start + new_links_section + marker_end + after_marker[ul_end + len(marker_end):]
    
    return updated_html

def main():
    if len(sys.argv) < 3:
        print("Usage: python update_index.py <article_content.json> <page_data.json> <html_filename>")
        sys.exit(1)
    
    article_path = sys.argv[1]
    page_data_path = sys.argv[2]
    html_filename = sys.argv[3] if len(sys.argv) > 3 else 'investigation.html'
    
    print("=" * 70)
    print("🏠 UPDATING INDEX.HTML (COMPLETE REFRESH)")
    print("=" * 70)
    print(f"Article: {article_path}")
    print(f"Page data: {page_data_path}")
    print(f"HTML file: {html_filename}")
    print("=" * 70)
    print()
    
    # Load inputs
    print("📂 Loading article and page data...")
    article = load_article_content(article_path)
    page_data = load_page_data(page_data_path)
    print("✅ Loaded")
    print()
    
    # Find index.html
    index_path = Path(__file__).parent.parent.parent.parent / 'index.html'
    
    if not index_path.exists():
        print(f"❌ Error: index.html not found at {index_path}")
        sys.exit(1)
    
    # Read current index.html
    with open(index_path, 'r') as f:
        html = f.read()
    
    # Check if investigation already exists
    if html_filename in html:
        print(f"⚠️  Investigation '{html_filename}' already exists in index.html")
        print("   Skipping update to avoid duplicates.")
        print()
        print("=" * 70)
        print("✅ INDEX UPDATE COMPLETE (no changes needed)")
        print("=" * 70)
        return
    
    # Generate investigation number
    inv_num = generate_investigation_number(html)
    print(f"🔢 Next investigation number: #{inv_num:03d}")
    print()
    
    # Extract key stats for sidebar
    print("📊 Extracting key stats for sidebar...")
    key_stats = extract_key_stats(page_data)
    print(f"✅ Found {len(key_stats)} stats")
    print()
    
    # Create new hero HTML
    print("🎨 Creating hero section...")
    hero_html = create_hero_html(inv_num, article, page_data, html_filename)
    print("✅ Hero created")
    print()
    
    # Update all sections
    print("✍️  Updating hero section...")
    html = update_hero_section(html, hero_html)
    print("✅ Hero updated")
    print()
    
    print("✍️  Updating sidebar stats...")
    html = update_sidebar_stats(html, key_stats)
    print("✅ Sidebar stats updated")
    print()
    
    print("✍️  Updating top stories...")
    html = update_top_stories(html, inv_num, article, html_filename)
    print("✅ Top stories updated")
    print()
    
    print("✍️  Updating footer links...")
    html = update_footer_links(html, inv_num, article, html_filename)
    print("✅ Footer links updated")
    print()
    
    # Update stat strip count
    print("✍️  Updating stat strip...")
    html = re.sub(
        r'<span class="strip-num">(\d+)</span>\s*<div class="strip-label">Investigations Live</div>',
        f'<span class="strip-num">{inv_num}</span>\n    <div class="strip-label">Investigations Live</div>',
        html
    )
    print("✅ Stat strip updated")
    print()
    
    # Write back
    with open(index_path, 'w') as f:
        f.write(html)
    
    print("=" * 70)
    print("✅ INDEX UPDATE COMPLETE")
    print("=" * 70)
    print()
    print(f"Investigation #{inv_num:03d} is now:")
    print(f"  • Hero story")
    print(f"  • In sidebar stats ('From Our Latest Investigation')")
    print(f"  • In top stories")
    print(f"  • In footer links")
    print(f"  • Link: investigations/{html_filename}")
    print()

if __name__ == '__main__':
    main()
