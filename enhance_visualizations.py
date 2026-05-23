#!/usr/bin/env python3
"""
Domain-Specific Visualization Generator for RecordsReveal
==========================================================

Generates insight-driven visualizations based on dataset characteristics.

Detects and creates:
- Temporal patterns (hourly, daily, monthly trends)
- Geographic distributions (by region, state, borough)
- Category breakdowns (top N categories, distributions)
- Correlations between key metrics

This replaces generic ML charts with publication-quality data journalism visualizations.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


# RecordsReveal styling constants
RECORDSREVEAL_LAYOUT = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'family': 'Barlow, sans-serif', 'color': '#4a4a4a', 'size': 11},
    'margin': {'t': 10, 'b': 50, 'l': 60, 'r': 20},
    'xaxis': {
        'gridcolor': 'rgba(0,0,0,0.05)',
        'zerolinecolor': 'rgba(0,0,0,0.1)',
        'tickfont': {'size': 10}
    },
    'yaxis': {
        'gridcolor': 'rgba(0,0,0,0.05)',
        'zerolinecolor': 'rgba(0,0,0,0.1)',
        'tickfont': {'size': 10}
    },
    'showlegend': False
}

RECORDSREVEAL_CONFIG = {
    'responsive': True,
    'displayModeBar': False
}

RED = '#b5271f'
ORANGE = '#d2691e'
FADED = 'rgba(181,39,31,0.4)'
LABEL_COLOR = '#888'


def detect_temporal_columns(df):
    """Detect date and time columns"""
    temporal_cols = {'date': [], 'time': [], 'datetime': []}
    
    # Check datetime types
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    temporal_cols['datetime'].extend(datetime_cols)
    
    # Check string columns that might be dates/times
    for col in df.select_dtypes(include=['object']).columns:
        col_lower = col.lower()
        if 'date' in col_lower and 'time' not in col_lower:
            try:
                pd.to_datetime(df[col].dropna().head(100), errors='coerce')
                temporal_cols['date'].append(col)
            except:
                pass
        elif 'time' in col_lower and 'date' not in col_lower:
            temporal_cols['time'].append(col)
        elif 'datetime' in col_lower:
            try:
                pd.to_datetime(df[col].dropna().head(100), errors='coerce')
                temporal_cols['datetime'].append(col)
            except:
                pass
    
    return temporal_cols


def detect_geographic_columns(df):
    """Detect geographic/location columns"""
    geo_cols = []
    geo_patterns = ['borough', 'city', 'state', 'region', 'county', 'district', 'location', 'place']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in geo_patterns):
            if df[col].dtype == 'object' or df[col].dtype == 'category':
                geo_cols.append(col)
    
    return geo_cols


def detect_category_columns(df, max_unique=50):
    """Detect categorical columns with reasonable cardinality"""
    category_cols = []
    
    for col in df.select_dtypes(include=['object', 'category']).columns:
        unique_count = df[col].nunique()
        if 2 < unique_count <= max_unique:
            category_cols.append(col)
    
    return category_cols


def create_hourly_pattern_chart(df, time_col, target_col, theme_color='#d2691e'):
    """Create hourly pattern visualization matching RecordsReveal style"""
    # Extract hour from time column
    if df[time_col].dtype == 'object':
        try:
            df[time_col] = pd.to_datetime(df[time_col], format='%H:%M', errors='coerce').dt.hour
        except:
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce').dt.hour
    
    # Ensure we have all 24 hours represented
    hourly = df.groupby(df[time_col]).agg({
        target_col: ['sum', 'count']
    }).reset_index()
    hourly.columns = ['hour', 'total', 'count']
    
    # Fill missing hours with 0
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly = all_hours.merge(hourly, on='hour', how='left').fillna(0)
    
    # Find peak hour and second highest
    peak_hour = int(hourly.loc[hourly['total'].idxmax(), 'hour'])
    sorted_totals = hourly.nlargest(2, 'total')
    second_hour = int(sorted_totals.iloc[1]['hour']) if len(sorted_totals) > 1 else None
    
    # Generate color map for JavaScript
    color_js = []
    for h in hourly['hour']:
        h = int(h)
        if h == peak_hour:
            color_js.append(f"h==={h}?RED")
        elif h == second_hour:
            color_js.append(f"h==={h}?ORANGE")
        else:
            color_js.append(f"h==={h}?FADED")
    
    # Create chart data structure for embedding
    chart_data = {
        'hours': hourly['hour'].tolist(),
        'totals': hourly['total'].tolist(),
        'counts': hourly['count'].tolist(),
        'peak_hour': peak_hour,
        'second_hour': second_hour,
        'target_label': target_col.replace('NUMBER OF ', '').replace('PERSONS ', '').title()
    }
    
    return chart_data


def create_day_of_week_chart(df, date_col, target_col, theme_color='#d2691e'):
    """Create day of week pattern matching RecordsReveal style"""
    # Convert to datetime if needed
    if df[date_col].dtype == 'object':
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    df['day_of_week'] = df[date_col].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_abbr = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 'Thursday': 'Thu', 
                'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'}
    
    daily = df.groupby('day_of_week')[target_col].agg(['sum', 'count']).reset_index()
    daily['day_of_week'] = pd.Categorical(daily['day_of_week'], categories=day_order, ordered=True)
    daily = daily.sort_values('day_of_week')
    
    # Find peak and second highest
    sorted_daily = daily.nlargest(2, 'sum')
    peak_day = sorted_daily.iloc[0]['day_of_week']
    second_day = sorted_daily.iloc[1]['day_of_week'] if len(sorted_daily) > 1 else None
    
    # Color: RED for peak, ORANGE for second, faded for rest
    colors = []
    for day in daily['day_of_week']:
        if day == peak_day:
            colors.append(RED)
        elif day == second_day:
            colors.append(ORANGE)
        else:
            colors.append(FADED)
    
    # Use abbreviated day names
    daily['day_abbr'] = daily['day_of_week'].map(day_abbr)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily['day_abbr'],
        y=daily['sum'],
        marker=dict(color=colors)
    ))
    
    # Apply RecordsReveal styling
    fig.update_layout(**RECORDSREVEAL_LAYOUT)
    fig.update_layout(
        xaxis_title=None,
        width=1000,
        height=300,
        autosize=False
    )
    
    fig.update_yaxes(
        title=dict(text='Total ' + target_col.lower(), font=dict(size=10, color=LABEL_COLOR)),
        tickformat=',d'
    )
    
    return fig


def create_category_breakdown_chart(df, category_col, target_col, top_n=10, theme_color='#d2691e', orientation='h'):
    """Create category breakdown (top N) matching RecordsReveal style"""
    breakdown = df.groupby(category_col)[target_col].agg(['sum', 'count']).reset_index()
    breakdown = breakdown.sort_values('sum', ascending=False).head(top_n)
    
    if orientation == 'h':
        breakdown = breakdown.sort_values('sum', ascending=True)  # Reverse for horizontal
        
        # Highlight: top 2 from the END (since we reversed)
        colors = []
        for i in range(len(breakdown)):
            if i >= len(breakdown) - 1:  # Top 1
                colors.append(RED)
            elif i >= len(breakdown) - 2:  # Top 2
                colors.append(ORANGE)
            else:
                colors.append(FADED)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=breakdown['sum'],
            y=breakdown[category_col],
            orientation='h',
            marker=dict(color=colors)
        ))
        
        # Apply RecordsReveal styling
        fig.update_layout(**RECORDSREVEAL_LAYOUT)
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            height=max(320, top_n * 32),
            width=1000,
            autosize=False,
            margin=dict(t=10, b=40, l=160 if orientation == 'h' else 60, r=20)
        )
        
        fig.update_xaxes(
            title=dict(text='Total ' + target_col.lower(), font=dict(size=10, color=LABEL_COLOR)),
            tickformat=',d'
        )
        
    else:
        # Vertical bars
        colors = []
        sorted_breakdown = breakdown.sort_values('sum', ascending=False)
        top_cat = sorted_breakdown.iloc[0][category_col]
        second_cat = sorted_breakdown.iloc[1][category_col] if len(sorted_breakdown) > 1 else None
        
        for cat in breakdown[category_col]:
            if cat == top_cat:
                colors.append(RED)
            elif cat == second_cat:
                colors.append(ORANGE)
            else:
                colors.append(FADED)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=breakdown[category_col],
            y=breakdown['sum'],
            marker=dict(color=colors)
        ))
        
        # Apply RecordsReveal styling
        fig.update_layout(**RECORDSREVEAL_LAYOUT)
        fig.update_layout(
            xaxis_title=None,
            width=1000,
            height=380,
            autosize=False
        )
        
        fig.update_yaxes(
            title=dict(text='Total ' + target_col.lower(), font=dict(size=10, color=LABEL_COLOR)),
            tickformat=',d'
        )
    
    return fig


def create_target_distribution_chart(df, target_col, theme_color='#d2691e'):
    """Create target variable distribution matching RecordsReveal style"""
    fig = go.Figure()
    
    if df[target_col].nunique() < 50:  # Categorical or count variable
        value_counts = df[target_col].value_counts().sort_index()
        
        # Find peak value
        peak_val = value_counts.idxmax()
        colors = [RED if val == peak_val else FADED for val in value_counts.index]
        
        fig.add_trace(go.Bar(
            x=value_counts.index,
            y=value_counts.values,
            marker=dict(color=colors)
        ))
    else:  # Continuous variable
        fig.add_trace(go.Histogram(
            x=df[target_col],
            nbinsx=50,
            marker=dict(color=FADED)
        ))
    
    # Apply RecordsReveal styling
    fig.update_layout(**RECORDSREVEAL_LAYOUT)
    fig.update_layout(
        xaxis_title=None,
        width=1000,
        height=300,
        autosize=False
    )
    
    fig.update_yaxes(
        title=dict(text='Frequency', font=dict(size=10, color=LABEL_COLOR)),
        tickformat=',d'
    )
    
    return fig


def create_metric_comparison_chart(df, metrics, theme_color='#d2691e'):
    """Create comparison of multiple metrics matching RecordsReveal style"""
    totals = {metric: df[metric].sum() for metric in metrics}
    
    # Sort by value
    sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    # Color: RED for top, ORANGE for second, faded for rest
    colors = []
    for i, (metric, value) in enumerate(sorted_totals):
        if i == 0:
            colors.append(RED)
        elif i == 1:
            colors.append(ORANGE)
        else:
            colors.append(FADED)
    
    # Clean up metric names (remove "NUMBER OF" prefix)
    clean_labels = []
    for metric, _ in sorted_totals:
        label = metric.replace('NUMBER OF ', '').replace('INJURED', '').replace('KILLED', '').strip()
        label = label.title()
        clean_labels.append(label)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=clean_labels,
        y=[v for _, v in sorted_totals],
        marker=dict(color=colors)
    ))
    
    # Apply RecordsReveal styling
    fig.update_layout(**RECORDSREVEAL_LAYOUT)
    fig.update_layout(
        xaxis_title=None,
        width=1000,
        height=320,
        autosize=False
    )
    
    fig.update_yaxes(
        title=dict(text='Total injuries', font=dict(size=10, color=LABEL_COLOR)),
        tickformat=',d'
    )
    
    return fig


def generate_domain_visualizations(df, target_col, output_dir, theme_color='#d2691e'):
    """
    Main function: Detect patterns and generate relevant visualizations
    
    Returns dict of visualization HTML strings
    """
    print("\n" + "="*60)
    print("📊 GENERATING DOMAIN-SPECIFIC VISUALIZATIONS")
    print("="*60)
    
    viz_dir = Path(output_dir)
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    visualizations = {}
    
    # Detect column types
    temporal_cols = detect_temporal_columns(df)
    geo_cols = detect_geographic_columns(df)
    category_cols = detect_category_columns(df)
    
    print(f"\n🔍 Detected patterns:")
    print(f"   📅 Temporal columns: {len(temporal_cols['date']) + len(temporal_cols['time'])}")
    print(f"   🗺️  Geographic columns: {len(geo_cols)}")
    print(f"   📂 Category columns: {len(category_cols)}")
    
    # 1. Target distribution (always create)
    print(f"\n   📊 Creating target distribution chart...")
    fig = create_target_distribution_chart(df, target_col, theme_color)
    viz_path = viz_dir / "target_distribution.html"
    fig.write_html(str(viz_path), include_plotlyjs='cdn')
    visualizations['target_distribution'] = str(viz_path)
    
    # 2. Temporal patterns
    if temporal_cols['time']:
        time_col = temporal_cols['time'][0]
        print(f"   ⏰ Creating hourly pattern chart from '{time_col}'...")
        fig = create_hourly_pattern_chart(df.copy(), time_col, target_col, theme_color)
        viz_path = viz_dir / "hourly_pattern.html"
        fig.write_html(str(viz_path), include_plotlyjs='cdn')
        visualizations['hourly_pattern'] = str(viz_path)
    
    if temporal_cols['date']:
        date_col = temporal_cols['date'][0]
        print(f"   📅 Creating day-of-week chart from '{date_col}'...")
        fig = create_day_of_week_chart(df.copy(), date_col, target_col, theme_color)
        viz_path = viz_dir / "day_of_week.html"
        fig.write_html(str(viz_path), include_plotlyjs='cdn')
        visualizations['day_of_week'] = str(viz_path)
    
    # 3. Geographic breakdown
    if geo_cols:
        geo_col = geo_cols[0]
        print(f"   🗺️  Creating geographic breakdown from '{geo_col}'...")
        fig = create_category_breakdown_chart(df, geo_col, target_col, top_n=10, theme_color=theme_color, orientation='h')
        viz_path = viz_dir / "geographic_breakdown.html"
        fig.write_html(str(viz_path), include_plotlyjs='cdn')
        visualizations['geographic_breakdown'] = str(viz_path)
    
    # 4. Category breakdowns (top 2 most interesting)
    category_cols_filtered = [c for c in category_cols if c not in geo_cols and 'factor' in c.lower() or 'type' in c.lower() or 'category' in c.lower()]
    
    for i, cat_col in enumerate(category_cols_filtered[:2]):
        print(f"   📂 Creating category breakdown from '{cat_col}'...")
        orientation = 'h' if df[cat_col].nunique() > 6 else 'v'
        fig = create_category_breakdown_chart(df, cat_col, target_col, top_n=10, theme_color=theme_color, orientation=orientation)
        viz_path = viz_dir / f"category_breakdown_{i+1}.html"
        fig.write_html(str(viz_path), include_plotlyjs='cdn')
        visualizations[f'category_breakdown_{i+1}'] = str(viz_path)
    
    # 5. Metric comparison (if multiple injury/count columns)
    injury_cols = [col for col in df.columns if 'injured' in col.lower() or 'killed' in col.lower()]
    if len(injury_cols) >= 3:
        print(f"   📊 Creating metric comparison chart...")
        fig = create_metric_comparison_chart(df, injury_cols[:5], theme_color)
        viz_path = viz_dir / "metric_comparison.html"
        fig.write_html(str(viz_path), include_plotlyjs='cdn')
        visualizations['metric_comparison'] = str(viz_path)
    
    print(f"\n✅ Generated {len(visualizations)} domain-specific visualizations")
    print(f"   📁 Saved to: {viz_dir}")
    
    return visualizations


if __name__ == "__main__":
    print("This module provides domain-specific visualization generation.")
    print("Import and use generate_domain_visualizations() function.")
