#!/usr/bin/env python3
"""
RecordsReveal Classification Analysis Skill
Trains ML models with feature importance and Ollama insights
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, Lasso
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('ignore')

from ollama_helper import ask_ollama_write, test_connection

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

def analyze_classification(csv_path, target_column, output_dir="analysis_results"):
    """
    Train classification models and analyze feature importance
    """
    print("\n" + "="*70)
    print("🤖 RECORDSREVEAL CLASSIFICATION ANALYSIS")
    print("="*70)
    print(f"Dataset: {csv_path}")
    print(f"Target: {target_column}")
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
    
    # Check if target column exists
    if target_column not in df.columns:
        print(f"❌ Error: Column '{target_column}' not found")
        return None
    
    results = {
        "analysis_type": "classification",
        "dataset": str(csv_path),
        "target_column": target_column,
        "patterns": {}
    }
    
    print("="*70)
    print("🔍 PREPARING DATA FOR ML")
    print("="*70 + "\n")
    
    # Prepare features and target
    df_clean = df.dropna(subset=[target_column])
    y = df_clean[target_column]
    
    # Select numeric features only for simplicity
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if target_column in numeric_cols:
        numeric_cols.remove(target_column)
    
    if len(numeric_cols) < 2:
        print("❌ Error: Need at least 2 numeric features for classification")
        return None
    
    X = df_clean[numeric_cols].fillna(0)
    
    print(f"Features: {len(numeric_cols)} numeric columns")
    print(f"Target: {target_column} ({len(y.unique())} classes)")
    print(f"Samples: {len(X):,}\n")
    
    # Encode target if categorical
    if y.dtype == 'object':
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        class_names = le.classes_.tolist()
    else:
        y_encoded = y.values
        class_names = sorted(y.unique().tolist())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Train: {len(X_train):,} samples")
    print(f"Test: {len(X_test):,} samples\n")
    
    # Train models
    print("="*70)
    print("🎯 TRAINING CLASSIFICATION MODELS")
    print("="*70 + "\n")
    
    models_results = {}
    
    # Logistic Regression
    print("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    y_pred = lr.predict(X_test_scaled)
    
    models_results['LogisticRegression'] = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
    }
    print(f"   Accuracy: {models_results['LogisticRegression']['accuracy']:.3f}\n")
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    
    models_results['RandomForest'] = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
    }
    print(f"   Accuracy: {models_results['RandomForest']['accuracy']:.3f}\n")
    
    # XGBoost (if available)
    if XGBOOST_AVAILABLE:
        print("Training XGBoost...")
        xgb = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
        xgb.fit(X_train, y_train)
        y_pred = xgb.predict(X_test)
        
        models_results['XGBoost'] = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        }
        print(f"   Accuracy: {models_results['XGBoost']['accuracy']:.3f}\n")
    
    # Find best model
    best_model_name = max(models_results.keys(), key=lambda k: models_results[k]['accuracy'])
    best_accuracy = models_results[best_model_name]['accuracy']
    
    print(f"🏆 Best Model: {best_model_name} ({best_accuracy:.3f} accuracy)\n")
    
    results["patterns"]["models"] = models_results
    results["patterns"]["best_model"] = best_model_name
    results["patterns"]["best_accuracy"] = float(best_accuracy)
    
    # Feature Importance (from Random Forest)
    print("="*70)
    print("📊 FEATURE IMPORTANCE")
    print("="*70 + "\n")
    
    feature_importance = []
    for i, col in enumerate(numeric_cols):
        importance = float(rf.feature_importances_[i])
        feature_importance.append({
            "feature": col,
            "importance": importance
        })
    
    # Sort by importance
    feature_importance.sort(key=lambda x: x['importance'], reverse=True)
    
    print("Top 10 features:")
    for i, feat in enumerate(feature_importance[:10], 1):
        print(f"   {i}. {feat['feature']}: {feat['importance']:.4f}")
    print()
    
    results["patterns"]["feature_importance"] = feature_importance
    results["patterns"]["top_feature"] = feature_importance[0]['feature']
    results["patterns"]["top_feature_importance"] = feature_importance[0]['importance']
    
    # Lasso Coefficients (for linear relationship)
    print("="*70)
    print("📈 LASSO COEFFICIENTS")
    print("="*70 + "\n")
    
    # For multi-class, use first class coefficients
    lasso_coefs = []
    if hasattr(lr, 'coef_'):
        coef_array = lr.coef_[0] if len(lr.coef_.shape) > 1 else lr.coef_
        for i, col in enumerate(numeric_cols):
            lasso_coefs.append({
                "feature": col,
                "coefficient": float(coef_array[i])
            })
    
    # Sort by absolute value
    lasso_coefs.sort(key=lambda x: abs(x['coefficient']), reverse=True)
    
    print("Top 10 coefficients:")
    for i, coef in enumerate(lasso_coefs[:10], 1):
        sign = "+" if coef['coefficient'] > 0 else ""
        print(f"   {i}. {coef['feature']}: {sign}{coef['coefficient']:.4f}")
    print()
    
    results["patterns"]["lasso_coefficients"] = lasso_coefs
    
    # Identify eliminated features (near-zero coefficients)
    eliminated = [c['feature'] for c in lasso_coefs if abs(c['coefficient']) < 0.01]
    results["patterns"]["lasso_eliminated"] = eliminated
    if eliminated:
        print(f"Features eliminated by Lasso: {len(eliminated)}")
        print(f"   {', '.join(eliminated[:5])}{'...' if len(eliminated) > 5 else ''}\n")
    
    # Ask Ollama for insights
    if use_ollama:
        print("="*70)
        print("🤖 GENERATING AI INSIGHTS (OLLAMA)")
        print("="*70 + "\n")
        
        summary = format_classification_summary(results)
        
        prompt = f"""You are a data journalist analyzing machine learning classification results.

