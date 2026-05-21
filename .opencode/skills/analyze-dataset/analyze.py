#!/usr/bin/env python3
"""
RecordsReveal Analyze Dataset Skill
Orchestrates: EDA + ML + Clustering + AI Insights
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from analyze_v2 import EnhancedAnalyzer
from ollama_helper import (
    test_connection,
    ask_ollama_eda_insights,
    ask_ollama_cluster_names,
    ask_ollama_write
)

def analyze_dataset(csv_path, output_dir="analysis_results", use_ollama=True):
    """
    Main analysis pipeline
    """
    print("\n" + "="*70)
    print("🚀 RECORDSREVEAL DATASET ANALYSIS PIPELINE")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Output: {output_dir}")
    print(f"AI Insights: {'Ollama (FREE)' if use_ollama else 'None'}")
    print("="*70)
    
    # Test Ollama connection if enabled
    if use_ollama:
        print("\n📡 Testing Ollama connection...")
        if not test_connection():
            print("⚠️  Warning: Ollama not available. Continuing without AI insights.")
            use_ollama = False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load dataset
    print(f"\n📂 Loading dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
    
    # Run core analysis with analyze_v2.py
    print("\n" + "="*70)
    print("🔬 RUNNING CORE ANALYSIS (ML + Clustering)")
    print("="*70)
    
    analyzer = EnhancedAnalyzer(csv_path)
    try:
        analyzer.run()
    except Exception as e:
        print(f"⚠️  Analysis completed with some errors: {e}")
    results = analyzer.results
    
    # Save base results
    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✅ Saved base results: {results_path}")
    
    # Phase 2: EDA Insights with Ollama
    if use_ollama and 'profile' in results:
        print("\n" + "="*70)
        print("🤖 PHASE 2: AI-POWERED EDA INSIGHTS")
        print("="*70)
        
        # Prepare EDA summary for Ollama
        eda_summary = format_eda_for_ollama(results)
        if eda_summary.strip():
            print("\nAsking Ollama to identify surprising patterns...")
            print(f"Data summary:\n{eda_summary[:200]}...")
            
            insights = ask_ollama_eda_insights(eda_summary)
            if insights:
                print("\n📊 Ollama Insights:")
                print("-" * 70)
                print(insights)
                print("-" * 70)
                results['ollama_eda_insights'] = insights
            else:
                print("⚠️  Could not get Ollama insights")
        else:
            print("⚠️  No EDA summary available for Ollama")
    
    # Phase 3: ML Interpretation with Ollama
    if use_ollama and 'models' in results:
        print("\n" + "="*70)
        print("🤖 PHASE 3: AI-POWERED ML INTERPRETATION")
        print("="*70)
        
        ml_summary = format_ml_for_ollama(results)
        if ml_summary.strip():
            print("\nAsking Ollama to interpret ML results...")
            print(f"ML summary:\n{ml_summary[:200]}...")
            
            prompt = f"""You are a data journalist interpreting machine learning results.

Here's what the models found:
{ml_summary}

Please explain:
1. What do these predictions reveal about the data?
2. Which features matter most and why is that significant?
3. What story does this tell?

