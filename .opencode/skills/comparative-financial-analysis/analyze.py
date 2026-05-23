#!/usr/bin/env python3
"""
RecordsReveal Comparative Financial Analysis Skill
Analyzes financial data with A vs B comparisons (spending, donations, budgets)
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

def detect_financial_columns(df):
    """Detect columns containing financial data"""
    financial_keywords = ['spend', 'cost', 'price', 'revenue', 'budget', 'donation', 
                         'contribution', 'support', 'oppose', 'money', 'dollar', 
                         'amount', 'total', 'payment', 'fee', 'salary']
    
    financial_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in financial_keywords):
            if pd.api.types.is_numeric_dtype(df[col]):
                financial_cols.append(col)
    
    return financial_cols

def detect_comparative_pattern(df):
    """Detect A vs B comparative patterns (dem/rep, before/after, etc.)"""
    comparative_patterns = {
        'political': {
            'keywords': ['dem', 'rep', 'democrat', 'republican', 'liberal', 'conservative'],
            'sides': []
        },
        'temporal': {
            'keywords': ['before', 'after', 'pre', 'post', 'old', 'new'],
            'sides': []
        },
        'binary': {
            'keywords': ['yes', 'no', 'for', 'against', 'support', 'oppose'],
            'sides': []
        }
    }
    
    for col in df.columns:
        col_lower = col.lower()
        for pattern_type, pattern_info in comparative_patterns.items():
            for keyword in pattern_info['keywords']:
                if keyword in col_lower:
                    pattern_info['sides'].append(col)
                    break
    
    # Find the pattern with the most matches
    best_pattern = max(comparative_patterns.items(), 
                      key=lambda x: len(x[1]['sides']))
    
    if len(best_pattern[1]['sides']) >= 2:
        return best_pattern[0], best_pattern[1]['sides']
    
    return None, []

def analyze_comparative_financial(csv_path, output_dir="analysis_results"):
    """
    Analyze financial data with comparative patterns
    """
    print("\n" + "="*70)
    print("💰 RECORDSREVEAL COMPARATIVE FINANCIAL ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
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
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns\n")
    
    results = {
        "analysis_type": "comparative_financial",
        "dataset": str(csv_path),
        "patterns": {}
    }
    
    # Detect financial columns
    print("="*70)
    print("💵 DETECTING FINANCIAL COLUMNS")
    print("="*70 + "\n")
    
    financial_cols = detect_financial_columns(df)
    print(f"Found {len(financial_cols)} financial column(s):")
    for col in financial_cols:
        print(f"  • {col}")
    print()
    
    if not financial_cols:
        print("❌ No financial columns detected")
        return None
    
    # Detect comparative pattern
    print("="*70)
    print("⚖️  DETECTING COMPARATIVE PATTERNS")
    print("="*70 + "\n")
    
    pattern_type, pattern_cols = detect_comparative_pattern(df)
    
    if pattern_type:
        print(f"✅ Detected {pattern_type} comparison pattern")
        print(f"   Columns: {', '.join(pattern_cols)}\n")
        results["patterns"]["comparison_type"] = pattern_type
        results["patterns"]["comparison_columns"] = pattern_cols
    else:
        print("⚠️  No clear comparative pattern detected\n")
    
    # Analyze top entities by total financial amount
    print("="*70)
    print("🏆 TOP ENTITIES BY FINANCIAL TOTALS")
    print("="*70 + "\n")
    
    # Find the main financial total column
    total_cols = [c for c in financial_cols if 'total' in c.lower()]
    main_financial_col = total_cols[0] if total_cols else financial_cols[0]
    
    # Get entity column (first text column that's not financial)
    entity_col = None
    for col in df.columns:
        if df[col].dtype == 'object' and col not in financial_cols:
            entity_col = col
            break
    
    if entity_col and main_financial_col:
        top_n = min(10, len(df))
        top_entities = df.nlargest(top_n, main_financial_col)
        
        print(f"Top {top_n} by {main_financial_col}:\n")
        
        top_list = []
        for i, (idx, row) in enumerate(top_entities.iterrows(), 1):
            entity = row[entity_col]
            amount = row[main_financial_col]
            print(f"   {i}. {entity}: ${amount:,.2f}")
            top_list.append({
                "rank": i,
                "entity": str(entity),
                "amount": float(amount)
            })
        
        print()
        
        results["patterns"]["top_entities"] = {
            "column": main_financial_col,
            "entity_column": entity_col,
            "top_10": top_list,
            "total": float(df[main_financial_col].sum()),
            "average": float(df[main_financial_col].mean()),
            "median": float(df[main_financial_col].median())
        }
    
    # Analyze comparative financial advantage (if pattern detected)
    if pattern_type == 'political' and pattern_cols:
        print("="*70)
        print("⚖️  COMPARATIVE ADVANTAGE ANALYSIS")
        print("="*70 + "\n")
        
        # Find dem vs rep columns
        dem_cols = [c for c in financial_cols if 'dem' in c.lower()]
        rep_cols = [c for c in financial_cols if 'rep' in c.lower()]
        
        if dem_cols and rep_cols:
            # Calculate net advantages
            dem_total = df[[c for c in dem_cols if 'support' in c.lower() or 'total' in c.lower()]].sum().sum()
            rep_total = df[[c for c in rep_cols if 'support' in c.lower() or 'total' in c.lower()]].sum().sum()
            
            print(f"Democratic total: ${dem_total:,.2f}")
            print(f"Republican total: ${rep_total:,.2f}")
            print(f"Net advantage: ${abs(dem_total - rep_total):,.2f} ({'DEM' if dem_total > rep_total else 'REP'})")
            print()
            
            # Find entities with biggest advantages
            if 'net_dem_advantage' in df.columns or 'advantage' in str(df.columns).lower():
                advantage_col = [c for c in df.columns if 'advantage' in c.lower()][0]
                
                print(f"Biggest advantages ({advantage_col}):\n")
                
                top_dem = df.nlargest(5, advantage_col)
                print("  Democratic advantages:")
                for i, (idx, row) in enumerate(top_dem.iterrows(), 1):
                    entity = row[entity_col] if entity_col else idx
                    adv = row[advantage_col]
                    print(f"    {i}. {entity}: +${adv:,.2f}")
                
                print()
                
                top_rep = df.nsmallest(5, advantage_col)
                print("  Republican advantages:")
                for i, (idx, row) in enumerate(top_rep.iterrows(), 1):
                    entity = row[entity_col] if entity_col else idx
                    adv = abs(row[advantage_col])
                    print(f"    {i}. {entity}: +${adv:,.2f}")
                
                print()
                
                results["patterns"]["comparative_advantage"] = {
                    "dem_total": float(dem_total),
                    "rep_total": float(rep_total),
                    "net_advantage": float(dem_total - rep_total),
                    "leader": "DEM" if dem_total > rep_total else "REP"
                }
    
    # Analyze spending distribution
    print("="*70)
    print("📊 SPENDING DISTRIBUTION")
    print("="*70 + "\n")
    
    for col in financial_cols[:3]:  # Top 3 financial columns
        total = df[col].sum()
        mean = df[col].mean()
        median = df[col].median()
        max_val = df[col].max()
        min_val = df[col].min()
        
        print(f"{col}:")
        print(f"  Total: ${total:,.2f}")
        print(f"  Average: ${mean:,.2f}")
        print(f"  Median: ${median:,.2f}")
        print(f"  Range: ${min_val:,.2f} - ${max_val:,.2f}")
        print()
        
        results["patterns"][f"distribution_{col}"] = {
            "total": float(total),
            "mean": float(mean),
            "median": float(median),
            "min": float(min_val),
            "max": float(max_val)
        }
    
    # Generate Ollama insights
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING AI INSIGHTS (OLLAMA)")
        print("="*70 + "\n")
        
        # Prepare context for Ollama
        context = f"""Dataset: {csv_path}
