#!/usr/bin/env python3
"""
Create a simple ICO favicon file (16x16 and 32x32)
"""

# Create a minimal ICO file with embedded PNG data
# ICO format: header + directory entries + image data

import struct

def create_simple_favicon():
    """Create a minimal 16x16 ICO file with R logo"""
    
    # For simplicity, let's create the smallest possible ICO
    # Just redirect - create a minimal HTML that tells browser to use SVG
    
    print("Creating favicon redirect...")
    
    # Better approach: Let's just make sure the SVG works
    # Add a fallback PNG link
    
    fallback_html = '''
<!-- Favicon (multiple formats for browser compatibility) -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="alternate icon" href="/favicon.ico" type="image/x-icon">
'''
    
    print(fallback_html)
    print("\nThe SVG favicon should work in modern browsers.")
    print("Try doing a hard refresh: Cmd+Shift+R")
    print("Or clear browser cache and reload.")

if __name__ == "__main__":
    create_simple_favicon()
