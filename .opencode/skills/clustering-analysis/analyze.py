#!/usr/bin/env python3
"""
RecordsReveal Clustering Analysis Skill
K-Means clustering with PCA visualization and Ollama insights
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

from ollama_helper import ask_ollama_write, test_connection

def analyze_clustering(csv_path, output_dir="analysis_results"):
    """
    Perform K-Means clustering with PCA visualization
    """
    print("\n" + "="*70)
    print("🧩 RECORDSREVEAL CLUSTERING ANALYSIS")
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
        "analysis_type": "clustering",
        "dataset": str(csv_path),
        "patterns": {}
    }
    
    print("="*70)
    print("🔍 PREPARING DATA FOR CLUSTERING")
    print("="*70 + "\n")
    
    # Select numeric columns only
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        print("❌ Error: Need at least 2 numeric columns for clustering")
        return None
    
    X = df[numeric_cols].fillna(0)
    
    print(f"Features: {len(numeric_cols)} numeric columns")
    print(f"Samples: {len(X):,}\n")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Elbow method to find optimal k
    print("="*70)
    print("📈 ELBOW METHOD (Finding Optimal K)")
    print("="*70 + "\n")
    
    k_range = range(2, min(11, len(X) // 10))  # Test k from 2 to 10
    inertias = []
    silhouette_scores = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertias.append(float(kmeans.inertia_))
        
        # Calculate silhouette score
        if k < len(X):
            sil_score = silhouette_score(X_scaled, labels)
            silhouette_scores.append(float(sil_score))
        else:
            silhouette_scores.append(0.0)
    
    # Find elbow (simple method: look for largest decrease)
    decreases = np.diff(inertias)
    elbow_idx = np.argmax(decreases) + 1  # +1 because diff reduces length by 1
    optimal_k = list(k_range)[elbow_idx] if elbow_idx < len(k_range) else list(k_range)[0]
    
    # Alternative: use highest silhouette score
    sil_optimal_k = list(k_range)[np.argmax(silhouette_scores)]
    
    # Use silhouette if reasonable, otherwise use elbow
    if silhouette_scores[list(k_range).index(sil_optimal_k)] > 0.3:
        optimal_k = sil_optimal_k
    
    print(f"Tested k from {min(k_range)} to {max(k_range)}")
    print(f"Optimal k: {optimal_k}\n")
    
    results["patterns"]["elbow"] = {
        "k_values": list(k_range),
        "inertias": inertias
    }
    results["patterns"]["optimal_k"] = int(optimal_k)
    
    # Run final clustering with optimal k
    print("="*70)
    print(f"🎯 CLUSTERING WITH K={optimal_k}")
    print("="*70 + "\n")
    
    kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans_final.fit_predict(X_scaled)
    
    # Calculate final silhouette score
    final_silhouette = silhouette_score(X_scaled, cluster_labels)
    
    # Cluster sizes
    unique, counts = np.unique(cluster_labels, return_counts=True)
    cluster_sizes = counts.tolist()
    
    print(f"Silhouette score: {final_silhouette:.3f}")
    print(f"\nCluster sizes:")
    for i, size in enumerate(cluster_sizes):
        pct = size / len(X) * 100
        print(f"   Cluster {i}: {size:,} samples ({pct:.1f}%)")
    print()
    
    results["patterns"]["cluster_sizes"] = cluster_sizes
    results["patterns"]["silhouette_score"] = float(final_silhouette)
    
    # PCA for visualization
    print("="*70)
    print("📊 PCA FOR 2D VISUALIZATION")
    print("="*70 + "\n")
    
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    
    variance_explained = pca.explained_variance_ratio_ * 100
    
    print(f"PC1 variance: {variance_explained[0]:.1f}%")
    print(f"PC2 variance: {variance_explained[1]:.1f}%")
    print(f"Total: {variance_explained.sum():.1f}%\n")
    
    results["patterns"]["pca"] = {
        "x": X_pca[:, 0].tolist(),
        "y": X_pca[:, 1].tolist(),
        "labels": cluster_labels.tolist(),
        "variance_1": float(variance_explained[0]),
        "variance_2": float(variance_explained[1]),
        "total_variance": float(variance_explained.sum())
    }
    
    # Cluster profiles
    print("="*70)
    print("📋 CLUSTER PROFILES")
    print("="*70 + "\n")
    
    df_with_clusters = df[numeric_cols].copy()
    df_with_clusters['cluster'] = cluster_labels
    
    cluster_profiles = []
    for i in range(optimal_k):
        cluster_data = df_with_clusters[df_with_clusters['cluster'] == i]
        
        profile = {
            "cluster_id": int(i),
            "size": int(len(cluster_data)),
            "percentage": float(len(cluster_data) / len(X) * 100),
            "means": {}
        }
        
        # Calculate means for top features
        for col in numeric_cols[:5]:  # Top 5 features
            profile["means"][col] = float(cluster_data[col].mean())
        
        cluster_profiles.append(profile)
        
        print(f"Cluster {i} ({profile['percentage']:.1f}%):")
        for col, mean_val in list(profile["means"].items())[:3]:
            print(f"   {col}: {mean_val:.2f}")
        print()
    
    results["patterns"]["cluster_profiles"] = cluster_profiles
    
    # Ask Ollama for cluster names
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING CLUSTER NAMES (OLLAMA)")
        print("="*70 + "\n")
        
        summary = format_clustering_summary(results, numeric_cols)
        
        prompt = f"""You are a data journalist analyzing K-Means clustering results.

