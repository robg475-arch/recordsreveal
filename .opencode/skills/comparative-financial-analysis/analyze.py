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
    
    # ===================================================================
    # DEEP ANALYSIS 1: ATTACK VS SUPPORT SPENDING
    # ===================================================================
    print("="*70)
    print("🎯 ATTACK VS SUPPORT ANALYSIS")
    print("="*70 + "\n")
    
    # Look for spending_for and spending_against columns
    if 'spending_for' in df.columns and 'spending_against' in df.columns:
        total_for = df['spending_for'].sum()
        total_against = df['spending_against'].sum()
        total_both = total_for + total_against
        pct_attack = (total_against / total_both * 100) if total_both > 0 else 0
        pct_support = (total_for / total_both * 100) if total_both > 0 else 0
        
        print(f"Spending FOR candidates:     ${total_for:>15,.0f} ({pct_support:.1f}%)")
        print(f"Spending AGAINST candidates: ${total_against:>15,.0f} ({pct_attack:.1f}%)")
        print(f"\nKey insight: {pct_attack:.1f}% of spending goes to ATTACK ads\n")
        
        results["patterns"]["attack_vs_support"] = {
            "spending_for": float(total_for),
            "spending_against": float(total_against),
            "pct_attack": float(pct_attack),
            "pct_support": float(pct_support),
            "insight": f"{pct_attack:.1f}% of dark money funds attack ads, not candidate support"
        }
    
    # ===================================================================
    # DEEP ANALYSIS 2: TOP SPENDERS ACROSS ALL DISTRICTS
    # ===================================================================
    print("="*70)
    print("💰 TOP SPENDERS (CROSS-DISTRICT ANALYSIS)")
    print("="*70 + "\n")
    
    # Parse top_spenders column if it exists
    if 'top_spenders' in df.columns:
        all_spenders = {}
        spender_districts = {}
        
        for spenders_str in df['top_spenders'].dropna():
            for entry in spenders_str.split(' | '):
                if ': $' in entry:
                    name, amount_str = entry.split(': $')
                    amount = float(amount_str.replace(',', ''))
                    all_spenders[name] = all_spenders.get(name, 0) + amount
                    if name not in spender_districts:
                        spender_districts[name] = 0
                    spender_districts[name] += 1
        
        top_spenders_sorted = sorted(all_spenders.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("Top 10 spenders across ALL districts:\n")
        spender_list = []
        for i, (name, total) in enumerate(top_spenders_sorted, 1):
            districts = spender_districts.get(name, 0)
            avg_per_district = total / districts if districts > 0 else 0
            print(f"{i:2}. {name:35} ${total:>15,.0f} | {districts:3} districts | ${avg_per_district:>10,.0f}/dist")
            spender_list.append({
                "rank": i,
                "name": name,
                "total": float(total),
                "districts": districts,
                "avg_per_district": float(avg_per_district)
            })
        
        print()
        
        # Identify dominant spender
        if top_spenders_sorted:
            top_name, top_amount = top_spenders_sorted[0]
            total_all_spenders = sum(amt for _, amt in top_spenders_sorted)
            dominance_pct = (top_amount / total_all_spenders * 100) if total_all_spenders > 0 else 0
            print(f"Dominant spender: {top_name} controls {dominance_pct:.1f}% of top 10 spending\n")
        
        results["patterns"]["top_spenders"] = {
            "spender_list": spender_list,
            "dominant_spender": spender_list[0] if spender_list else None,
            "insight": f"{spender_list[0]['name']} spent ${spender_list[0]['total']:,.0f} across {spender_list[0]['districts']} districts" if spender_list else None
        }
    
    # ===================================================================
    # DEEP ANALYSIS 3: CONCENTRATION ANALYSIS (POWER LAW)
    # ===================================================================
    print("="*70)
    print("📈 CONCENTRATION ANALYSIS (Top N Effect)")
    print("="*70 + "\n")
    
    if main_financial_col:
        # Calculate what % of total spending goes to top N districts
        total_spending = df[main_financial_col].sum()
        
        concentrations = {}
        for n in [5, 10, 20]:
            top_n_total = df.nlargest(n, main_financial_col)[main_financial_col].sum()
            pct = (top_n_total / total_spending * 100) if total_spending > 0 else 0
            concentrations[f"top_{n}"] = {
                "total": float(top_n_total),
                "pct": float(pct)
            }
            print(f"Top {n:2} districts: ${top_n_total:>15,.0f} ({pct:5.1f}% of total)")
        
        print()
        
        results["patterns"]["concentration"] = {
            **concentrations,
            "insight": f"Top 10 districts capture {concentrations['top_10']['pct']:.1f}% of all spending"
        }
    
    # ===================================================================
    # DEEP ANALYSIS 4: STATE-LEVEL PATTERNS
    # ===================================================================
    print("="*70)
    print("🗺️  STATE-LEVEL SPENDING PATTERNS")
    print("="*70 + "\n")
    
    if 'state' in df.columns and main_financial_col:
        state_totals = df.groupby('state')[main_financial_col].sum().sort_values(ascending=False)
        state_counts = df.groupby('state').size()
        state_avgs = (state_totals / state_counts).sort_values(ascending=False)
        
        print("Top 10 states by total spending:\n")
        state_analysis = []
        for i, (state, total) in enumerate(state_totals.head(10).items(), 1):
            count = state_counts[state]
            avg = total / count
            print(f"{i:2}. {state:3} ${total:>15,.0f} | {count:2} districts | ${avg:>12,.0f} avg/district")
            state_analysis.append({
                "rank": i,
                "state": state,
                "total": float(total),
                "districts": int(count),
                "avg_per_district": float(avg)
            })
        
        print()
        
        results["patterns"]["state_analysis"] = {
            "state_rankings": state_analysis,
            "highest_total": state_analysis[0] if state_analysis else None,
            "highest_avg": {
                "state": state_avgs.index[0],
                "avg": float(state_avgs.iloc[0])
            } if len(state_avgs) > 0 else None,
            "insight": f"{state_analysis[0]['state']} leads with ${state_analysis[0]['total']:,.0f} across {state_analysis[0]['districts']} districts" if state_analysis else None
        }
    
    # ===================================================================
    # DEEP ANALYSIS 5: TRANSACTION PATTERNS (MICRO-TARGETING)
    # ===================================================================
    print("="*70)
    print("🎯 TRANSACTION PATTERNS (Micro-Targeting Detection)")
    print("="*70 + "\n")
    
    if 'num_transactions' in df.columns and main_financial_col:
        # Calculate cost per transaction
        df_temp = df.copy()
        df_temp['cost_per_transaction'] = df_temp[main_financial_col] / df_temp['num_transactions']
        
        # Most transactions (micro-targeting)
        most_trans = df_temp.nlargest(5, 'num_transactions')[[entity_col, 'num_transactions', main_financial_col, 'cost_per_transaction']]
        
        print("Districts with MOST transactions (micro-targeting):\n")
        micro_targeting = []
        for i, (idx, row) in enumerate(most_trans.iterrows(), 1):
            entity = row[entity_col] if entity_col else idx
            trans = row['num_transactions']
            total = row[main_financial_col]
            avg = row['cost_per_transaction']
            print(f"  {i}. {entity:10} {trans:4} transactions | ${total:>12,.0f} total | ${avg:>10,.0f} avg")
            micro_targeting.append({
                "rank": i,
                "entity": str(entity),
                "transactions": int(trans),
                "total": float(total),
                "avg_per_transaction": float(avg)
            })
        
        print("\nDistricts with FEWEST transactions (big-ticket spending):\n")
        least_trans = df_temp[df_temp['num_transactions'] > 0].nsmallest(5, 'num_transactions')[[entity_col, 'num_transactions', main_financial_col, 'cost_per_transaction']]
        big_ticket = []
        for i, (idx, row) in enumerate(least_trans.iterrows(), 1):
            entity = row[entity_col] if entity_col else idx
            trans = row['num_transactions']
            total = row[main_financial_col]
            avg = row['cost_per_transaction']
            print(f"  {i}. {entity:10} {trans:4} transactions | ${total:>12,.0f} total | ${avg:>10,.0f} avg")
            big_ticket.append({
                "rank": i,
                "entity": str(entity),
                "transactions": int(trans),
                "total": float(total),
                "avg_per_transaction": float(avg)
            })
        
        print()
        
        results["patterns"]["transaction_patterns"] = {
            "micro_targeting": micro_targeting,
            "big_ticket": big_ticket,
            "insight": f"{micro_targeting[0]['entity']} had {micro_targeting[0]['transactions']} transactions (surgical micro-targeting)" if micro_targeting else None
        }
    
    # ===================================================================
    # DEEP ANALYSIS 6: OUTLIER DETECTION
    # ===================================================================
    print("="*70)
    print("🚨 OUTLIER DETECTION (Anomalies Worth Investigating)")
    print("="*70 + "\n")
    
    outliers = []
    
    # Outlier 1: Republican advantages in overwhelmingly Democratic field
    if 'net_dem_advantage' in df.columns and entity_col:
        rep_advantages = df[df['net_dem_advantage'] < 0].nsmallest(3, 'net_dem_advantage')
        if len(rep_advantages) > 0:
            print("Republican spending advantages (unusual in this dataset):\n")
            for i, (idx, row) in enumerate(rep_advantages.iterrows(), 1):
                entity = row[entity_col] if entity_col else idx
                adv = abs(row['net_dem_advantage'])
                print(f"  {i}. {entity}: REP +${adv:,.0f}")
                outliers.append({
                    "type": "rep_advantage_anomaly",
                    "entity": str(entity),
                    "amount": float(adv),
                    "insight": f"{entity} shows unusual REP advantage of ${adv:,.0f}"
                })
            print()
    
    # Outlier 2: Extreme cost-per-transaction
    if 'num_transactions' in df.columns and main_financial_col:
        df_temp = df.copy()
        df_temp['cost_per_transaction'] = df_temp[main_financial_col] / df_temp['num_transactions']
        extreme_cost = df_temp.nlargest(3, 'cost_per_transaction')[[entity_col, 'cost_per_transaction', 'num_transactions']]
        if len(extreme_cost) > 0:
            print("Extreme cost-per-transaction (possible single large buys):\n")
            for i, (idx, row) in enumerate(extreme_cost.iterrows(), 1):
                entity = row[entity_col] if entity_col else idx
                cost = row['cost_per_transaction']
                trans = row['num_transactions']
                print(f"  {i}. {entity}: ${cost:,.0f}/transaction ({trans} total)")
                outliers.append({
                    "type": "extreme_cost_per_transaction",
                    "entity": str(entity),
                    "cost_per_transaction": float(cost),
                    "transactions": int(trans),
                    "insight": f"{entity} averaged ${cost:,.0f} per transaction (only {trans} buys)"
                })
            print()
    
    results["patterns"]["outliers"] = outliers
    
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
        
        # Prepare comprehensive context for Ollama
        context = f"""Dataset: {csv_path}
Analysis type: Comparative Financial Analysis

OVERALL METRICS:
- Total entities: {len(df):,}
- Total spending: ${results['patterns']['top_entities']['total']:,.2f}
- Top entity: {results['patterns']['top_entities']['top_10'][0]['entity']} (${results['patterns']['top_entities']['top_10'][0]['amount']:,.2f})
"""
        
        if pattern_type == 'political' and 'comparative_advantage' in results['patterns']:
            context += f"""
POLITICAL ADVANTAGE:
- Democratic total: ${results['patterns']['comparative_advantage']['dem_total']:,.2f}
- Republican total: ${results['patterns']['comparative_advantage']['rep_total']:,.2f}
- Net advantage: ${abs(results['patterns']['comparative_advantage']['net_advantage']):,.2f} ({results['patterns']['comparative_advantage']['leader']})
"""
        
        if 'attack_vs_support' in results['patterns']:
            avs = results['patterns']['attack_vs_support']
            context += f"""
ATTACK VS SUPPORT:
- Attack spending: ${avs['spending_against']:,.0f} ({avs['pct_attack']:.1f}%)
- Support spending: ${avs['spending_for']:,.0f} ({avs['pct_support']:.1f}%)
- Key: {avs['pct_attack']:.1f}% goes to ATTACK ads
"""
        
        if 'top_spenders' in results['patterns'] and results['patterns']['top_spenders'].get('dominant_spender'):
            dominant = results['patterns']['top_spenders']['dominant_spender']
            context += f"""
DOMINANT SPENDER:
- {dominant['name']}: ${dominant['total']:,.0f} across {dominant['districts']} districts
"""
        
        if 'concentration' in results['patterns']:
            conc = results['patterns']['concentration']
            context += f"""
CONCENTRATION:
- Top 10 districts: {conc['top_10']['pct']:.1f}% of all spending
- Top 20 districts: {conc['top_20']['pct']:.1f}% of all spending
"""
        
        if 'state_analysis' in results['patterns'] and results['patterns']['state_analysis'].get('highest_total'):
            top_state = results['patterns']['state_analysis']['highest_total']
            context += f"""
STATE LEADER:
- {top_state['state']}: ${top_state['total']:,.0f} across {top_state['districts']} districts
"""
        
        if 'transaction_patterns' in results['patterns']:
            tp = results['patterns']['transaction_patterns']
            if tp.get('micro_targeting'):
                mt = tp['micro_targeting'][0]
                context += f"""
MICRO-TARGETING:
- {mt['entity']}: {mt['transactions']} transactions (surgical spending)
"""
        
        if 'outliers' in results['patterns'] and len(results['patterns']['outliers']) > 0:
            context += f"\nOUTLIERS:\n"
            for outlier in results['patterns']['outliers'][:3]:
                context += f"- {outlier.get('insight', 'Anomaly detected')}\n"
        
        prompt = f"""{context}

Based on this comprehensive financial analysis with 8 dimensions of data, write a compelling investigative journalism finding.

Focus on the MOST NEWSWORTHY pattern from:
1. Attack vs Support ratio (65% attack?)
2. Dominant spender concentration  
3. Top N spending concentration
4. Geographic patterns
5. Micro-targeting evidence
6. Outliers/anomalies
7. Political advantage disparities
8. Spending efficiency

Your finding should:
- Lead with the most surprising/impactful number
- Explain what it means for voters/democracy
- Include a memorable pull quote
- Be specific and data-driven

Format:
**Finding:** [2-3 sentences with the key discovery]
**Implication:** [What this means - why it matters]
**Pull Quote:** "[One quotable sentence with a number]"
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
