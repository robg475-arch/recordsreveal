#!/usr/bin/env python3
"""
RecordsReveal HTML Renderer
Converts flexible investigation JSON to complete HTML using existing build system
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Import the complete HTML builder
sys.path.insert(0, str(Path(__file__).parent / ".opencode/skills/build-html-page"))
from build import build_html_page

def convert_investigation_to_pipeline_format(investigation):
    """
    Convert new flexible investigation JSON to old pipeline format
    so we can use the existing complete HTML builder
    """
    # Extract data
    headline = investigation.get('headline', 'Untitled Investigation')
    lede = investigation.get('lede', '')
    findings = investigation.get('findings', [])
    pull_quotes = investigation.get('pull_quotes', [])
    methodology = investigation.get('methodology', '')
    stat_boxes = investigation.get('stat_boxes', [])
    dataset = investigation.get('dataset', 'Unknown')
    rows = investigation.get('data_analysis', {}).get('rows', 0)
    
    # Create article_content.json format
    article_content = {
        "dataset": dataset,
        "analyses_used": ["ai_investigation"],
        "headline": headline,
        "lede": lede,
        "findings": findings,
        "pull_quotes": pull_quotes,
        "methodology": methodology
    }
    
    # Create page_data.json format
    page_data = {
        "dataset": dataset,
        "analyses_run": ["ai_investigation"],
        "chart_data": {},  # No charts for now
        "stats": {
            "total_records": f"{rows:,}" if rows else "N/A"
        },
        "insights": {},
        "pull_quotes": pull_quotes
    }
    
    # Add stat boxes to page_data.stats
    for i, stat_box in enumerate(stat_boxes):
        # Map to generic stat names that template understands
        if i == 0:
            page_data["stats"]["stat_1_value"] = stat_box.get('value', 'N/A')
            page_data["stats"]["stat_1_label"] = stat_box.get('label', '')
            page_data["stats"]["stat_1_context"] = stat_box.get('context', '')
        elif i == 1:
            page_data["stats"]["stat_2_value"] = stat_box.get('value', 'N/A')
            page_data["stats"]["stat_2_label"] = stat_box.get('label', '')
            page_data["stats"]["stat_2_context"] = stat_box.get('context', '')
        elif i == 2:
            page_data["stats"]["stat_3_value"] = stat_box.get('value', 'N/A')
            page_data["stats"]["stat_3_label"] = stat_box.get('label', '')
            page_data["stats"]["stat_3_context"] = stat_box.get('context', '')
    
    return article_content, page_data

def render_html(investigation_json_path, output_dir="investigations"):
    """
    Render investigation JSON to complete HTML
    Uses existing complete build system for consistency
    """
    print("\n" + "="*70)
    print("🎨 RECORDSREVEAL HTML RENDERER")
    print("="*70)
    print(f"Input: {investigation_json_path}")
    print(f"Output directory: {output_dir}")
    print("="*70 + "\n")
    
    # Load investigation
    print("📂 Loading investigation...")
    with open(investigation_json_path, 'r') as f:
        investigation = json.load(f)
    
    headline = investigation.get('headline', 'Untitled Investigation')
    findings = investigation.get('findings', [])
    pull_quotes = investigation.get('pull_quotes', [])
    stat_boxes = investigation.get('stat_boxes', [])
    
    print(f"✅ Loaded investigation")
    print(f"   Headline: {headline[:60]}...")
    print(f"   Findings: {len(findings)}")
    print(f"   Pull quotes: {len(pull_quotes)}")
    print(f"   Stat boxes: {len(stat_boxes)}\n")
    
    # Convert to pipeline format
    print("🔄 Converting to pipeline format...")
    article_content, page_data = convert_investigation_to_pipeline_format(investigation)
    
    # Create temp files for build system
    temp_dir = Path(output_dir) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    article_path = temp_dir / "article_content.json"
    page_data_path = temp_dir / "page_data.json"
    
    with open(article_path, 'w') as f:
        json.dump(article_content, f, indent=2)
    
    with open(page_data_path, 'w') as f:
        json.dump(page_data, f, indent=2)
    
    print("✅ Converted to pipeline format\n")
    
    # Build HTML using complete system
    print("🏗️  Building complete HTML (footer, sidebar, share buttons, etc.)...")
    output_file = build_html_page(str(article_path), str(page_data_path), output_dir)
    
    # Clean up temp files
    article_path.unlink()
    page_data_path.unlink()
    temp_dir.rmdir()
    
    print("\n" + "="*70)
    print("✅ HTML RENDERING COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_file}")
    print(f"Findings rendered: {len(findings)}")
    print(f"Stat boxes: {len(stat_boxes)}")
    print(f"Pull quotes: {len(pull_quotes)}")
    
    print(f"\n📖 Open in browser:")
    print(f"  open {output_file}\n")
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python render.py <investigation_json> [output_dir]")
        print("\nExample:")
        print("  python render.py investigation_output/investigation-20260523-090450.json")
        print("\nThis will:")
        print("  1. Load investigation JSON")
        print("  2. Apply COMPLETE RecordsReveal HTML template")
        print("     (footer, sidebar, share buttons, all styling)")
        print("  3. Output ready-to-publish HTML")
        sys.exit(1)
    
    investigation_json = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "investigations"
    
    if not os.path.exists(investigation_json):
        print(f"❌ Error: File not found: {investigation_json}")
        sys.exit(1)
    
    render_html(investigation_json, output_dir)

if __name__ == "__main__":
    main()
