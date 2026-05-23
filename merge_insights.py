#!/usr/bin/env python3
"""
Merge Insights Script
Combines multiple analysis JSON files into one comprehensive insights file
"""

import sys
import os
import json
from pathlib import Path
import glob

def merge_insights(output_dir="analysis_results", output_file="combined_insights.json"):
    """
    Merge all *_insights.json files in output_dir into one combined file
    """
    print("\n" + "="*70)
    print("🔗 MERGING ANALYSIS INSIGHTS")
    print("="*70)
    print(f"Directory: {output_dir}")
    print("="*70 + "\n")
    
    # Find all insight files
    insight_files = glob.glob(os.path.join(output_dir, "*_insights.json"))
    
    if not insight_files:
        print(f"❌ No *_insights.json files found in {output_dir}")
        return None
    
    print(f"Found {len(insight_files)} insight file(s):")
    for f in insight_files:
        print(f"  • {os.path.basename(f)}")
    print()
    
    # Load and merge
    combined = {
        "dataset": None,
        "analyses": [],
        "all_patterns": {},
        "all_ollama_insights": {}
    }
    
    for file_path in insight_files:
        print(f"📖 Reading {os.path.basename(file_path)}...")
        
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            analysis_type = data.get("analysis_type", "unknown")
            
            # Store dataset name (use first one found)
            if not combined["dataset"] and "dataset" in data:
                combined["dataset"] = data["dataset"]
            
            # Add to analyses list
            combined["analyses"].append(analysis_type)
            
            # Merge patterns under analysis type key
            if "patterns" in data:
                combined["all_patterns"][analysis_type] = data["patterns"]
            
            # Merge Ollama insights
            if "ollama_insights" in data:
                combined["all_ollama_insights"][analysis_type] = data["ollama_insights"]
            
            print(f"   ✓ Added {analysis_type} analysis")
            
        except Exception as e:
            print(f"   ⚠️  Error reading {file_path}: {e}")
    
    print()
    
    # Add summary
    combined["summary"] = {
        "total_analyses": len(combined["analyses"]),
        "analysis_types": combined["analyses"],
        "has_ollama_insights": len(combined["all_ollama_insights"]) > 0
    }
    
    # Save combined file
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=2, default=str)
    
    print("="*70)
    print("✅ MERGE COMPLETE")
    print("="*70)
    print(f"\nCombined insights: {output_path}")
    print(f"Total analyses: {len(combined['analyses'])}")
    print(f"Analysis types: {', '.join(combined['analyses'])}")
    print(f"Ollama insights: {len(combined['all_ollama_insights'])}")
    print()
    
    return combined

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "analysis_results"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "combined_insights.json"
    
    merge_insights(output_dir, output_file)
