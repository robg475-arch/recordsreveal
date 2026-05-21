#!/usr/bin/env python3
"""
RecordsReveal Categorical Analysis Skill
Analyzes categorical distributions with Ollama insights
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

def analyze_categorical_patterns(csv_path, category_column, output_dir="analysis_results"):
    """
    Analyze categorical column distributions
    """
    print("\n" + "="*70)
    print("📊 RECORDSREVEAL CATEGORICAL ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Category column: {category_column}")
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
    
    # Check if category column exists
    if category_column not in df.columns:
        print(f"❌ Error: Column '{category_column}' not found in dataset")
        print(f"Available columns: {', '.join(df.columns)}")
        return None
    
    results = {
        "analysis_type": "categorical",
        "dataset": str(csv_path),
        "category_column": category_column,
        "patterns": {}
    }
    
    print("="*70)
    print("🔍 ANALYZING CATEGORY DISTRIBUTION")
    print("="*70 + "\n")
    
    # Get value counts
    value_counts = df[category_column].value_counts()
    total_records = len(df)
    
    # Get top categories (limit to top 15 for visualization)
    top_n = min(15, len(value_counts))
    top_categories = value_counts.head(top_n)
    
    # Calculate percentages
    percentages = (top_categories / total_records * 100).round(1)
    
    # Identify majority category
    majority_label = top_categories.idxmax()
    majority_count = top_categories.max()
    majority_pct = percentages.iloc[0]
    
    print(f"📈 Found {len(value_counts)} unique categories")
    print(f"   Total records: {total_records:,}")
    print(f"   Showing top {top_n}\n")
    
    print(f"🏆 Majority category: {majority_label}")
    print(f"   Count: {majority_count:,} ({majority_pct}%)\n")
    
    print("Top categories:")
    for i, (label, count) in enumerate(top_categories.head(10).items(), 1):
        pct = percentages.iloc[i-1]
        print(f"   {i}. {label}: {count:,} ({pct}%)")
    print()
    
    # Store distribution
    results["patterns"]["distribution"] = {
        "labels": top_categories.index.tolist(),
        "counts": top_categories.values.tolist(),
        "percentages": percentages.values.tolist(),
        "total_unique": int(len(value_counts)),
        "total_records": int(total_records),
        "majority_label": str(majority_label),
        "majority_count": int(majority_count),
        "majority_pct": float(majority_pct)
    }
    
    # Check for imbalance
    if majority_pct > 50:
        imbalance_ratio = majority_count / top_categories.iloc[1] if len(top_categories) > 1 else 1
        results["patterns"]["imbalance"] = {
            "detected": True,
            "ratio": float(round(imbalance_ratio, 2)),
            "message": f"{majority_label} dominates with {majority_pct}%"
        }
        print(f"⚠️  Class imbalance detected!")
        print(f"   {majority_label} is {imbalance_ratio:.1f}x more common than 2nd place\n")
    
    # Ask Ollama for insights
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING AI INSIGHTS (OLLAMA)")
        print("="*70 + "\n")
        
        # Prepare summary for Ollama
        summary = format_categorical_summary(results)
        
        prompt = f"""You are a data journalist analyzing categorical data distributions.

Here's what I found:
{summary}

Please provide:
1. The most newsworthy finding about this distribution (1-2 sentences)
2. What this distribution pattern suggests about the data (1-2 sentences)
3. A compelling pull quote for an article (10-15 words, quotable)

Keep it journalistic and engaging."""
        
        print("Asking Ollama for categorical insights...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama Categorical Insights:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            results["ollama_insights"] = insights
        else:
            print("⚠️  Could not get Ollama insights\n")
    
    # Save results
    output_path = os.path.join(output_dir, "categorical_insights.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ CATEGORICAL ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def format_categorical_summary(results):
    """Format categorical results for Ollama"""
    summary = []
    
    patterns = results.get("patterns", {})
    dist = patterns.get("distribution", {})
    
    summary.append(f"Category: {results.get('category_column')}")
    summary.append(f"Total unique values: {dist.get('total_unique', 0)}")
    summary.append(f"Total records: {dist.get('total_records', 0):,}")
    summary.append(f"Majority category: {dist.get('majority_label')} ({dist.get('majority_pct')}%)")
    
    # Top 5 categories
    labels = dist.get('labels', [])
    counts = dist.get('counts', [])
    percentages = dist.get('percentages', [])
    
    if labels and counts:
        summary.append("\nTop 5 categories:")
        for i in range(min(5, len(labels))):
            summary.append(f"  {i+1}. {labels[i]}: {counts[i]:,} ({percentages[i]}%)")
    
    # Imbalance note
    if patterns.get('imbalance', {}).get('detected'):
        summary.append(f"\nImbalance: {patterns['imbalance']['message']}")
    
    return "\n".join(summary)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze.py <csv_path> <category_column> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    category_column = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "analysis_results"
    
    analyze_categorical_patterns(csv_path, category_column, output_dir)