Here's what I found:
{summary}

For each of the {optimal_k} clusters, provide:
1. A short descriptive name (2-4 words)
2. A one-sentence description of what makes this cluster unique

Format as a simple list. Keep names memorable and journalistic."""
        
        print("Asking Ollama to name clusters...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama Cluster Names:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            results["ollama_insights"] = insights
            
            # Try to extract cluster names from response
            cluster_names = extract_cluster_names(insights, optimal_k)
            if cluster_names:
                results["patterns"]["cluster_names"] = cluster_names
    
    # Save results
    output_path = os.path.join(output_dir, "clustering_insights.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ CLUSTERING ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Optimal k: {optimal_k} clusters")
    print(f"Silhouette: {final_silhouette:.3f}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def format_clustering_summary(results, numeric_cols):
    """Format clustering results for Ollama"""
    summary = []
    
    patterns = results.get("patterns", {})
    
    summary.append(f"Optimal clusters: {patterns.get('optimal_k')}")
    summary.append(f"Silhouette score: {patterns.get('silhouette_score', 0):.3f}")
    summary.append(f"Features used: {', '.join(numeric_cols[:5])}")
    
    # Cluster sizes
    if 'cluster_sizes' in patterns:
        summary.append("\nCluster sizes:")
        for i, size in enumerate(patterns['cluster_sizes']):
            pct = size / sum(patterns['cluster_sizes']) * 100
            summary.append(f"  Cluster {i}: {size:,} ({pct:.1f}%)")
    
    # Cluster profiles (simplified)
    if 'cluster_profiles' in patterns:
        summary.append("\nCluster characteristics:")
        for profile in patterns['cluster_profiles']:
            summary.append(f"  Cluster {profile['cluster_id']}: {profile['size']} samples")
    
    return "\n".join(summary)

def extract_cluster_names(ollama_response, k):
    """Try to extract cluster names from Ollama response"""
    cluster_names = []
    lines = ollama_response.split('\n')
    
    for line in lines:
        # Look for patterns like "Cluster 0:", "1.", etc.
        if any(str(i) in line for i in range(k)):
            # Extract text after cluster number
            parts = line.split(':', 1)
            if len(parts) > 1:
                name = parts[1].strip().split('.')[0].strip()
                if name and len(name) < 50:
                    cluster_names.append(name)
    
    return cluster_names[:k] if len(cluster_names) >= k else []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <csv_path> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_results"
    
    analyze_clustering(csv_path, output_dir)
