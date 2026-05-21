#!/usr/bin/env python3
"""
RecordsReveal Temporal Analysis Skill
Analyzes time-based patterns with Ollama insights
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

def analyze_temporal_patterns(csv_path, time_column, output_dir="analysis_results"):
    """
    Analyze temporal patterns in the dataset
    """
    print("\n" + "="*70)
    print("📅 RECORDSREVEAL TEMPORAL ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Time column: {time_column}")
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
    
    # Check if time column exists
    if time_column not in df.columns:
        print(f"❌ Error: Column '{time_column}' not found in dataset")
        print(f"Available columns: {', '.join(df.columns)}")
        return None
    
    results = {
        "analysis_type": "temporal",
        "dataset": str(csv_path),
        "time_column": time_column,
        "patterns": {}
    }
    
    print("="*70)
    print("🔍 ANALYZING TIME PATTERNS")
    print("="*70 + "\n")
    
    # Parse the time column
    try:
        df[time_column] = pd.to_datetime(df[time_column])
        print(f"✓ Parsed {time_column} as datetime")
    except Exception as e:
        print(f"⚠️  Could not parse as datetime: {e}")
        print("Treating as categorical time values...\n")
    
    # Extract time components
    if pd.api.types.is_datetime64_any_dtype(df[time_column]):
        df['_hour'] = df[time_column].dt.hour
        df['_day_of_week'] = df[time_column].dt.day_name()
        df['_month'] = df[time_column].dt.month_name()
        df['_year'] = df[time_column].dt.year
        
        # Hourly pattern
        print("⏰ Analyzing hourly patterns...")
        hourly = df['_hour'].value_counts().sort_index()
        peak_hour = hourly.idxmax()
        peak_count = hourly.max()
        
        # Data quality check: detect if most records are at one hour
        total_records = len(df)
        peak_percentage = (peak_count / total_records * 100) if total_records > 0 else 0
        data_quality_warning = None
        
        if peak_percentage > 80:
            data_quality_warning = f"WARNING: {peak_percentage:.1f}% of records are at hour {peak_hour}:00. This likely indicates missing time data rather than a real pattern."
            print(f"   ⚠️  {data_quality_warning}")
        
        # Ensure all 24 hours are represented (fill missing hours with 0)
        hourly_full = pd.Series({h: 0 for h in range(24)})
        hourly_full.update(hourly)
        hourly_full = hourly_full.sort_index()
        
        results["patterns"]["hourly"] = {
            "distribution": hourly_full.to_dict(),
            "peak_hour": int(peak_hour),
            "peak_count": int(peak_count),
            "peak_percentage": round(peak_percentage, 1),
            "total_records": int(hourly_full.sum()),
            "data_quality_warning": data_quality_warning
        }
        
        print(f"   Peak hour: {peak_hour}:00 ({peak_count:,} records, {peak_percentage:.1f}%)")
        print(f"   Total records: {hourly.sum():,}\n")
        
        # Day of week pattern
        print("📆 Analyzing day-of-week patterns...")
        dow = df['_day_of_week'].value_counts()
        busiest_day = dow.idxmax()
        busiest_count = dow.max()
        
        results["patterns"]["day_of_week"] = {
            "distribution": dow.to_dict(),
            "busiest_day": busiest_day,
            "busiest_count": int(busiest_count)
        }
        
        print(f"   Busiest day: {busiest_day} ({busiest_count:,} records)")
        print(f"   Distribution: {dow.to_dict()}\n")
        
        # Monthly pattern
        print("📊 Analyzing monthly patterns...")
        monthly = df['_month'].value_counts()
        busiest_month = monthly.idxmax()
        
        results["patterns"]["monthly"] = {
            "distribution": monthly.to_dict(),
            "busiest_month": busiest_month,
            "busiest_count": int(monthly.max())
        }
        
        print(f"   Busiest month: {busiest_month} ({monthly.max():,} records)\n")
        
        # Trend over time (yearly/monthly)
        print("📈 Analyzing trend over time...")
        
        # Check if we have enough date range for meaningful trend
        date_range = (df[time_column].max() - df[time_column].min()).days
        
        if date_range > 365:  # More than 1 year - use yearly trend
            yearly = df.groupby('_year').size().sort_index()
            trend_x = yearly.index.tolist()
            trend_y = yearly.values.tolist()
            peak_period = yearly.idxmax()
            peak_count = yearly.max()
            
            # Calculate percent change
            if len(yearly) >= 2:
                pct_change = ((yearly.iloc[-1] - yearly.iloc[0]) / yearly.iloc[0] * 100)
            else:
                pct_change = 0
            
            results["patterns"]["trend_over_time"] = {
                "granularity": "yearly",
                "x": [int(x) for x in trend_x],
                "y": [int(y) for y in trend_y],
                "peak_period": int(peak_period),
                "peak_count": int(peak_count),
                "pct_change": float(round(pct_change, 1)),
                "direction": "increase" if pct_change > 0 else "decrease"
            }
            
            print(f"   Trend: {len(trend_x)} years ({trend_x[0]}-{trend_x[-1]})")
            print(f"   Peak year: {peak_period} ({peak_count:,} records)")
            print(f"   Overall change: {abs(pct_change):.1f}% {results['patterns']['trend_over_time']['direction']}\n")
            
        elif date_range > 60:  # More than 2 months - use monthly trend
            df['_year_month'] = df[time_column].dt.to_period('M')
            monthly_trend = df.groupby('_year_month').size().sort_index()
            trend_x = [str(x) for x in monthly_trend.index]
            trend_y = monthly_trend.values.tolist()
            peak_period = str(monthly_trend.idxmax())
            peak_count = monthly_trend.max()
            
            # Calculate percent change
            if len(monthly_trend) >= 2:
                pct_change = ((monthly_trend.iloc[-1] - monthly_trend.iloc[0]) / monthly_trend.iloc[0] * 100)
            else:
                pct_change = 0
            
            results["patterns"]["trend_over_time"] = {
                "granularity": "monthly",
                "x": trend_x,
                "y": [int(y) for y in trend_y],
                "peak_period": peak_period,
                "peak_count": int(peak_count),
                "pct_change": float(round(pct_change, 1)),
                "direction": "increase" if pct_change > 0 else "decrease"
            }
            
            print(f"   Trend: {len(trend_x)} months")
            print(f"   Peak month: {peak_period} ({peak_count:,} records)")
            print(f"   Overall change: {abs(pct_change):.1f}% {results['patterns']['trend_over_time']['direction']}\n")
        else:
            print(f"   ⚠️  Date range too short ({date_range} days) for trend analysis\n")
        
    else:
        # Treat as categorical time values
        print("📊 Analyzing time value distribution...")
        time_dist = df[time_column].value_counts().head(10)
        
        results["patterns"]["time_distribution"] = {
            "top_10": time_dist.to_dict(),
            "unique_values": int(df[time_column].nunique())
        }
        
        print(f"   Unique time values: {df[time_column].nunique()}")
        print(f"   Top 10 values:\n{time_dist}\n")
    
    # Ask Ollama for insights
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING AI INSIGHTS (OLLAMA)")
        print("="*70 + "\n")
        
        # Prepare summary for Ollama
        summary = format_temporal_summary(results)
        
        prompt = f"""You are a data journalist analyzing temporal patterns in a dataset.