Here's what I found:
{summary}

Please provide:
1. The most newsworthy finding about these predictions (1-2 sentences)
2. What the feature importance reveals about the data (1-2 sentences)
3. A compelling pull quote for an article (10-15 words, quotable)

Keep it journalistic and accessible to non-technical readers."""
        
        print("Asking Ollama for ML insights...")
        insights = ask_ollama_write(prompt)
        
        if insights:
            print("\n📰 Ollama ML Insights:")
            print("-" * 70)
            print(insights)
            print("-" * 70 + "\n")
            results["ollama_insights"] = insights
    
    # Save results
    output_path = os.path.join(output_dir, "classification_insights.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("="*70)
    print("✅ CLASSIFICATION ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutput: {output_path}")
    print(f"Best model: {best_model_name} ({best_accuracy:.1%})")
    print(f"Top feature: {results['patterns']['top_feature']}")
    print(f"Cost: $0.00 (Ollama)\n")
    
    return results

def format_classification_summary(results):
    """Format classification results for Ollama"""
    summary = []
    
    patterns = results.get("patterns", {})
    
    summary.append(f"Target: {results.get('target_column')}")
    summary.append(f"Best model: {patterns.get('best_model')} ({patterns.get('best_accuracy', 0):.1%} accuracy)")
    
    # Model comparison
    if 'models' in patterns:
        summary.append("\nModel performance:")
        for name, metrics in patterns['models'].items():
            summary.append(f"  {name}: {metrics['accuracy']:.3f} accuracy")
    
    # Top features
    if 'feature_importance' in patterns:
        top_feats = patterns['feature_importance'][:3]
        summary.append("\nTop 3 features:")
        for feat in top_feats:
            summary.append(f"  {feat['feature']}: {feat['importance']:.3f}")
    
    return "\n".join(summary)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python analyze.py <csv_path> <target_column> [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    target_column = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "analysis_results"
    
    analyze_classification(csv_path, target_column, output_dir)
