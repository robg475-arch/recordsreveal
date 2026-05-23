#!/usr/bin/env python3
"""
Add favicon link to all HTML pages
"""
import glob
import re

favicon_link = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'

def add_favicon(filepath):
    """Add favicon link to HTML file if not already present"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if favicon already exists
    if 'favicon.svg' in content or 'rel="icon"' in content:
        print(f"  ⏭️  {filepath} - already has favicon")
        return False
    
    # Find the first </head> or <script> tag and insert before it
    # Try multiple patterns
    patterns = [
        (r'(<!-- Google Analytics 4 -->)', f'{favicon_link}\n\\1'),
        (r'(<script async src="https://www.googletagmanager.com)', f'{favicon_link}\n\\1'),
        (r'(<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly)', f'{favicon_link}\n\\1'),
        (r'(<link href="https://fonts.googleapis.com)', f'{favicon_link}\n\\1'),
    ]
    
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content, count=1)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ {filepath}")
            return True
    
    print(f"  ⚠️  {filepath} - couldn't find insertion point")
    return False

# Process all HTML files
print("Adding favicon to HTML pages...\n")

files = [
    'index.html',
    'about/index.html',
    'contact/index.html',
    'privacy/index.html'
] + glob.glob('investigations/*.html')

updated = 0
for filepath in files:
    try:
        if add_favicon(filepath):
            updated += 1
    except Exception as e:
        print(f"  ❌ {filepath} - Error: {e}")

print(f"\n✅ Updated {updated} file(s)")
