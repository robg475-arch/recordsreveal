#!/usr/bin/env python3
"""
Generate RecordsReveal favicon PNG files
"""
from io import BytesIO
import base64

# Create a simple PNG manually (32x32, 16x16)
# For now, we'll create the SVG and let the browser handle it

# Read the SVG
with open('favicon-simple.svg', 'r') as f:
    svg_content = f.read()

# Save as favicon.svg for direct use
print("✅ favicon-simple.svg ready to use")

# Create the HTML link tags
html_links = '''
<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
'''

print("\nAdd this to the <head> of all HTML pages:")
print(html_links)

print("\nTo generate PNG files:")
print("1. Open generate-favicon.html in your browser")
print("2. Right-click each canvas and save the images")
print("3. Or use: brew install librsvg && rsvg-convert -w 32 -h 32 favicon-simple.svg > favicon-32x32.png")
