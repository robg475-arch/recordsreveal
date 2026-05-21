#!/usr/bin/env python3
"""
RecordsReveal Geographic Analysis Skill
Analyzes location-based patterns with Ollama insights
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import numpy as np
from ollama_helper import ask_ollama_write, test_connection

def analyze_geographic_patterns(csv_path, lat_column, lon_column, output_dir="analysis_results"):
    """
    Analyze geographic patterns in the dataset
    """
    print("\n" + "="*70)
    print("🗺️  RECORDSREVEAL GEOGRAPHIC ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Latitude: {lat_column}")
    print(f"Longitude: {lon_column}")
    print(f"Output: {output_dir}")
    print("="*70 + "\n")
    
    # Test Ollama connection
    print("📡 Testing Ollama connection...")
    use_ollama = test_connection()
    if not use_ollama:
        print("⚠️  Ollama not available. Continuing without AI insights.\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load dataset
    print(f"📂 Loading dataset...")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df):,} rows\n")
    
    # Check if columns exist
    if lat_column not in df.columns or lon_column not in df.columns:
        print(f"❌ Error: Columns '{lat_column}' or '{lon_column}' not found")
        print(f"Available columns: {', '.join(df.columns)}")
        return None
    
    results = {
        "analysis_type": "geographic",
        "dataset": str(csv_path),
        "lat_column": lat_column,
        "lon_column": lon_column,
        "patterns": {}
    }
    
    print("="*70)
    print("🔍 ANALYZING GEOGRAPHIC PATTERNS")
    print("="*70 + "\n")
    
    # Clean coordinates (remove nulls)
    df_geo = df[[lat_column, lon_column]].dropna()
    print(f"Valid coordinates: {len(df_geo):,} / {len(df):,} records ({len(df_geo)/len(df)*100:.1f}%)\n")
    
    results["patterns"]["valid_coordinates"] = {
        "count": int(len(df_geo)),
        "total": int(len(df)),
        "percent": float(len(df_geo)/len(df)*100)
    }
    
    # Coordinate bounds
    print("📍 Analyzing coordinate bounds...")
    lat_min, lat_max = df_geo[lat_column].min(), df_geo[lat_column].max()
    lon_min, lon_max = df_geo[lon_column].min(), df_geo[lon_column].max()
    
    results["patterns"]["bounds"] = {
        "lat_min": float(lat_min),
        "lat_max": float(lat_max),
        "lon_min": float(lon_min),
        "lon_max": float(lon_max),
        "center_lat": float((lat_min + lat_max) / 2),
        "center_lon": float((lon_min + lon_max) / 2)
    }
    
    print(f"   Latitude range: {lat_min:.4f} to {lat_max:.4f}")
    print(f"   Longitude range: {lon_min:.4f} to {lon_max:.4f}")
    print(f"   Center: ({results['patterns']['bounds']['center_lat']:.4f}, {results['patterns']['bounds']['center_lon']:.4f})\n")
    
    # Grid-based hotspot detection (simple binning)
    print("🔥 Detecting geographic hotspots...")
    
    # Create 10x10 grid
    lat_bins = np.linspace(lat_min, lat_max, 11)
    lon_bins = np.linspace(lon_min, lon_max, 11)
    
    df_geo['lat_bin'] = pd.cut(df_geo[lat_column], bins=lat_bins, labels=False)
    df_geo['lon_bin'] = pd.cut(df_geo[lon_column], bins=lon_bins, labels=False)
    
    # Count records per grid cell
    grid_counts = df_geo.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')
    hotspots = grid_counts.nlargest(5, 'count')
    
    hotspot_list = []
    for _, row in hotspots.iterrows():
        lat_idx, lon_idx = int(row['lat_bin']), int(row['lon_bin'])
        lat_center = (lat_bins[lat_idx] + lat_bins[lat_idx + 1]) / 2
        lon_center = (lon_bins[lon_idx] + lon_bins[lon_idx + 1]) / 2
        
        hotspot_list.append({
            "lat": float(lat_center),
            "lon": float(lon_center),
            "count": int(row['count']),
            "percent": float(row['count'] / len(df_geo) * 100)
        })
    
    results["patterns"]["hotspots"] = hotspot_list
    
    print(f"   Top 5 hotspots:")
    for i, hs in enumerate(hotspot_list, 1):
        print(f"   {i}. ({hs['lat']:.4f}, {hs['lon']:.4f}) - {hs['count']:,} records ({hs['percent']:.1f}%)")
    print()
    
    # Check for borough/location columns
    location_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['borough', 'city', 'county', 'state', 'zip'])]
    
    if location_cols:
        print(f"📊 Analyzing location columns: {', '.join(location_cols)}")
        results["patterns"]["locations"] = {}
        
        for col in location_cols[:3]:  # Analyze up to 3 location columns
            dist = df[col].value_counts().head(10)
            results["patterns"]["locations"][col] = {
                "top_10": dist.to_dict(),
                "unique_count": int(df[col].nunique())
            }
            print(f"\n   {col} (top 5):")
            for loc, count in dist.head(5).items():
                print(f"      {loc}: {count:,} ({count/len(df)*100:.1f}%)")
        print()
    
    # Ask Ollama for insights
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING AI INSIGHTS (OLLAMA)")
        print("="*70 + "\n")
        
        # Prepare summary for Ollama
        summary = format_geographic_summary(results, location_cols if location_cols else [])
        
        prompt = f"""You are a data journalist analyzing geographic patterns in a dataset.

Here's what I found:
{summary}

Please provide:
1. The most newsworthy geographic finding (1-2 sentences)
2. What this spatial pattern suggests about the data (1-2 sentences)
3. A compelling pull quote about the location findings (10-15 words, quotable)

Keep it journalistic and engaging."""
        
        print("Asking Ollama for geographic insights...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama Geographic Insights:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            results["ollama_insights"] = insights
        else:
            print("⚠️  Could not get Ollama insights\n")
    
    # Save results
    output_path = os.path.join(output_dir, "geographic_insights.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ GEOGRAPHIC ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def format_geographic_summary(results, location_cols):
    """Format geographic results for Ollama"""
    summary = []
    
    patterns = results.get("patterns", {})
    
    if "valid_coordinates" in patterns:
        vc = patterns["valid_coordinates"]
        summary.append(f"Analyzed {vc['count']:,} records with valid coordinates ({vc['percent']:.1f}%)")
    
    if "bounds" in patterns:
        b = patterns["bounds"]
        summary.append(f"Geographic area: {b['lat_min']:.4f} to {b['lat_max']:.4f} lat, {b['lon_min']:.4f} to {b['lon_max']:.4f} lon")
    
    if "hotspots" in patterns and patterns["hotspots"]:
        top = patterns["hotspots"][0]
        summary.append(f"Top hotspot: ({top['lat']:.4f}, {top['lon']:.4f}) with {top['count']:,} records ({top['percent']:.1f}%)")
    
    if "locations" in patterns and location_cols:
        for col in location_cols[:1]:  # Just include first location column
            if col in patterns["locations"]:
                loc_data = patterns["locations"][col]
                top_loc = list(loc_data["top_10"].items())[0] if loc_data["top_10"] else None
                if top_loc:
                    summary.append(f"Top {col}: {top_loc[0]} with {top_loc[1]:,} records")
    
    return "\n".join(summary)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python analyze.py <csv_path> <lat_column> <lon_column> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    lat_column = sys.argv[2]
    lon_column = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "analysis_results"
    
    analyze_geographic_patterns(csv_path, lat_column, lon_column, output_dir)