Here's what I found:
{summary}

Please provide:
1. The most newsworthy time-based finding (1-2 sentences)
2. What this pattern suggests about behavior or events (1-2 sentences)
3. A compelling pull quote for an article (10-15 words, quotable)

Keep it journalistic and engaging."""
        
        print("Asking Ollama for temporal insights...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama Temporal Insights:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            results["ollama_insights"] = insights
        else:
            print("⚠️  Could not get Ollama insights\n")
    
    # Save results
    output_path = os.path.join(output_dir, "temporal_insights.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ TEMPORAL ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def format_temporal_summary(results):
    """Format temporal results for Ollama"""
    summary = []
    
    patterns = results.get("patterns", {})
    
    if "hourly" in patterns:
        h = patterns["hourly"]
        summary.append(f"Peak hour: {h['peak_hour']}:00 with {h['peak_count']} records")
    
    if "day_of_week" in patterns:
        dow = patterns["day_of_week"]
        summary.append(f"Busiest day: {dow['busiest_day']} with {dow['busiest_count']} records")
        summary.append(f"Day distribution: {dow['distribution']}")
    
    if "monthly" in patterns:
        m = patterns["monthly"]
        summary.append(f"Busiest month: {m['busiest_month']} with {m['busiest_count']} records")
    
    return "\n".join(summary)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze.py <csv_path> <time_column> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    time_column = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "analysis_results"
    
    analyze_temporal_patterns(csv_path, time_column, output_dir)
