#!/usr/bin/env python3
"""
Extract Page Numbers Script
Converts combined_insights.json into flat dict of template variables
Implements Phase 5 from INVESTIGATION_PLAYBOOK.md
"""

import sys
import os
import json
from pathlib import Path
import urllib.request
import urllib.parse
import time

def reverse_geocode(lat, lon):
    """
    Look up location name from coordinates using Nominatim (OpenStreetMap)
    Free, no API key required, but rate-limited to 1 request/second
    """
    try:
        # Nominatim requires a User-Agent
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14"
        req = urllib.request.Request(url, headers={'User-Agent': 'RecordsReveal/1.0'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            # Extract relevant location info
            address = data.get('address', {})
            
            # Try to build a readable location name
            # Priority: neighborhood > city > county > state
            location_parts = []
            
            if 'neighbourhood' in address:
                location_parts.append(address['neighbourhood'])
            elif 'suburb' in address:
                location_parts.append(address['suburb'])
            elif 'hamlet' in address:
                location_parts.append(address['hamlet'])
            
            if 'city' in address:
                location_parts.append(address['city'])
            elif 'town' in address:
                location_parts.append(address['town'])
            elif 'village' in address:
                location_parts.append(address['village'])
            
            if not location_parts and 'county' in address:
                location_parts.append(address['county'])
            
            if location_parts:
                return ', '.join(location_parts[:2])  # Max 2 parts for brevity
            
            # Fallback to display_name if nothing specific found
            display_name = data.get('display_name', '')
            if display_name:
                parts = display_name.split(',')
                return ', '.join(parts[:2]).strip()
            
            return None
    
    except Exception as e:
        print(f"   ⚠️  Geocoding failed: {e}")
        return None


def extract_page_numbers(combined_insights_path, output_path="page_data.json"):
    """
    Extracts all numbers needed for every visual element on the page.
    Returns a flat dict of named values ready for template injection.
    """
    print("\n" + "="*70)
    print("🔢 EXTRACTING PAGE NUMBERS FOR VISUALIZATION")
    print("="*70)
    print(f"Input: {combined_insights_path}")
    print(f"Output: {output_path}")
    print("="*70 + "\n")
    
    # Load combined insights
    with open(combined_insights_path) as f:
        combined = json.load(f)
    
    temporal = combined.get('all_patterns', {}).get('temporal', {})
    geographic = combined.get('all_patterns', {}).get('geographic', {})
    categorical = combined.get('all_patterns', {}).get('categorical', {})
    classification = combined.get('all_patterns', {}).get('classification', {})
    clustering = combined.get('all_patterns', {}).get('clustering', {})
    comparative_financial = combined.get('all_patterns', {}).get('comparative_financial', {})
    
    insights = combined.get('all_ollama_insights', {})
    
    page_data = {
        "dataset": combined.get("dataset", "Unknown"),
        "analyses_run": combined.get("analyses", []),
        "chart_data": {},
        "stats": {},
        "insights": insights
    }
    
    print("📊 Extracting chart data...")
    
    # ===================================================================
    # CHART 1: Hourly Pattern (Line Chart)
    # ===================================================================
    if 'hourly' in temporal:
        hourly = temporal['hourly']
        distribution = hourly.get('distribution', {})
        
        # Sort by hour
        hours = sorted([int(h) for h in distribution.keys()])
        counts = [distribution[str(h)] for h in hours]
        
        page_data["chart_data"]["hourly_pattern"] = {
            "x": hours,
            "y": counts,
            "peak_hour": hourly.get('peak_hour'),
            "peak_count": hourly.get('peak_count'),
            "data_quality_warning": hourly.get('data_quality_warning')
        }
        
        # Format peak hour as AM/PM
        peak_hour_raw = hourly.get('peak_hour', 0)
        if peak_hour_raw == 0:
            peak_hour_formatted = "12AM"
        elif peak_hour_raw < 12:
            peak_hour_formatted = f"{peak_hour_raw}AM"
        elif peak_hour_raw == 12:
            peak_hour_formatted = "12PM"
        else:
            peak_hour_formatted = f"{peak_hour_raw - 12}PM"
        
        page_data["stats"]["peak_hour"] = peak_hour_formatted
        page_data["stats"]["peak_hour_count"] = f"{hourly.get('peak_count', 0):,}"
        page_data["stats"]["peak_hour_warning"] = hourly.get('data_quality_warning')
        
        if hourly.get('data_quality_warning'):
            print(f"   ⚠️  Data quality warning detected for hourly pattern")
        print(f"   ✓ Hourly pattern: {len(hours)} data points")
    
    # ===================================================================
    # DAY OF WEEK Pattern (Bar Chart)
    # ===================================================================
    if 'day_of_week' in temporal:
        dow = temporal['day_of_week']
        distribution = dow.get('distribution', {})
        
        # Order by weekday - Sunday through Saturday
        day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        days = [d for d in day_order if d in distribution]
        counts = [distribution[d] for d in days]
        
        page_data["chart_data"]["day_of_week"] = {
            "x": days,
            "y": counts,
            "peak_day": dow.get('peak_day'),
            "peak_count": dow.get('peak_count')
        }
        
        print(f"   ✓ Day of week: {len(days)} data points")
    
    # ===================================================================
    # CHART 2: Rankings (Horizontal Bar)
    # ===================================================================
    if 'locations' in geographic:
        locations = geographic['locations']
        
        # Find the first location type (BOROUGH, CITY, etc.)
        location_type = list(locations.keys())[0] if locations else None
        
        if location_type:
            loc_data = locations[location_type]
            top_10 = loc_data.get('top_10', {})
            
            # Sort by count descending
            sorted_items = sorted(top_10.items(), key=lambda x: x[1], reverse=True)
            names = [item[0] for item in sorted_items]
            counts = [item[1] for item in sorted_items]
            
            page_data["chart_data"]["rankings"] = {
                "names": names,
                "counts": counts,
                "type": location_type,
                "top_name": names[0] if names else "Unknown",
                "top_count": counts[0] if counts else 0
            }
            
            page_data["stats"]["top_location"] = names[0] if names else "Unknown"
            page_data["stats"]["top_location_count"] = f"{counts[0]:,}" if counts else "0"
            
            print(f"   ✓ Rankings: {len(names)} locations")
    
    # ===================================================================
    # CHART 3: Distribution (Donut/Pie) - Categorical breakdown
    # ===================================================================
    if 'distribution' in categorical:
        dist = categorical['distribution']
        
        page_data["chart_data"]["distribution"] = {
            "labels": dist.get('labels', []),
            "counts": dist.get('counts', []),
            "percentages": dist.get('percentages', []),
            "majority_label": dist.get('majority_label'),
            "majority_pct": dist.get('majority_pct')
        }
        
        page_data["stats"]["majority_category"] = dist.get('majority_label', 'Unknown')
        page_data["stats"]["majority_pct"] = f"{dist.get('majority_pct', 0)}%"
        
        print(f"   ✓ Distribution: {len(dist.get('labels', []))} categories")
    
    # ===================================================================
    # CHART 4: Trend Over Time (Line with Fill) - moved to position 4
    # ===================================================================
    if 'trend_over_time' in temporal:
        trend = temporal['trend_over_time']
        
        page_data["chart_data"]["trend"] = {
            "x": trend.get('x', []),
            "y": trend.get('y', []),
            "granularity": trend.get('granularity', 'yearly'),
            "peak_period": trend.get('peak_period'),
            "peak_count": trend.get('peak_count'),
            "pct_change": trend.get('pct_change'),
            "direction": trend.get('direction')
        }
        
        page_data["stats"]["trend_pct_change"] = f"{abs(trend.get('pct_change', 0))}%"
        page_data["stats"]["trend_direction"] = trend.get('direction', 'stable')
        
        print(f"   ✓ Trend: {len(trend.get('x', []))} time periods")
    
    # ===================================================================
    # CHART 5: Feature Importance (will be available with classification)
    # ===================================================================
    if 'feature_importance' in classification:
        features = classification['feature_importance']
        
        feat_names = [f['feature'] for f in features]
        feat_importance = [f['importance'] for f in features]
        
        page_data["chart_data"]["feature_importance"] = {
            "names": feat_names,
            "importance": feat_importance,
            "top_feature": feat_names[0] if feat_names else "Unknown",
            "top_importance": feat_importance[0] if feat_importance else 0
        }
        
        print(f"   ✓ Feature importance: {len(feat_names)} features")
    
    # ===================================================================
    # CHART 6 & 7: Model Comparison (will be available with classification)
    # ===================================================================
    if 'models' in classification:
        models = classification['models']
        
        model_names = list(models.keys())
        
        # Try both r2 (regression) and accuracy (classification)
        model_r2s = [v.get('r2', 0) for v in models.values()]
        model_accuracies = [v.get('accuracy', 0) for v in models.values()]
        
        # Use whichever metric is available
        if any(r2 != 0 for r2 in model_r2s):
            primary_metric = model_r2s
            metric_name = 'r2'
        else:
            primary_metric = model_accuracies
            metric_name = 'accuracy'
        
        page_data["chart_data"]["models"] = {
            "names": model_names,
            "r2_scores": model_r2s,
            "accuracies": model_accuracies,
            "best_model": classification.get('best_model', 'Unknown')
        }
        
        page_data["stats"]["best_model"] = classification.get('best_model', 'Unknown')
        best_score = max(primary_metric) if primary_metric else 0
        page_data["stats"]["best_score"] = f"{best_score*100:.1f}%"
        
        print(f"   ✓ Model comparison: {len(model_names)} models ({metric_name})")
    
    # ===================================================================
    # CHART 8 & 9: Clustering (will be available with clustering skill)
    # ===================================================================
    if 'pca' in clustering:
        pca = clustering['pca']
        
        page_data["chart_data"]["clusters"] = {
            "pca_x": pca.get('x', []),
            "pca_y": pca.get('y', []),
            "labels": pca.get('labels', []),
            "variance_1": pca.get('variance_1'),
            "variance_2": pca.get('variance_2'),
            "cluster_names": clustering.get('cluster_names', []),
            "cluster_profiles": clustering.get('cluster_profiles', []),
            "optimal_k": clustering.get('optimal_k', 2),
            "cluster_sizes": clustering.get('cluster_sizes', [])
        }
        
        print(f"   ✓ PCA clusters: {len(pca.get('x', []))} points")
    
    if 'elbow' in clustering:
        elbow = clustering['elbow']
        
        page_data["chart_data"]["elbow"] = {
            "k_values": elbow.get('k_values', []),
            "inertias": elbow.get('inertias', []),
            "optimal_k": clustering.get('optimal_k')
        }
        
        print(f"   ✓ Elbow curve: {len(elbow.get('k_values', []))} k values")
    
    # ===================================================================
    # GENERAL STATS
    # ===================================================================
    print("\n📈 Extracting statistics...")
    
    # Total records (try multiple sources)
    if 'hourly' in temporal:
        page_data["stats"]["total_records"] = f"{temporal['hourly'].get('total_records', 0):,}"
        print(f"   ✓ Total records: {page_data['stats']['total_records']}")
    elif comparative_financial and 'count' in comparative_financial.get('patterns', {}).get('top_entities', {}):
        count = comparative_financial['patterns']['top_entities']['count']
        page_data["stats"]["total_records"] = f"{count:,}"
        print(f"   ✓ Total records: {page_data['stats']['total_records']}")
    elif clustering and 'original_shape' in clustering:
        count = clustering['original_shape'][0]
        page_data["stats"]["total_records"] = f"{count:,}"
        print(f"   ✓ Total records: {page_data['stats']['total_records']}")
    
    # Valid coordinates
    if 'valid_coordinates' in geographic:
        valid = geographic['valid_coordinates']
        page_data["stats"]["valid_coordinates"] = f"{valid.get('count', 0):,}"
        page_data["stats"]["valid_coords_pct"] = f"{valid.get('percent', 0):.1f}%"
        print(f"   ✓ Valid coordinates: {page_data['stats']['valid_coordinates']}")
    
    # Geographic bounds
    if 'bounds' in geographic:
        bounds = geographic['bounds']
        page_data["stats"]["center_lat"] = f"{bounds.get('center_lat', 0):.4f}"
        page_data["stats"]["center_lon"] = f"{bounds.get('center_lon', 0):.4f}"
    
    # Hotspots
    if 'hotspots' in geographic and geographic['hotspots']:
        top_hotspot = geographic['hotspots'][0]
        page_data["stats"]["top_hotspot_count"] = f"{top_hotspot.get('count', 0):,}"
        page_data["stats"]["top_hotspot_pct"] = f"{top_hotspot.get('percent', 0):.1f}%"
        
        # Get coordinates
        lat = top_hotspot.get('lat', 0)
        lon = top_hotspot.get('lon', 0)
        
        # Try to get location name via reverse geocoding
        print(f"\n🗺️  Looking up location for coordinates ({lat:.4f}, {lon:.4f})...")
        location_name = reverse_geocode(lat, lon)
        
        if location_name:
            page_data["stats"]["top_location"] = location_name
            print(f"   ✓ Found: {location_name}")
            time.sleep(1)  # Respect rate limit (1 req/sec for Nominatim)
        else:
            # Fallback to coordinates if lookup fails
            page_data["stats"]["top_location"] = f"{abs(lat):.2f}°{'N' if lat >= 0 else 'S'}, {abs(lon):.2f}°{'E' if lon >= 0 else 'W'}"
            print(f"   ⚠️  Using coordinates as fallback")
    else:
        page_data["stats"]["top_location"] = None  # Will be skipped in hero KPIs
    
    # Day of week
    if 'day_of_week' in temporal:
        dow = temporal['day_of_week']
        page_data["stats"]["busiest_day"] = dow.get('busiest_day', 'Unknown')
        page_data["stats"]["busiest_day_count"] = f"{dow.get('busiest_count', 0):,}"
    
    # Financial stats (ENHANCED!)
    if comparative_financial:
        financial = comparative_financial
        
        # Basic stats
        if 'top_entities' in financial:
            top_ent = financial['top_entities']
            page_data["stats"]["total_financial"] = f"${top_ent.get('total', 0):,.0f}"
            page_data["stats"]["average_financial"] = f"${top_ent.get('average', 0):,.0f}"
            
            if top_ent.get('top_10'):
                top = top_ent['top_10'][0]
                page_data["stats"]["top_entity"] = top.get('entity', 'N/A')
                page_data["stats"]["top_entity_amount"] = f"${top.get('amount', 0):,.0f}"
                print(f"   ✓ Top entity: {page_data['stats']['top_entity']} ({page_data['stats']['top_entity_amount']})")
        
        # Comparative advantage
        if 'comparative_advantage' in financial:
            comp_adv = financial['comparative_advantage']
            page_data["stats"]["comparative_leader"] = comp_adv.get('leader', 'N/A')
            page_data["stats"]["comparative_advantage"] = f"${abs(comp_adv.get('net_advantage', 0)):,.0f}"
            print(f"   ✓ Comparative advantage: {page_data['stats']['comparative_advantage']} ({page_data['stats']['comparative_leader']})")
        
        # Attack vs Support
        if 'attack_vs_support' in financial:
            avs = financial['attack_vs_support']
            page_data["stats"]["pct_attack"] = f"{avs.get('pct_attack', 0):.1f}%"
            page_data["stats"]["pct_support"] = f"{avs.get('pct_support', 0):.1f}%"
            page_data["stats"]["attack_insight"] = avs.get('insight', '')
            print(f"   ✓ Attack ads: {page_data['stats']['pct_attack']} of spending")
        
        # Top spenders
        if 'top_spenders' in financial and financial['top_spenders'].get('dominant_spender'):
            dominant = financial['top_spenders']['dominant_spender']
            page_data["stats"]["dominant_spender"] = dominant.get('name', 'N/A')
            page_data["stats"]["dominant_spender_amount"] = f"${dominant.get('total', 0):,.0f}"
            page_data["stats"]["dominant_spender_districts"] = dominant.get('districts', 0)
            print(f"   ✓ Dominant spender: {page_data['stats']['dominant_spender']} ({page_data['stats']['dominant_spender_amount']})")
        
        # Concentration
        if 'concentration' in financial:
            conc = financial['concentration']
            if 'top_10' in conc:
                page_data["stats"]["top_10_pct"] = f"{conc['top_10'].get('pct', 0):.1f}%"
                print(f"   ✓ Top 10 concentration: {page_data['stats']['top_10_pct']}")
        
        # State leader
        if 'state_analysis' in financial and financial['state_analysis'].get('highest_total'):
            top_state = financial['state_analysis']['highest_total']
            page_data["stats"]["top_state"] = top_state.get('state', 'N/A')
            page_data["stats"]["top_state_amount"] = f"${top_state.get('total', 0):,.0f}"
            page_data["stats"]["top_state_districts"] = top_state.get('districts', 0)
            print(f"   ✓ Top state: {page_data['stats']['top_state']} ({page_data['stats']['top_state_amount']})")
        
        # Micro-targeting
        if 'transaction_patterns' in financial and financial['transaction_patterns'].get('micro_targeting'):
            mt = financial['transaction_patterns']['micro_targeting'][0]
            page_data["stats"]["micro_target_entity"] = mt.get('entity', 'N/A')
            page_data["stats"]["micro_target_transactions"] = mt.get('transactions', 0)
            print(f"   ✓ Micro-targeting: {page_data['stats']['micro_target_entity']} ({page_data['stats']['micro_target_transactions']} transactions)")
        
        # Outliers
        if 'outliers' in financial and len(financial['outliers']) > 0:
            page_data["stats"]["outlier_count"] = len(financial['outliers'])
            page_data["stats"]["top_outlier"] = financial['outliers'][0].get('insight', 'N/A')
            print(f"   ✓ Outliers detected: {page_data['stats']['outlier_count']}")
    
    # ===================================================================
    # PULL QUOTES
    # ===================================================================
    print("\n💬 Extracting pull quotes...")
    
    # Extract pull quotes from Ollama insights
    pull_quotes = []
    
    for analysis_type, insight_text in insights.items():
        # Look for text in quotes or compelling statements
        if isinstance(insight_text, str) and len(insight_text) > 20:
            # Try to extract a sentence that works as a pull quote
            lines = insight_text.split('\n')
            for line in lines:
                if 'quote' in line.lower() and '"' in line:
                    # Extract quoted text
                    start = line.find('"')
                    end = line.rfind('"')
                    if start != -1 and end != -1 and end > start:
                        quote = line[start+1:end]
                        if 10 <= len(quote.split()) <= 25:  # Good quote length
                            pull_quotes.append({
                                "text": quote,
                                "source": analysis_type
                            })
    
    page_data["pull_quotes"] = pull_quotes[:3]  # Limit to 3 quotes
    print(f"   ✓ Extracted {len(pull_quotes)} pull quotes")
    
    # ===================================================================
    # SAVE OUTPUT
    # ===================================================================
    with open(output_path, 'w') as f:
        json.dump(page_data, f, indent=2, default=str)
    
    print("\n" + "="*70)
    print("✅ PAGE NUMBERS EXTRACTION COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Charts available: {len([k for k in page_data['chart_data'].keys()])}")
    print(f"Stats extracted: {len(page_data['stats'])}")
    print(f"Pull quotes: {len(page_data['pull_quotes'])}")
    print()
    
    return page_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_page_numbers.py <combined_insights.json> [output.json]")
        sys.exit(1)
    
    combined_insights_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "page_data.json"
    
    extract_page_numbers(combined_insights_path, output_path)
