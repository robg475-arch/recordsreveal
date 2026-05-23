#!/usr/bin/env python3
"""
Update favicon version across all HTML pages
"""
import glob
import re

def update_favicon_version(filepath):
    """Update favicon version to v=4"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has favicon link
    if 'favicon.svg' not in content:
        print(f"  ⏭️  {filepath} - no favicon link found")
        return False
    
    # Update version parameter or add it
    patterns = [
        (r'href="/favicon\.svg\?v=\d+"', 'href="/favicon.svg?v=4"'),
        (r'href="/favicon\.svg"', 'href="/favicon.svg?v=4"'),
    ]
    
    updated = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"  ✅ {filepath}")
                updated = True
                break
    
    if not updated:
        print(f"  ⚠️  {filepath} - no changes needed")
    
    return updated

# Process all HTML files
print("Updating favicon version to v=4 across all pages...\n")

files = [
    'index.html',
    'about/index.html',
    'contact/index.html',
    'privacy/index.html'
] + glob.glob('investigations/*.html')

updated = 0
for filepath in files:
    try:
        if update_favicon_version(filepath):
            updated += 1
    except Exception as e:
        print(f"  ❌ {filepath} - Error: {e}")

print(f"\n✅ Updated {updated} file(s) to favicon version 4")
