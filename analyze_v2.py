#!/usr/bin/env python3
"""
RecordsReveal Enhanced Analysis Script v2.0
============================================
Intelligent data analysis with auto-detection of data types.

Features:
- Auto-detects regression vs classification problems
- Adds XGBoost for better performance
- Creates classification metrics (ROC, confusion matrix)
- Generates correlation heatmaps
- Handles class imbalance
- Exports comprehensive JSON results
"""

import pandas as pd
import numpy as np
import json
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)

# Visualization
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not installed. Install with: pip install xgboost")

# Domain-specific visualizations
try:
    from enhance_visualizations import generate_domain_visualizations
    ENHANCED_VIZ_AVAILABLE = True
except ImportError:
    ENHANCED_VIZ_AVAILABLE = False
    print("⚠️  Enhanced visualizations module not found")


class DatasetProfiler:
    """Automatically detect dataset characteristics"""
    
    def __init__(self, df):
        self.df = df
        self.profile = {}
    
    def analyze(self):
        """Run full dataset profiling"""
        print("\n" + "="*60)
        print("🔍 ANALYZING DATASET CHARACTERISTICS")
        print("="*60)
        
        self.profile['shape'] = self.df.shape
        self.profile['columns'] = list(self.df.columns)
        self.profile['dtypes'] = self.df.dtypes.astype(str).to_dict()
        self.profile['missing'] = self.df.isnull().sum().to_dict()
        self.profile['missing_percent'] = (self.df.isnull().sum() / len(self.df) * 100).to_dict()
        
        # Detect column types
        self.profile['numeric_cols'] = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.profile['categorical_cols'] = self.df.select_dtypes(include=['object']).columns.tolist()
        self.profile['datetime_cols'] = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Check for datetime-like columns that weren't auto-detected
        for col in self.profile['categorical_cols']:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.df[col].dropna().head(100))
                    self.profile['datetime_cols'].append(col)
                    print(f"   📅 Detected datetime column: {col}")
                except:
                    pass
        
        # Check for coordinate columns
        coord_patterns = ['lat', 'lon', 'latitude', 'longitude', 'coord']
        self.profile['coordinate_cols'] = [
            col for col in self.df.columns 
            if any(pattern in col.lower() for pattern in coord_patterns)
        ]
        
        # Check for text columns (long strings)
        self.profile['text_cols'] = []
        for col in self.profile['categorical_cols']:
            if col not in self.profile['datetime_cols']:
                avg_length = self.df[col].dropna().astype(str).str.len().mean()
                if avg_length > 50:  # Likely text/description
                    self.profile['text_cols'].append(col)
        
        print(f"\n📊 Dataset Shape: {self.profile['shape']}")
        print(f"   Numeric columns: {len(self.profile['numeric_cols'])}")
        print(f"   Categorical columns: {len(self.profile['categorical_cols'])}")
        print(f"   Datetime columns: {len(self.profile['datetime_cols'])}")
        print(f"   Coordinate columns: {len(self.profile['coordinate_cols'])}")
        print(f"   Text columns: {len(self.profile['text_cols'])}")
        
        return self.profile
    
    def detect_target_type(self, target_col):
        """Determine if target is regression or classification"""
        
        if target_col not in self.df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataset")
        
        target = self.df[target_col].dropna()
        unique_count = target.nunique()
        
        print(f"\n🎯 Target Variable: {target_col}")
        print(f"   Unique values: {unique_count}")
        print(f"   Data type: {target.dtype}")
        
        # Classification if:
        # - Boolean type
        # - Object/string type
        # - Integer with few unique values (< 10)
        # - Float but only has integer values (0.0, 1.0, 2.0)
        
        if target.dtype == 'bool':
            task_type = 'binary_classification'
            print(f"   ✓ Detected: BINARY CLASSIFICATION (boolean)")
        
        elif target.dtype == 'object':
            if unique_count == 2:
                task_type = 'binary_classification'
                print(f"   ✓ Detected: BINARY CLASSIFICATION (2 categories)")
            else:
                task_type = 'multiclass_classification'
                print(f"   ✓ Detected: MULTI-CLASS CLASSIFICATION ({unique_count} classes)")
        
        elif unique_count == 2:
            task_type = 'binary_classification'
            print(f"   ✓ Detected: BINARY CLASSIFICATION (2 values)")
        
        elif unique_count <= 10 and target.dtype in ['int64', 'int32']:
            # Check if it's a count variable (starts at 0, increments by 1)
            sorted_unique = np.sort(target.unique())
            is_count = (sorted_unique[0] == 0 and 
                       np.allclose(np.diff(sorted_unique), 1) and
                       all(v >= 0 for v in sorted_unique))
            
            if is_count:
                task_type = 'regression'
                print(f"   ✓ Detected: REGRESSION (count variable: {unique_count} values)")
            else:
                task_type = 'multiclass_classification'
                print(f"   ✓ Detected: MULTI-CLASS CLASSIFICATION ({unique_count} classes)")
        
        elif target.dtype in ['float64', 'float32'] and np.allclose(target, target.astype(int)):
            if unique_count <= 10:
                # Check if it's a count-like variable
                sorted_unique = np.sort(target.unique())
                is_count = (sorted_unique[0] >= 0 and np.allclose(np.diff(sorted_unique), 1))
                
                if is_count:
                    task_type = 'regression'
                    print(f"   ✓ Detected: REGRESSION (count variable: {unique_count} values)")
                else:
                    task_type = 'multiclass_classification'
                    print(f"   ✓ Detected: MULTI-CLASS CLASSIFICATION ({unique_count} classes)")
            else:
                task_type = 'regression'
                print(f"   ✓ Detected: REGRESSION (continuous values)")
        
        else:
            task_type = 'regression'
            print(f"   ✓ Detected: REGRESSION (continuous values)")
        
        # Check for class imbalance in classification
        if 'classification' in task_type:
            value_counts = target.value_counts()
            max_class = value_counts.max()
            min_class = value_counts.min()
            imbalance_ratio = max_class / min_class if min_class > 0 else float('inf')
            
            print(f"\n   Class distribution:")
            for value, count in value_counts.items():
                pct = count / len(target) * 100
                print(f"      {value}: {count} ({pct:.1f}%)")
            
            if imbalance_ratio > 3:
                print(f"   ⚠️  Class imbalance detected (ratio: {imbalance_ratio:.1f}:1)")
                self.profile['class_imbalance'] = imbalance_ratio
        
        self.profile['target_type'] = task_type
        return task_type