Keep it journalistic and concise (3-4 sentences)."""
            
            ml_insights = ask_ollama_write(prompt)
            if ml_insights:
                print("\n🎯 Ollama ML Insights:")
                print("-" * 70)
                print(ml_insights)
                print("-" * 70)
                results['ollama_ml_insights'] = ml_insights
        else:
            print("⚠️  No ML summary available for Ollama")
    
    # Phase 4: Cluster Naming with Ollama
    if use_ollama and 'clustering' in results:
        print("\n" + "="*70)
        print("🤖 PHASE 4: AI-POWERED CLUSTER NAMING")
        print("="*70)
        
        cluster_summary = format_clusters_for_ollama(results)
        if cluster_summary.strip():
            print("\nAsking Ollama to name clusters...")
            print(f"Cluster summary:\n{cluster_summary[:200]}...")
            
            cluster_names = ask_ollama_cluster_names(cluster_summary)
            if cluster_names:
                print("\n🧩 Ollama Cluster Names:")
                print("-" * 70)
                print(cluster_names)
                print("-" * 70)
                results['ollama_cluster_names'] = cluster_names
        else:
            print("⚠️  No cluster summary available for Ollama")
    
    # Save enhanced results with Ollama insights
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Phase 5: Generate domain-specific visualizations
    print("\n" + "="*70)
    print("📊 PHASE 5: DOMAIN-SPECIFIC VISUALIZATIONS")
    print("="*70)
    
    try:
        from enhance_visualizations import generate_domain_visualizations
        viz_results = generate_domain_visualizations(csv_path, output_dir)
        results['visualizations'] = viz_results
        print(f"✅ Generated {len(viz_results)} domain-specific visualizations")
    except Exception as e:
        print(f"⚠️  Could not generate domain visualizations: {e}")
    
    # Phase 6: Export chart data for inline rendering
    print("\n" + "="*70)
    print("📈 PHASE 6: EXPORT CHART DATA")
    print("="*70)
    
    try:
        from export_chart_data import export_all_chart_data
        chart_data_path = os.path.join(output_dir, "chart_data.json")
        export_all_chart_data(output_dir, chart_data_path)
        print(f"✅ Exported chart data: {chart_data_path}")
    except Exception as e:
        print(f"⚠️  Could not export chart data: {e}")
    
    # Print summary
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs:")
    print(f"  • {results_path}")
    print(f"  • {os.path.join(output_dir, 'chart_data.json')}")
    print(f"  • {output_dir}/*.html (visualizations)")
    
    if use_ollama:
        print(f"\n💰 Cost: $0.00 (Ollama)")
    
    return results

def format_eda_for_ollama(results):
    """Format EDA results for Ollama prompt"""
    summary = []
    
    # Add dataset profile
    if 'profile' in results:
        profile = results['profile']
        if 'shape' in profile:
            summary.append(f"Dataset: {profile['shape'][0]:,} rows × {profile['shape'][1]} columns")
        if 'numeric_cols' in profile:
            summary.append(f"Numeric columns: {len(profile['numeric_cols'])}")
        if 'categorical_cols' in profile:
            summary.append(f"Categorical columns: {len(profile['categorical_cols'])}")
    
    # Add EDA insights
    if 'eda' in results:
        eda = results['eda']
        if 'correlations' in eda:
            summary.append(f"Found {len(eda.get('correlations', {}))} correlations")
    
    # Add model info
    if 'models' in results and 'task_type' in results['models']:
        summary.append(f"Task type: {results['models']['task_type']}")
        if 'target_distribution' in results['models']:
            dist = results['models']['target_distribution']
            summary.append(f"Target has {len(dist)} unique values")
    
    return "\n".join(summary)

def format_ml_for_ollama(results):
    """Format ML results for Ollama prompt"""
    summary = []
    
    models = results.get('models', {})
    summary.append(f"Problem type: {models.get('task_type', 'Unknown')}")
    
    if 'best_model' in models:
        summary.append(f"Best model: {models['best_model']}")
    
    if 'model_scores' in models:
        scores = models['model_scores']
        for name, metrics in scores.items():
            if isinstance(metrics, dict) and 'accuracy' in metrics:
                summary.append(f"{name}: {metrics['accuracy']:.3f} accuracy")
    
    if 'feature_importance' in models:
        top_features = list(models['feature_importance'].items())[:5]
        summary.append(f"Top features: {[f'{k}={v:.3f}' for k,v in top_features]}")
    
    return "\n".join(summary)

def format_clusters_for_ollama(results):
    """Format cluster results for Ollama prompt"""
    summary = []
    
    clustering = results.get('clustering', {})
    if 'n_clusters' in clustering:
        summary.append(f"Found {clustering['n_clusters']} clusters")
    
    if 'cluster_sizes' in clustering:
        sizes = clustering['cluster_sizes']
        for i, size in enumerate(sizes):
            summary.append(f"Cluster {i}: {size} records ({size/sum(sizes)*100:.1f}%)")
    
    if 'silhouette_score' in clustering:
        summary.append(f"Silhouette score: {clustering['silhouette_score']:.3f}")
    
    return "\n".join(summary)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <csv_path> [output_dir] [--no-ollama]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "analysis_results"
    use_ollama = '--no-ollama' not in sys.argv
    
    analyze_dataset(csv_path, output_dir, use_ollama)
