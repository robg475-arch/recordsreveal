#!/usr/bin/env python3
"""
RecordsReveal Profile Dataset Skill
Profiles CSV and recommends which analysis skills to run
"""

import sys
import os
import json
from pathlib import Path
import pandas as pd
import numpy as np

def profile_dataset(csv_path, output_dir="analysis_results"):
    """
    Profile a CSV dataset and recommend analyses
    """
    print("\n" + "="*70)
    print("📊 RECORDSREVEAL DATASET PROFILER")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Output: {output_dir}")
    print("="*70 + "\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load dataset
    print(f"📂 Loading dataset...")
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns\n")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None
    
    # Build profile
    profile = {
        "dataset": str(csv_path),
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": {},
        "patterns": {},
        "summary_stats": {}
    }
    
    print("="*70)
    print("🔍 PROFILING COLUMNS")
    print("="*70)
    
    # Detect column types and patterns
    temporal_cols = []
    geographic_cols = []
    categorical_cols = []
    numeric_cols = []
    
    for col in df.columns:
        col_profile = {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing_count": int(df[col].isnull().sum()),
            "missing_percent": float(df[col].isnull().sum() / len(df) * 100),
            "unique_values": int(df[col].nunique())
        }
        
        # Detect temporal columns
        if any(kw in col.lower() for kw in ['date', 'time', 'year', 'month', 'day', 'hour', 'minute', 'timestamp']):
            temporal_cols.append(col)
            col_profile["pattern"] = "temporal"
            print(f"   📅 {col} (temporal)")
        
        # Detect geographic columns
        elif any(kw in col.lower() for kw in ['lat', 'lon', 'latitude', 'longitude', 'address', 'city', 'state', 'zip', 'postal', 'location', 'borough', 'county']):
            geographic_cols.append(col)
            col_profile["pattern"] = "geographic"
            print(f"   🗺️  {col} (geographic)")
        
        # Detect numeric columns
        elif df[col].dtype in ['int64', 'float64']:
            numeric_cols.append(col)
            col_profile["pattern"] = "numeric"
            col_profile["stats"] = {
                "min": float(df[col].min()) if not df[col].empty else None,
                "max": float(df[col].max()) if not df[col].empty else None,
                "mean": float(df[col].mean()) if not df[col].empty else None,
                "median": float(df[col].median()) if not df[col].empty else None
            }
            print(f"   🔢 {col} (numeric: {col_profile['stats']['min']:.2f} - {col_profile['stats']['max']:.2f})")
        
        # Detect categorical columns (text with < 50 unique values)
        elif df[col].dtype == 'object' and df[col].nunique() < 50:
            categorical_cols.append(col)
            col_profile["pattern"] = "categorical"
            top_values = df[col].value_counts().head(3).to_dict()
            col_profile["top_values"] = {str(k): int(v) for k, v in top_values.items()}
            print(f"   📂 {col} (categorical: {df[col].nunique()} values)")
        
        else:
            col_profile["pattern"] = "text"
            print(f"   📝 {col} (text)")
        
        profile["columns"][col] = col_profile
    
    # Store detected patterns
    profile["patterns"] = {
        "temporal": temporal_cols,
        "geographic": geographic_cols,
        "categorical": categorical_cols,
        "numeric": numeric_cols
    }
    
    # Generate recommendations
    print("\n" + "="*70)
    print("💡 ANALYSIS RECOMMENDATIONS")
    print("="*70 + "\n")
    
    recommendations = {
        "dataset": str(csv_path),
        "profiled_at": pd.Timestamp.now().isoformat(),
        "recommended_skills": []
    }
    
    # Recommend temporal-analysis
    if temporal_cols:
        rec = {
            "skill": "temporal-analysis",
            "priority": "high",
            "reason": f"Found {len(temporal_cols)} temporal column(s): {', '.join(temporal_cols)}",
            "command": f"python temporal-analysis/analyze.py {csv_path} {temporal_cols[0]}",
            "estimated_time": "30 seconds",
            "cost": "$0.00 (Ollama)",
            "insights_provided": ["hourly patterns", "day of week patterns", "peak times", "temporal trends"]
        }
        recommendations["recommended_skills"].append(rec)
        print(f"✓ {rec['skill']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Command: {rec['command']}")
        print()
    
    # Recommend geographic-analysis
    if geographic_cols:
        lat_col = next((c for c in geographic_cols if 'lat' in c.lower()), None)
        lon_col = next((c for c in geographic_cols if 'lon' in c.lower()), None)
        
        if lat_col and lon_col:
            rec = {
                "skill": "geographic-analysis",
                "priority": "high",
                "reason": f"Found coordinate columns: {lat_col}, {lon_col}",
                "command": f"python geographic-analysis/analyze.py {csv_path} {lat_col} {lon_col}",
                "estimated_time": "45 seconds",
                "cost": "$0.00 (Ollama)",
                "insights_provided": ["geographic hotspots", "location clustering", "spatial patterns"]
            }
        else:
            rec = {
                "skill": "geographic-analysis",
                "priority": "medium",
                "reason": f"Found geographic column(s): {', '.join(geographic_cols)}",
                "command": f"python geographic-analysis/analyze.py {csv_path} {geographic_cols[0]}",
                "estimated_time": "45 seconds",
                "cost": "$0.00 (Ollama)",
                "insights_provided": ["location breakdowns", "geographic patterns"]
            }
        recommendations["recommended_skills"].append(rec)
        print(f"✓ {rec['skill']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Command: {rec['command']}")
        print()
    
    # Recommend classification-analysis (if we have categorical target)
    if categorical_cols and len(df) > 100:
        # Pick the categorical column with most unique values as likely target
        target_col = max(categorical_cols, key=lambda c: df[c].nunique())
        rec = {
            "skill": "classification-analysis",
            "priority": "medium",
            "reason": f"Found potential classification target: {target_col} ({df[target_col].nunique()} classes)",
            "command": f"python classification-analysis/analyze.py {csv_path} \"{target_col}\"",
            "estimated_time": "90 seconds",
            "cost": "$0.00 (Ollama)",
            "insights_provided": ["ML predictions", "feature importance", "accuracy metrics"]
        }
        recommendations["recommended_skills"].append(rec)
        print(f"✓ {rec['skill']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Command: {rec['command']}")
        print()
    
    # Recommend clustering-analysis (if enough data)
    if len(df) >= 100 and len(numeric_cols) >= 2:
        rec = {
            "skill": "clustering-analysis",
            "priority": "medium",
            "reason": f"Dataset has {len(df):,} rows with {len(numeric_cols)} numeric features - good for pattern discovery",
            "command": f"python clustering-analysis/analyze.py {csv_path}",
            "estimated_time": "60 seconds",
            "cost": "$0.00 (Ollama)",
            "insights_provided": ["hidden patterns", "record groupings", "cluster profiles"]
        }
        recommendations["recommended_skills"].append(rec)
        print(f"✓ {rec['skill']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Command: {rec['command']}")
        print()
    
    # Recommend categorical-analysis
    if categorical_cols:
        rec = {
            "skill": "categorical-analysis",
            "priority": "low",
            "reason": f"Found {len(categorical_cols)} categorical column(s) for breakdown analysis",
            "command": f"python categorical-analysis/analyze.py {csv_path} {categorical_cols[0]}",
            "estimated_time": "20 seconds",
            "cost": "$0.00 (Ollama)",
            "insights_provided": ["category distributions", "top categories", "breakdowns"]
        }
        recommendations["recommended_skills"].append(rec)
        print(f"✓ {rec['skill']}")
        print(f"  Reason: {rec['reason']}")
        print(f"  Command: {rec['command']}")
        print()
    
    # Save outputs
    profile_path = os.path.join(output_dir, "profile.json")
    recommendations_path = os.path.join(output_dir, "recommendations.json")
    
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2, default=str)
    
    with open(recommendations_path, 'w') as f:
        json.dump(recommendations, f, indent=2, default=str)
    
    print("="*70)
    print("✅ PROFILING COMPLETE")
    print("="*70)
    print(f"\nOutputs:")
    print(f"  • {profile_path}")
    print(f"  • {recommendations_path}")
    print(f"\nRecommended: Run {len(recommendations['recommended_skills'])} analysis skills")
    print(f"Total estimated time: ~{sum_estimated_time(recommendations)} seconds")
    print(f"Total cost: $0.00 (all use Ollama)\n")
    
    return profile, recommendations

def sum_estimated_time(recommendations):
    """Sum up estimated times from recommendations"""
    total = 0
    for rec in recommendations["recommended_skills"]:
        time_str = rec["estimated_time"]
        try:
            total += int(time_str.split()[0])
        except:
            pass
    return total

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python profile.py <csv_path> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_results"
    
    profile_dataset(csv_path, output_dir)