class EnhancedAnalyzer:
    """Main analysis engine with auto-detection"""
    
    def __init__(self, csv_path, target_col=None):
        self.csv_path = Path(csv_path)
        self.df = pd.read_csv(csv_path)
        self.target_col = target_col
        self.profiler = DatasetProfiler(self.df)
        self.results = {
            'dataset': str(self.csv_path),
            'profile': {},
            'eda': {},
            'models': {},
            'clustering': {},
            'visualizations': {}
        }
    
    def run(self):
        """Execute full analysis pipeline"""
        
        print("\n" + "="*60)
        print("🚀 RECORDSREVEAL ENHANCED ANALYSIS v2.0")
        print("="*60)
        
        # Step 1: Profile the dataset
        self.results['profile'] = self.profiler.analyze()
        
        # Step 2: Auto-detect target if not specified
        if not self.target_col:
            self.target_col = self._auto_detect_target()
        
        # Step 3: Detect task type
        task_type = self.profiler.detect_target_type(self.target_col)
        
        # Step 4: Run EDA
        self.run_eda()
        
        # Step 5: Run appropriate modeling
        if task_type == 'regression':
            self.run_regression_models()
        elif 'classification' in task_type:
            self.run_classification_models()
        
        # Step 6: Run clustering
        self.run_clustering()
        
        # Step 7: Generate domain-specific visualizations
        if ENHANCED_VIZ_AVAILABLE:
            output_dir = self.csv_path.parent / 'analysis_results' / 'visualizations'
            domain_viz = generate_domain_visualizations(
                self.df, 
                self.target_col, 
                output_dir,
                theme_color='#d2691e'
            )
            self.results['domain_visualizations'] = domain_viz
        
        # Step 8: Export results
        self.export_results()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE!")
        print("="*60)
        
        return self.results
    
    def _auto_detect_target(self):
        """Try to automatically identify the target variable"""
        print("\n🤔 Auto-detecting target variable...")
        
        # Common target column name patterns
        target_patterns = [
            'target', 'label', 'class', 'outcome', 'result', 'prediction',
            'y', 'dependent', 'response', 'casualties', 'revenue', 'price',
            'damage', 'rating', 'score', 'survived', 'churn', 'fraud'
        ]
        
        # Look for columns matching patterns
        for pattern in target_patterns:
            matches = [col for col in self.df.columns if pattern in col.lower()]
            if matches:
                target = matches[0]
                print(f"   ✓ Found potential target: {target}")
                return target
        
        # If no match, use last column as default
        target = self.df.columns[-1]
        print(f"   ⚠️  No obvious target found, using last column: {target}")
        return target
    
    def run_eda(self):
        """Exploratory Data Analysis"""
        print("\n" + "="*60)
        print("📊 EXPLORATORY DATA ANALYSIS")
        print("="*60)
        
        # Basic statistics
        self.results['eda']['basic_stats'] = self.df.describe().to_dict()
        
        # Correlation matrix for numeric columns
        numeric_df = self.df[self.results['profile']['numeric_cols']]
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            
            # Create correlation heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 8}
            ))
            fig.update_layout(
                title='Feature Correlation Heatmap',
                width=1000,
                height=800,
                autosize=False
            )
            
            self.results['visualizations']['correlation_heatmap'] = fig.to_html(include_plotlyjs='cdn')
            print("   ✓ Generated correlation heatmap")
        
        # Distribution of target variable
        target_data = self.df[self.target_col].dropna()
        
        if self.results['profile']['target_type'] == 'regression':
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=target_data, nbinsx=50, name=self.target_col))
            fig.update_layout(
                title=f'Distribution of {self.target_col}',
                xaxis_title=self.target_col,
                yaxis_title='Frequency',
                width=1000,
                height=600,
                autosize=False
            )
        else:
            value_counts = target_data.value_counts()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=value_counts.index, y=value_counts.values))
            fig.update_layout(
                title=f'Distribution of {self.target_col}',
                xaxis_title=self.target_col,
                yaxis_title='Count',
                width=1000,
                height=600,
                autosize=False
            )
        
        self.results['visualizations']['target_distribution'] = fig.to_html(include_plotlyjs='cdn')
        print("   ✓ Generated target distribution plot")
    
    def run_regression_models(self):
        """Run regression model suite"""
        print("\n" + "="*60)
        print("🤖 REGRESSION MODELS")
        print("="*60)
        
        # Prepare data
        X, y = self._prepare_features()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        }
        
        if XGBOOST_AVAILABLE:
            models['XGBoost'] = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        
        results = {}
        
        for name, model in models.items():
            print(f"\n   Training {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            results[name] = {
                'r2_score': float(r2),
                'rmse': float(rmse),
                'mae': float(mae)
            }
            
            # Feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                results[name]['feature_importance'] = {
                    col: float(imp) for col, imp in zip(X.columns, importance)
                }
            
            print(f"      R² = {r2:.4f}, RMSE = {rmse:.4f}, MAE = {mae:.4f}")
        
        self.results['models']['regression'] = results
        
        # Create model comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(results.keys()),
            y=[results[m]['r2_score'] for m in results.keys()],
            name='R² Score'
        ))
        fig.update_layout(
            title='Model Comparison - R² Scores',
            yaxis_title='R² Score',
            xaxis_title='Model',
            width=1000,
            height=600,
            autosize=False
        )
        self.results['visualizations']['model_comparison'] = fig.to_html(include_plotlyjs='cdn')
        
        # Best model
        best_model = max(results.items(), key=lambda x: x[1]['r2_score'])
        print(f"\n   🏆 Best Model: {best_model[0]} (R² = {best_model[1]['r2_score']:.4f})")
        self.results['models']['best_model'] = best_model[0]
    
    def run_classification_models(self):
        """Run classification model suite"""
        print("\n" + "="*60)
        print("🤖 CLASSIFICATION MODELS")
        print("="*60)
        
        # Prepare data
        X, y = self._prepare_features()
        
        # Encode target if needed
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            self.results['models']['label_mapping'] = {str(i): label for i, label in enumerate(le.classes_)}
        
        # Only use stratify if classes have sufficient samples
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        except ValueError:
            # Fall back to non-stratified split for extreme class imbalance
            print("   ⚠️  Extreme class imbalance - using non-stratified split")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Determine if binary or multiclass
        is_binary = len(np.unique(y)) == 2
        
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        }
        
        if XGBOOST_AVAILABLE:
            models['XGBoost'] = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
        
        results = {}
        
        for name, model in models.items():
            print(f"\n   Training {name}...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            
            # For binary classification
            if is_binary:
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                auc = roc_auc_score(y_test, y_proba[:, 1])
                
                results[name] = {
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1_score': float(f1),
                    'roc_auc': float(auc)
                }
                
                print(f"      Accuracy = {accuracy:.4f}, Precision = {precision:.4f}, Recall = {recall:.4f}, F1 = {f1:.4f}, AUC = {auc:.4f}")
            
            # For multiclass
            else:
                precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                results[name] = {
                    'accuracy': float(accuracy),
                    'precision_weighted': float(precision),
                    'recall_weighted': float(recall),
                    'f1_score_weighted': float(f1)
                }
                
                print(f"      Accuracy = {accuracy:.4f}, Precision = {precision:.4f}, Recall = {recall:.4f}, F1 = {f1:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            results[name]['confusion_matrix'] = cm.tolist()
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                results[name]['feature_importance'] = {
                    col: float(imp) for col, imp in zip(X.columns, importance)
                }
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_[0]) if is_binary else np.abs(model.coef_).mean(axis=0)
                results[name]['feature_importance'] = {
                    col: float(imp) for col, imp in zip(X.columns, importance)
                }
        
        self.results['models']['classification'] = results
        
        # Create confusion matrix heatmap for best model
        best_model_name = max(results.items(), key=lambda x: x[1].get('f1_score', x[1].get('f1_score_weighted', 0)))[0]
        cm = np.array(results[best_model_name]['confusion_matrix'])
        
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            text=cm,
            texttemplate='%{text}',
            colorscale='Blues'
        ))
        fig.update_layout(
            title=f'Confusion Matrix - {best_model_name}',
            xaxis_title='Predicted',
            yaxis_title='Actual',
            width=800,
            height=700,
            autosize=False
        )
        self.results['visualizations']['confusion_matrix'] = fig.to_html(include_plotlyjs='cdn')
        
        print(f"\n   🏆 Best Model: {best_model_name}")
        self.results['models']['best_model'] = best_model_name
    
    def run_clustering(self):
        """K-Means clustering analysis"""
        print("\n" + "="*60)
        print("🔍 CLUSTERING ANALYSIS")
        print("="*60)
        
        # Prepare features (without target)
        X, _ = self._prepare_features()
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Elbow method
        inertias = []
        K_range = range(2, 11)
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
        
        # Fit with K=4
        optimal_k = 4
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # PCA for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        self.results['clustering'] = {
            'optimal_k': optimal_k,
            'inertias': {int(k): float(inertia) for k, inertia in zip(K_range, inertias)},
            'pca_variance_explained': {
                'pc1': float(pca.explained_variance_ratio_[0]),
                'pc2': float(pca.explained_variance_ratio_[1]),
                'total': float(pca.explained_variance_ratio_.sum())
            },
            'cluster_sizes': {int(i): int(np.sum(clusters == i)) for i in range(optimal_k)}
        }
        
        # Create elbow plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(K_range),
            y=inertias,
            mode='lines+markers',
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Elbow Method - Optimal K Selection',
            xaxis_title='Number of Clusters (K)',
            yaxis_title='Inertia',
            width=1000,
            height=600,
            autosize=False
        )
        self.results['visualizations']['elbow_plot'] = fig.to_html(include_plotlyjs='cdn')
        
        # Create PCA cluster plot
        fig = go.Figure()
        for i in range(optimal_k):
            mask = clusters == i
            fig.add_trace(go.Scatter(
                x=X_pca[mask, 0],
                y=X_pca[mask, 1],
                mode='markers',
                name=f'Cluster {i}',
                marker=dict(size=5, opacity=0.6)
            ))
        fig.update_layout(
            title='Cluster Visualization (PCA 2D)',
            xaxis_title=f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)',
            yaxis_title=f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)',
            width=1000,
            height=700,
            autosize=False
        )
        self.results['visualizations']['cluster_plot'] = fig.to_html(include_plotlyjs='cdn')
        
        print(f"   ✓ Optimal K = {optimal_k}")
        print(f"   ✓ PCA explains {pca.explained_variance_ratio_.sum()*100:.1f}% variance")
        for i in range(optimal_k):
            count = np.sum(clusters == i)
            pct = count / len(clusters) * 100
            print(f"      Cluster {i}: {count} samples ({pct:.1f}%)")
    
    def _prepare_features(self):
        """Prepare feature matrix X and target y"""
        # Drop rows with missing target
        df_clean = self.df.dropna(subset=[self.target_col]).copy()
        
        # Separate target
        y = df_clean[self.target_col]
        X = df_clean.drop(columns=[self.target_col])
        
        # Keep only numeric columns or encode categoricals
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        # For now, use only numeric columns
        # In future versions, we can add sophisticated categorical encoding
        X = X[numeric_cols]
        
        # Fill any remaining missing values with median
        X = X.fillna(X.median())
        
        # Limit to reasonable number of features (top by variance)
        if len(X.columns) > 20:
            variances = X.var().sort_values(ascending=False)
            top_features = variances.head(20).index
            X = X[top_features]
            print(f"   ℹ️  Using top 20 features by variance")
        
        return X, y
    
    def export_results(self):
        """Export results to JSON and HTML"""
        output_dir = self.csv_path.parent / 'analysis_results'
        output_dir.mkdir(exist_ok=True)
        
        # Export JSON (without HTML visualizations)
        json_results = {k: v for k, v in self.results.items() if k != 'visualizations'}
        json_path = output_dir / 'results.json'
        with open(json_path, 'w') as f:
            json.dump(json_results, f, indent=2)
        print(f"\n   📄 Results saved to: {json_path}")
        
        # Export visualizations as separate HTML files
        viz_dir = output_dir / 'visualizations'
        viz_dir.mkdir(exist_ok=True)
        
        for viz_name, viz_html in self.results['visualizations'].items():
            viz_path = viz_dir / f'{viz_name}.html'
            
            # viz_html is already a complete HTML document from to_html(include_plotlyjs='cdn')
            with open(viz_path, 'w') as f:
                f.write(viz_html)
        
        print(f"   📊 Visualizations saved to: {viz_dir}")
        
        return json_path


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_v2.py <csv_file> [target_column]")
        print("\nExample:")
        print("  python analyze_v2.py data.csv")
        print("  python analyze_v2.py data.csv total_casualties")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    target_col = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = EnhancedAnalyzer(csv_path, target_col)
    analyzer.run()


if __name__ == '__main__':
    main()