Analysis type: Comparative Financial Analysis

Key findings:
1. Total entities analyzed: {len(df):,}
2. Main financial metric: {main_financial_col}
3. Total amount: ${results['patterns']['top_entities']['total']:,.2f}
4. Top entity: {results['patterns']['top_entities']['top_10'][0]['entity']} (${results['patterns']['top_entities']['top_10'][0]['amount']:,.2f})
"""
        
        if pattern_type == 'political' and 'comparative_advantage' in results['patterns']:
            context += f"""5. Democratic total: ${results['patterns']['comparative_advantage']['dem_total']:,.2f}
6. Republican total: ${results['patterns']['comparative_advantage']['rep_total']:,.2f}
7. Net advantage: ${abs(results['patterns']['comparative_advantage']['net_advantage']):,.2f} ({results['patterns']['comparative_advantage']['leader']})
"""
        
        context += "\nTop 5 entities:\n"
        for item in results['patterns']['top_entities']['top_10'][:5]:
            context += f"  {item['rank']}. {item['entity']}: ${item['amount']:,.2f}\n"
        
        prompt = f"""{context}

Based on this financial data analysis, write a compelling data journalism finding that answers:

1. What is the single most newsworthy financial pattern or disparity?
2. What does this mean for the entities involved?
3. Provide a memorable pull quote (one sentence) that captures the finding.

Format your response as:
**Finding:** [Your newsworthy finding]
**Implication:** [What this means]
**Pull Quote:** "[Your quote]"
"""
        
        print("Asking Ollama for financial insights...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama Financial Insights:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            
            results["ollama_insights"] = insights
    
    # Save results
    output_file = os.path.join(output_dir, "comparative_financial_insights.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ COMPARATIVE FINANCIAL ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_file}")
    print(f"Financial columns: {len(financial_cols)}")
    print(f"Pattern type: {pattern_type or 'none'}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <csv_file> [output_dir]")
        print("\nExample:")
        print("  python analyze.py campaign_finance.csv pipeline_output")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_results"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: File not found: {csv_path}")
        sys.exit(1)
    
    analyze_comparative_financial(csv_path, output_dir)

if __name__ == "__main__":
    main()
