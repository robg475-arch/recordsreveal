#!/usr/bin/env python3
"""
Update All Investigations sidebar and footer sections in existing investigation pages
"""

import json
import re
from pathlib import Path

def load_investigations_registry():
    """Load investigations from registry"""
    with open('investigations_registry.json', 'r') as f:
        data = json.load(f)
        investigations = [inv for inv in data['investigations'] if inv.get('active', True)]
        investigations.sort(key=lambda x: x.get('order', 999))
        return investigations

def generate_sidebar_section(investigations):
    """Generate All Investigations sidebar HTML"""
    html = []
    html.append('      <div class="all-investigations">')
    html.append('        <h3>All Investigations</h3>')
    html.append('        ')
    
    for inv in investigations:
        status = inv.get('status', 'LIVE NOW')
        category = inv.get('category', 'DATA')
        url = inv.get('url', '#')
        headline = inv.get('headline', inv.get('title', 'Untitled'))
        
        html.append('        <div class="investigation-item">')
        html.append(f'          <div class="investigation-tag">{status} · {category}</div>')
        html.append(f'          <a href="{url}" class="investigation-link">{headline}</a>')
        html.append('        </div>')
        html.append('        ')
    
    html.append('      </div>')
    return '\n'.join(html)

def generate_footer_section(investigations):
    """Generate footer investigations list HTML"""
    html = []
    html.append('        <li><a href="investigation-20260521-114147.html">Police Use of Force · Live</a></li>')
    html.append('        <li><a href="car-crashes.html">NYC Traffic Crashes · Live</a></li>')
    html.append('        <li><a href="hollywood.html">Hollywood Box Office · Live</a></li>')
    html.append('        <li><a href="bird-strikes.html">Bird Strikes · Live</a></li>')
    html.append('        <li><a href="#">Food Nutrition · Soon</a></li>')
    html.append('        <li><a href="#">Crime Statistics · Soon</a></li>')
    return '\n'.join(html)

def update_investigation_page(filepath, investigations):
    """Update a single investigation page"""
    print(f"Updating {filepath.name}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Update sidebar section
    sidebar_pattern = r'<div class="all-investigations">.*?</div>\s*\n\s*<div class="sidebar-block">'
    new_sidebar = generate_sidebar_section(investigations)
    new_sidebar += '\n\n      <div class="sidebar-block">'
    
    content = re.sub(sidebar_pattern, new_sidebar, content, flags=re.DOTALL)
    
    # Update footer section - find INVESTIGATIONS section
    footer_pattern = r'<div class="footer-heading">INVESTIGATIONS</div>\s*<ul class="footer-links">.*?</ul>'
    new_footer = f'<div class="footer-heading">INVESTIGATIONS</div>\n      <ul class="footer-links">\n{generate_footer_section(investigations)}\n      </ul>'
    
    content = re.sub(footer_pattern, new_footer, content, flags=re.DOTALL)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  ✅ Updated {filepath.name}")

def main():
    print("🔄 Updating All Investigations sections in existing pages...\n")
    
    # Load registry
    investigations = load_investigations_registry()
    print(f"📋 Loaded {len(investigations)} investigations\n")
    
    # Find all investigation HTML files
    inv_dir = Path('investigations')
    html_files = [
        'bird-strikes.html',
        'hollywood.html', 
        'car-crashes.html',
        'investigation-20260521-114147.html',
        'investigation-20260521-104346.html'
    ]
    
    for filename in html_files:
        filepath = inv_dir / filename
        if filepath.exists():
            update_investigation_page(filepath, investigations)
        else:
            print(f"⚠️  Skipping {filename} (not found)")
    
    print("\n✅ All pages updated!")

if __name__ == "__main__":
    main()
