#!/usr/bin/env python3
"""
RecordsReveal Homepage Updater
===============================

Adds a new investigation card to index.html

Usage:
    python3 update_homepage.py full_article.json \\
        --inv-number 004 \\
        --category "Crime Analysis" \\
        --emoji "🚔" \\
        --label "CRIME DATA" \\
        --filename "investigation-004.html"

Author: RecordsReveal Data Team
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_investigation_card(article_data, inv_number, category, emoji, label, filename):
    """Generate HTML for investigation card"""
    
    ai = article_data.get('ai_content', {})
    hero = article_data.get('hero', {})
    
    # Format numbers
    total_records = hero.get('total_records', 0)
    if total_records >= 1000000:
        records_formatted = f"{total_records/1000000:.1f}M"
    elif total_records >= 1000:
        records_formatted = f"{total_records/1000:.1f}K"
    else:
        records_formatted = str(total_records)
    
    headline = ai.get('headline', 'Investigation Results')
    subhead = ai.get('subhead', '')
    
    # Extract key stat from og_description or subhead
    og_desc = ai.get('og_description', subhead)
    
    card_html = f'''      <!-- INVESTIGATION #{inv_number}: {category.upper()} -->
      <div style="display:grid;grid-template-columns:180px 1fr;gap:24px;border-bottom:2px solid var(--border2);margin-bottom:36px;padding-bottom:28px;align-items:start">
        <div class="story-card-img" style="height:110px;margin:0;font-size:1.1rem;flex-direction:column;gap:4px;display:flex;align-items:center;justify-content:center">
          <div>{emoji}</div>
          <div>{label}</div>
        </div>
        <div>
          <div class="hero-tag">Investigation #{inv_number} · Live Now</div>
          <div class="story-card-kicker" style="margin-top:8px">{category}</div>
          <h2 class="story-card-headline" style="font-size:1.15rem;margin-bottom:8px"><a href="investigations/{filename}">{headline}</a></h2>
          <p class="story-card-dek">{og_desc}</p>
          <div class="story-card-meta">RecordsReveal Data Team · {datetime.now().strftime("%B %Y")} · 12 min read · <span style="color:var(--red);font-weight:600">{records_formatted} records analyzed</span></div>
        </div>
      </div>

'''
    
    return card_html


def update_homepage(new_card_html, index_path):
    """Insert new investigation card into homepage"""
    
    with open(index_path, 'r') as f:
        html_content = f.read()
    
    # Find the insertion point (before "SECTION: COMING INVESTIGATIONS")
    marker = '      <!-- SECTION: COMING INVESTIGATIONS -->'
    
    if marker not in html_content:
        print("❌ Could not find insertion marker in index.html")
        print("   Looking for: <!-- SECTION: COMING INVESTIGATIONS -->")
        return False
    
    # Insert the new card before the marker
    updated_html = html_content.replace(marker, new_card_html + marker)
    
    # Write back
    with open(index_path, 'w') as f:
        f.write(updated_html)
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_homepage.py <full_article.json> [options]")
        print("\nOptions:")
        print("  --inv-number <num>      Investigation number (default: 004)")
        print("  --category <name>       Category name (default: 'Data Analysis')")
        print("  --emoji <emoji>         Emoji for card (default: 📊)")
        print("  --label <text>          Label text (default: 'DATA')")
        print("  --filename <file>       HTML filename (default: 'investigation-004.html')")
        print("\nExample:")
        print("  python3 update_homepage.py analysis_results/full_article.json \\")
        print("    --inv-number 004 \\")
        print("    --category 'FBI Crime Analysis' \\")
        print("    --emoji '🚔' \\")
        print("    --label 'CRIME DATA' \\")
        print("    --filename 'fbi-crime.html'")
        sys.exit(1)
    
    article_path = Path(sys.argv[1])
    
    # Parse options
    inv_number = "004"
    category = "Data Analysis"
    emoji = "📊"
    label = "DATA"
    filename = "investigation-004.html"
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--inv-number' and i + 1 < len(sys.argv):
            inv_number = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--emoji' and i + 1 < len(sys.argv):
            emoji = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--label' and i + 1 < len(sys.argv):
            label = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--filename' and i + 1 < len(sys.argv):
            filename = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if not article_path.exists():
        print(f"❌ Article file not found: {article_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("RecordsReveal Homepage Updater")
    print("=" * 60)
    
    # Load article data
    print(f"\n📂 Loading article data...")
    article_data = load_json(article_path)
    print(f"   ✅ {article_path}")
    
    # Generate card HTML
    print(f"\n🔨 Generating investigation card...")
    print(f"   Investigation #: {inv_number}")
    print(f"   Category: {category}")
    print(f"   Emoji: {emoji}")
    print(f"   Label: {label}")
    print(f"   Filename: {filename}")
    
    card_html = create_investigation_card(
        article_data, inv_number, category, emoji, label, filename
    )
    
    # Find index.html
    index_path = Path(__file__).parent / 'index.html'
    if not index_path.exists():
        print(f"\n❌ index.html not found at: {index_path}")
        sys.exit(1)
    
    # Create backup
    backup_path = index_path.parent / 'index.html.backup'
    print(f"\n💾 Creating backup...")
    import shutil
    shutil.copy(index_path, backup_path)
    print(f"   ✅ Backup saved: {backup_path}")
    
    # Update homepage
    print(f"\n✏️  Updating homepage...")
    success = update_homepage(card_html, index_path)
    
    if success:
        print(f"   ✅ Investigation card added to index.html")
        print("\n" + "=" * 60)
        print("✅ HOMEPAGE UPDATED!")
        print("=" * 60)
        print(f"\n📝 Changes:")
        print(f"   - Added Investigation #{inv_number}")
        print(f"   - Inserted before 'Coming Investigations' section")
        print(f"   - Backup saved: {backup_path.name}")
        print(f"\n🌐 Review the changes:")
        print(f"   open {index_path}")
    else:
        print("\n❌ Update failed!")
        print("   Restoring from backup...")
        shutil.copy(backup_path, index_path)
        print("   ✅ Restored original")


if __name__ == "__main__":
    main()
