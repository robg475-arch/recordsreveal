#!/usr/bin/env python3
"""
Export chart data as JSON for inline JavaScript rendering
Matches RecordsReveal's manual chart style exactly
"""

import pandas as pd
import json
from pathlib import Path


def export_hourly_pattern(df, time_col, target_col):
    """Export hourly pattern data"""
    # Extract hour
    if df[time_col].dtype == 'object':
        df[time_col] = pd.to_datetime(df[time_col], format='%H:%M', errors='coerce').dt.hour
    
    hourly = df.groupby(df[time_col]).agg({
        target_col: ['sum', 'count']
    }).reset_index()
    hourly.columns = ['hour', 'total', 'count']
    
    # Fill missing hours
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly = all_hours.merge(hourly, on='hour', how='left').fillna(0)
    
    # Find peaks
    peak_hour = int(hourly.loc[hourly['total'].idxmax(), 'hour'])
    sorted_h = hourly.nlargest(2, 'total')
    second_hour = int(sorted_h.iloc[1]['hour']) if len(sorted_h) > 1 else None
    
    return {
        'type': 'hourly',
        'hours': [int(h) for h in hourly['hour']],
        'totals': [int(t) for t in hourly['total']],
        'counts': [int(c) for c in hourly['count']],
        'peak_hour': peak_hour,
        'second_hour': second_hour
    }


def export_day_of_week(df, date_col, target_col):
    """Export day of week data"""
    if df[date_col].dtype == 'object':
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    df['day_of_week'] = df[date_col].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    daily = df.groupby('day_of_week')[target_col].agg(['sum', 'count']).reset_index()
    daily['day_of_week'] = pd.Categorical(daily['day_of_week'], categories=day_order, ordered=True)
    daily = daily.sort_values('day_of_week')
    
    # Find peaks
    peak_day = daily.loc[daily['sum'].idxmax(), 'day_of_week']
    sorted_d = daily.nlargest(2, 'sum')
    second_day = sorted_d.iloc[1]['day_of_week'] if len(sorted_d) > 1 else None
    
    day_abbr = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 'Thursday': 'Thu',
                'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'}
    
    return {
        'type': 'day_of_week',
        'days': [day_abbr[d] for d in daily['day_of_week']],
        'totals': [int(t) for t in daily['sum']],
        'peak_day': day_abbr[peak_day],
        'second_day': day_abbr[second_day] if second_day else None
    }


def export_geographic(df, geo_col, target_col, top_n=5):
    """Export geographic breakdown"""
    breakdown = df.groupby(geo_col)[target_col].agg(['sum', 'count']).reset_index()
    breakdown = breakdown.sort_values('sum', ascending=False).head(top_n)
    breakdown = breakdown.sort_values('sum', ascending=True)  # Reverse for horizontal
    
    peak_loc = breakdown.iloc[-1][geo_col]
    second_loc = breakdown.iloc[-2][geo_col] if len(breakdown) > 1 else None
    
    return {
        'type': 'geographic',
        'locations': breakdown[geo_col].tolist(),
        'totals': [int(t) for t in breakdown['sum']],
        'peak_location': peak_loc,
        'second_location': second_loc
    }


def export_category_breakdown(df, cat_col, target_col, top_n=10):
    """Export category breakdown"""
    breakdown = df.groupby(cat_col)[target_col].agg(['sum', 'count']).reset_index()
    breakdown = breakdown.sort_values('sum', ascending=False).head(top_n)
    breakdown = breakdown.sort_values('sum', ascending=True)  # Reverse for horizontal
    
    peak_cat = breakdown.iloc[-1][cat_col]
    second_cat = breakdown.iloc[-2][cat_col] if len(breakdown) > 1 else None
    
    return {
        'type': 'category',
        'categories': breakdown[cat_col].tolist(),
        'totals': [int(t) for t in breakdown['sum']],
        'peak_category': peak_cat,
        'second_category': second_cat
    }


def export_all_chart_data(csv_path, target_col, output_path):
    """Export all chart data for a dataset"""
    df = pd.read_csv(csv_path)
    
    charts = {}
    
    # Detect temporal columns
    time_cols = [c for c in df.columns if 'time' in c.lower() and 'date' not in c.lower()]
    date_cols = [c for c in df.columns if 'date' in c.lower() and 'time' not in c.lower()]
    geo_cols = [c for c in df.columns if any(g in c.lower() for g in ['borough', 'city', 'state', 'region', 'county'])]
    cat_cols = [c for c in df.select_dtypes(include=['object']).columns 
                if df[c].nunique() < 50 and c not in time_cols and c not in date_cols and c not in geo_cols]
    
    # Export hourly pattern
    if time_cols:
        charts['hourly_pattern'] = export_hourly_pattern(df.copy(), time_cols[0], target_col)
    
    # Export day of week
    if date_cols:
        charts['day_of_week'] = export_day_of_week(df.copy(), date_cols[0], target_col)
    
    # Export geographic
    if geo_cols:
        charts['geographic'] = export_geographic(df, geo_cols[0], target_col)
    
    # Export categories
    for i, cat_col in enumerate(cat_cols[:2]):
        charts[f'category_{i+1}'] = export_category_breakdown(df, cat_col, target_col)
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(charts, f, indent=2)
    
    print(f"✅ Exported {len(charts)} chart data files to {output_path}")
    return charts


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 export_chart_data.py <csv_file> <target_column>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    target_col = sys.argv[2]
    output_path = Path(csv_path).parent / 'analysis_results' / 'chart_data.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    export_all_chart_data(csv_path, target_col, output_path)
