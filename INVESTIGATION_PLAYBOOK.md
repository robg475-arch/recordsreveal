# RecordsReveal Investigation Playbook
> How to programmatically build a complete data investigation from any public dataset
> From raw CSV to live website with interactive charts, AdSense, and social sharing

---

## Overview

Every RecordsReveal investigation is built from the same repeatable pipeline:

```
Dataset → Analysis → Numbers → Charts → Story → HTML Page → Deploy
```

This document gives you the exact code, templates, and process to replicate this
for any new dataset — fully programmatically.

---

## Prerequisites

### Mac (Main Workstation)
```bash
# Python environment
cd ~/Documents/Claude/Projects
python3 -m venv datascience
source datascience/bin/activate
pip install pandas numpy scikit-learn plotly matplotlib seaborn requests kaggle jupyter

# Kaggle API credentials
mkdir -p ~/.kaggle
# Place kaggle.json at ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Linux PC (GPU Server — optional but recommended)
- Ollama running at `192.168.1.153:11434`
- Models: `qwen2.5-coder:7b` and `llama3.2`
- Auto-starts on boot via systemd

### Ollama Helper (use in every notebook)
```python
import requests

OLLAMA_HOST = "http://192.168.1.153:11434"  # Linux GPU server

def ask_ollama(prompt, model="qwen2.5-coder:7b"):
    """Send prompt to Linux GPU server"""
    r = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120
    )
    return r.json()["response"]

def ask_ollama_code(prompt):
    return ask_ollama(prompt, model="qwen2.5-coder:7b")

def ask_ollama_write(prompt):
    return ask_ollama(prompt, model="llama3.2")
```

---

## Phase 1 — Dataset Selection

### Checklist Before Committing
```python
def evaluate_dataset(df, target_col, feature_cols):
    """
    Score a dataset for investigation potential.
    Returns a dict of quality metrics.
    """
    missing_pct = df[feature_cols + [target_col]].isnull().mean()
    
    return {
        "row_count": len(df),                              # Need 50K+
        "feature_count": len(feature_cols),                # Need 8+
        "target_missing_pct": missing_pct[target_col],    # Need <30%
        "avg_feature_missing": missing_pct[feature_cols].mean(),
        "target_variance": df[target_col].var(),           # Need >0
        "viable": (
            len(df) >= 50000 and
            len(feature_cols) >= 8 and
            missing_pct[target_col] < 0.30
        )
    }
```

### Downloading from Kaggle
```python
import subprocess

def download_kaggle_dataset(slug, dest_dir="~/datascience"):
    """
    slug: e.g. 'utkarshx27/movies-dataset'
    """
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", slug, "--unzip", "-p", dest_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
    return result.returncode == 0

# Example
download_kaggle_dataset("utkarshx27/movies-dataset")
```

### Proven Dataset Sources
| Topic | Kaggle Slug or URL | Key Column |
|---|---|---|
| FAA Bird Strikes | `bartekmietlicki/faa-wildlife-strikes` | DAMAGE_LEVEL |
| Movies/Box Office | `utkarshx27/movies-dataset` | revenue |
| Car Crashes (NHTSA) | data.gov FARS dataset | injury_severity |
| Food Nutrition | `nih-nutrition/usda-food-nutritional-profiles` | caloric_density |
| Crime Stats | data.gov FBI UCR | violent_crime_rate |
| Hospital Readmissions | data.cms.gov | readmission_rate |

---

## Phase 2 — Exploratory Data Analysis (EDA)

### Standard EDA Template
```python
import pandas as pd
import numpy as np
import plotly.express as px

def run_eda(df, config):
    """
    config = {
        'name': 'FAA Wildlife Strikes',
        'target_col': 'DAMAGE_LEVEL',
        'date_col': 'INCIDENT_YEAR',
        'group_col': 'AIRPORT',
        'numeric_cols': ['HEIGHT', 'SPEED', 'NUM_ENGS'],
        'categorical_cols': ['PHASE_OF_FLIGHT', 'SIZE', 'AC_CLASS'],
        'top_n': 15
    }
    Returns dict of all findings needed for the page.
    """
    results = {}

    # 1. Basic shape
    results['total_records'] = len(df)
    results['date_range'] = f"{df[config['date_col']].min()} – {df[config['date_col']].max()}"

    # 2. Missing values
    missing = df.isnull().sum() / len(df) * 100
    results['missing'] = missing.sort_values(ascending=False).to_dict()
    results['good_cols'] = missing[missing < 30].index.tolist()

    # 3. Trend over time
    if config['date_col']:
        trend = df.groupby(config['date_col']).size().reset_index(name='count')
        results['trend_x'] = trend[config['date_col']].tolist()
        results['trend_y'] = trend['count'].tolist()
        results['trend_peak_year'] = trend.loc[trend['count'].idxmax(), config['date_col']]
        results['trend_peak_count'] = int(trend['count'].max())
        results['trend_pct_change'] = round(
            (trend['count'].iloc[-1] - trend['count'].iloc[0]) / trend['count'].iloc[0] * 100
        )

    # 4. Top groups
    if config['group_col']:
        top = df[config['group_col']].value_counts().head(config['top_n'])
        results['top_groups_names'] = top.index.tolist()
        results['top_groups_counts'] = top.values.tolist()
        results['top_group_name'] = top.index[0]
        results['top_group_count'] = int(top.iloc[0])

    # 5. Target distribution
    target = df[config['target_col']].value_counts()
    results['target_dist_labels'] = target.index.tolist()
    results['target_dist_counts'] = target.values.tolist()
    majority_val = target.index[0]
    results['target_majority_pct'] = round(target.iloc[0] / len(df) * 100, 1)
    results['target_majority_label'] = str(majority_val)

    # 6. Correlation with target (numeric only)
    numeric_df = df[config['numeric_cols'] + [config['target_col']]].apply(
        pd.to_numeric, errors='coerce'
    )
    corr = numeric_df.corr()[config['target_col']].drop(config['target_col'])
    results['correlations'] = corr.sort_values(key=abs, ascending=False).to_dict()

    # 7. Category distributions
    for col in config['categorical_cols']:
        vc = df[col].value_counts().head(10)
        results[f'dist_{col}'] = {
            'labels': vc.index.tolist(),
            'counts': vc.values.tolist()
        }

    return results


def ask_ollama_eda_insights(results, topic):
    """Ask Ollama to find the most viral/surprising findings"""
    prompt = f"""
I analyzed a dataset about {topic}. Here are the key findings:

Total records: {results['total_records']:,}
Date range: {results['date_range']}
Top group: {results['top_group_name']} ({results['top_group_count']:,} records)
Target majority: {results['target_majority_pct']}% are '{results['target_majority_label']}'
Trend change: {results['trend_pct_change']}% over the full period

For a general audience (not data scientists), provide:
1. Five surprising/counterintuitive findings with punchy headlines
2. The single most viral finding (the one that would make someone say "wait, really?")
3. Three short pull quotes (stats as quotable sentences)
4. A compelling investigative angle/headline for the whole investigation

Be specific with exact numbers. Write for curious general readers, not academics.
"""
    return ask_ollama_write(prompt)
```

---

## Phase 3 — Supervised Learning Pipeline

### Standard Regression Pipeline
```python
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import numpy as np

def run_regression_pipeline(df, target_col, feature_cols, target_encoding=None):
    """
    target_encoding: dict mapping target values to numbers
                     e.g. {'N':0, 'M':1, 'S':2, 'D':3}
                     or None for numeric targets

    Returns dict of all model results needed for the page.
    """
    results = {}

    # Prepare target
    model_df = df[feature_cols + [target_col]].copy()
    model_df = model_df.dropna(subset=[target_col])

    if target_encoding:
        model_df[target_col] = model_df[target_col].map(target_encoding)
        model_df = model_df.dropna(subset=[target_col])
    else:
        model_df[target_col] = pd.to_numeric(model_df[target_col], errors='coerce')
        model_df = model_df.dropna(subset=[target_col])

    results['model_row_count'] = len(model_df)

    # Encode features
    encoded_df = model_df.copy()
    for col in feature_cols:
        if encoded_df[col].dtype == 'object':
            encoded_df[col] = encoded_df[col].fillna('Unknown')
            le = LabelEncoder()
            encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))
        else:
            encoded_df[col] = pd.to_numeric(encoded_df[col], errors='coerce')
            encoded_df[col] = encoded_df[col].fillna(encoded_df[col].median())

    X = encoded_df[feature_cols]
    y = model_df[target_col]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    results['train_size'] = len(X_train)
    results['test_size'] = len(X_test)

    # Train all models
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge': RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0]),
        'Lasso': LassoCV(alphas=[0.001, 0.01, 0.1], max_iter=2000, cv=3),
        'Random Forest': RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1
        )
    }

    model_results = {}
    best_r2 = -999
    best_model_name = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        model_results[name] = {'r2': round(r2, 4), 'rmse': round(rmse, 4)}
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name

        # Get coefficients if linear
        if hasattr(model, 'coef_'):
            model_results[name]['coefficients'] = dict(
                zip(feature_cols, model.coef_.round(4))
            )

    results['models'] = model_results
    results['best_model'] = best_model_name
    results['best_r2'] = best_r2

    # Feature importance from Random Forest
    rf = models['Random Forest']
    feat_imp = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)

    results['feature_importance'] = feat_imp.to_dict('records')
    results['top_feature'] = feat_imp.iloc[0]['feature']
    results['top_feature_pct'] = round(feat_imp.iloc[0]['importance'] * 100, 1)

    # Lasso feature selection
    lasso = models['Lasso']
    eliminated = [f for f, c in zip(feature_cols, lasso.coef_) if c == 0]
    results['lasso_eliminated'] = eliminated

    return results


def ask_ollama_model_insights(model_results, topic):
    """Ask Ollama to explain model findings for general readers"""
    best = model_results['best_model']
    r2 = model_results['best_r2']
    top_feat = model_results['top_feature']
    top_pct = model_results['top_feature_pct']

    prompt = f"""
I built machine learning models to predict outcomes in {topic} data.

Best model: {best} with R² = {r2:.4f} (explains {r2*100:.1f}% of variance)
Top predictor: '{top_feat}' accounts for {top_pct}% of prediction power
Lasso eliminated these features as unimportant: {model_results['lasso_eliminated']}

For a general audience:
1. Explain what R²={r2:.2f} means in plain English (one sentence)
2. Explain why '{top_feat}' being the top predictor is surprising or interesting
3. Write a headline for the machine learning finding section
4. Write 2-3 sentences explaining what this means for real people

Avoid jargon. Be concrete and specific.
"""
    return ask_ollama_write(prompt)
```

---

## Phase 4 — Unsupervised Learning Pipeline

### Standard K-Means Clustering Pipeline
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def run_clustering_pipeline(df, cluster_features, k_range=range(2, 9)):
    """
    Returns dict of all clustering results needed for the page.
    """
    results = {}

    # Prepare data
    cluster_df = df[cluster_features].copy()
    for col in cluster_features:
        cluster_df[col] = pd.to_numeric(cluster_df[col], errors='coerce')
    cluster_df = cluster_df.dropna()
    results['cluster_row_count'] = len(cluster_df)

    # Scale
    scaler = StandardScaler()
    scaled = scaler.fit_transform(cluster_df)

    # Elbow curve
    inertias = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(scaled)
        inertias.append(km.inertia_)

    results['elbow_k'] = list(k_range)
    results['elbow_inertias'] = [round(i, 0) for i in inertias]

    # Find elbow (largest drop in inertia)
    drops = [inertias[i-1] - inertias[i] for i in range(1, len(inertias))]
    optimal_k = list(k_range)[drops.index(max(drops)) + 1]
    results['optimal_k'] = optimal_k

    # Apply optimal K
    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    labels = km_final.fit_predict(scaled)
    cluster_df['cluster'] = labels

    # PCA for visualization
    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(scaled)
    results['pca_variance'] = [
        round(pca.explained_variance_ratio_[0] * 100, 1),
        round(pca.explained_variance_ratio_[1] * 100, 1)
    ]
    results['pca_total_variance'] = sum(results['pca_variance'])
    results['pca_x'] = pca_coords[:, 0].tolist()
    results['pca_y'] = pca_coords[:, 1].tolist()
    results['pca_labels'] = labels.tolist()

    # Cluster profiles
    profiles = cluster_df.groupby('cluster').agg(['mean', 'count']).round(2)
    cluster_sizes = cluster_df['cluster'].value_counts().sort_index()

    results['cluster_sizes'] = cluster_sizes.to_dict()
    results['cluster_profiles'] = {}

    for c in range(optimal_k):
        mask = cluster_df['cluster'] == c
        results['cluster_profiles'][c] = {
            'size': int(cluster_sizes[c]),
            'pct': round(cluster_sizes[c] / len(cluster_df) * 100, 1),
            'means': cluster_df[mask][cluster_features].mean().round(2).to_dict()
        }

    return results, cluster_df


def ask_ollama_cluster_names(cluster_results, topic, cluster_features):
    """Ask Ollama to name and describe each cluster in plain English"""
    profiles_str = ""
    for c, profile in cluster_results['cluster_profiles'].items():
        profiles_str += f"\nCluster {c} ({profile['size']:,} records, {profile['pct']}%):\n"
        for feat, val in profile['means'].items():
            profiles_str += f"  {feat}: {val}\n"

    prompt = f"""
I ran K-Means clustering (K={cluster_results['optimal_k']}) on {topic} data
using these features: {cluster_features}

Cluster profiles:
{profiles_str}

For each cluster provide:
1. A short memorable name (2-4 words, e.g. "The Summer Blockbuster")
2. A 2-sentence plain English description of what type of {topic} this cluster represents
3. 2-3 real-world examples that would fit this cluster

Make the names distinctive and the descriptions concrete.
"""
    return ask_ollama_write(prompt)
```

---

## Phase 5 — Extract Publishable Numbers

### The Number Extraction Step
This is the most important step — converting analysis results into
the specific numbers that appear on the page.

```python
def extract_page_numbers(eda_results, model_results, cluster_results):
    """
    Extracts all numbers needed for every visual element on the page.
    Returns a flat dict of named values ready for template injection.
    """
    return {
        # Hero stats (4-5 big numbers at top)
        'TOTAL_RECORDS': f"{eda_results['total_records']:,}",
        'DATE_RANGE': eda_results['date_range'],
        'TREND_PCT_CHANGE': f"{abs(eda_results['trend_pct_change'])}%",
        'TREND_DIRECTION': 'increase' if eda_results['trend_pct_change'] > 0 else 'decrease',
        'BEST_R2': f"{model_results['best_r2']*100:.1f}%",

        # Trend chart
        'TREND_X': eda_results['trend_x'],
        'TREND_Y': eda_results['trend_y'],
        'TREND_PEAK_YEAR': eda_results['trend_peak_year'],
        'TREND_PEAK_COUNT': f"{eda_results['trend_peak_count']:,}",

        # Ranking chart
        'RANKING_NAMES': eda_results['top_groups_names'],
        'RANKING_COUNTS': eda_results['top_groups_counts'],
        'TOP_NAME': eda_results['top_group_name'],
        'TOP_COUNT': f"{eda_results['top_group_count']:,}",

        # Target distribution
        'TARGET_LABELS': eda_results['target_dist_labels'],
        'TARGET_COUNTS': eda_results['target_dist_counts'],
        'MAJORITY_PCT': f"{eda_results['target_majority_pct']}%",
        'MAJORITY_LABEL': eda_results['target_majority_label'],

        # Model cards
        'MODEL_NAMES': list(model_results['models'].keys()),
        'MODEL_R2S': [v['r2'] for v in model_results['models'].values()],
        'MODEL_RMSES': [v['rmse'] for v in model_results['models'].values()],
        'BEST_MODEL': model_results['best_model'],
        'BEST_R2_RAW': model_results['best_r2'],
        'TOP_FEATURE': model_results['top_feature'],
        'TOP_FEATURE_PCT': f"{model_results['top_feature_pct']}%",
        'LASSO_ELIMINATED': ', '.join(model_results['lasso_eliminated']),

        # Feature importance chart
        'FEAT_NAMES': [f['feature'] for f in model_results['feature_importance']],
        'FEAT_IMPORTANCE': [f['importance'] for f in model_results['feature_importance']],

        # Clustering
        'OPTIMAL_K': cluster_results['optimal_k'],
        'ELBOW_K': cluster_results['elbow_k'],
        'ELBOW_INERTIAS': cluster_results['elbow_inertias'],
        'PCA_VARIANCE_1': cluster_results['pca_variance'][0],
        'PCA_VARIANCE_2': cluster_results['pca_variance'][1],
        'PCA_TOTAL': cluster_results['pca_total_variance'],
        'CLUSTER_SIZES': list(cluster_results['cluster_sizes'].values()),
        'CLUSTER_PROFILES': cluster_results['cluster_profiles'],
    }
```

---

## Phase 6 — Chart Specifications

### Every Chart Type — Exact Plotly.js Specification

Each chart is defined by its data arrays and a Plotly.js call.
The chart data is hardcoded JavaScript derived from Phase 5.

#### Chart 1: Trend Line (Change Over Time)
```javascript
// Data from: eda_results['trend_x'], eda_results['trend_y']
Plotly.newPlot('chart-trend', [{
    x: {{TREND_X}},
    y: {{TREND_Y}},
    type: 'scatter',
    mode: 'lines+markers',
    line: { color: RED, width: 2.5 },
    marker: { color: RED, size: 4 },
    fill: 'tozeroy',
    fillcolor: 'rgba(181,39,31,0.06)',
    hovertemplate: '<b>%{x}</b><br>%{y:,}<extra></extra>'
}], plotlyLayout(), config);
```

#### Chart 2: Horizontal Bar — Rankings
```javascript
// Data from: eda_results['top_groups_names'], eda_results['top_groups_counts']
// Highlight rule: color specific bars differently (e.g. local city, top performer)
Plotly.newPlot('chart-ranking', [{
    x: {{RANKING_COUNTS}}.reverse(),
    y: {{RANKING_NAMES}}.reverse(),
    type: 'bar',
    orientation: 'h',
    marker: {
        color: {{RANKING_NAMES}}.reverse().map(
            n => n.includes('{{HIGHLIGHT_NAME}}') ? GOLD : RED
        )
    },
    hovertemplate: '<b>%{y}</b><br>%{x:,}<extra></extra>'
}], {...plotlyLayout(), margin: {t:10, b:40, l:160, r:20}}, config);
```

#### Chart 3: Donut/Pie — Distribution
```javascript
// Data from: eda_results['target_dist_labels'], eda_results['target_dist_counts']
Plotly.newPlot('chart-dist', [{
    labels: {{TARGET_LABELS}},
    values: {{TARGET_COUNTS}},
    type: 'pie',
    hole: 0.5,
    marker: { colors: [RED, DARK_RED, DARKER_RED, GOLD, MUTED] },
    textinfo: 'label+percent',
    insidetextorientation: 'radial'
}], {...plotlyLayout(), showlegend: false}, config);
```

#### Chart 4: Bar with Log Scale — Skewed Distributions
```javascript
// Use when one category dominates (e.g. 89% no damage, tiny % destroyed)
Plotly.newPlot('chart-damage', [{
    x: {{TARGET_LABELS}},
    y: {{TARGET_COUNTS}},
    type: 'bar',
    marker: {
        color: {{TARGET_COUNTS}}.map(
            (v, i) => `rgba(181,39,31,${0.2 + (i / {{TARGET_COUNTS}}.length) * 0.8})`
        )
    }
}], {
    ...plotlyLayout(),
    yaxis: { ...plotlyLayout().yaxis, type: 'log', tickformat: ',d' }
}, config);
```

#### Chart 5: Feature Importance — Horizontal Bar
```javascript
// Data from: model_results['feature_importance']
// Color rule: top feature = RED, 2nd tier = GOLD, rest = MUTED
const importance = {{FEAT_IMPORTANCE}};
const maxImp = Math.max(...importance);

Plotly.newPlot('chart-features', [{
    x: importance.slice().reverse(),
    y: {{FEAT_NAMES}}.slice().reverse(),
    type: 'bar',
    orientation: 'h',
    marker: {
        color: importance.slice().reverse().map(v =>
            v > maxImp * 0.5 ? RED :
            v > maxImp * 0.1 ? GOLD : MUTED
        )
    },
    hovertemplate: '<b>%{y}</b><br>%{x:.3f}<extra></extra>'
}], {...plotlyLayout(), margin: {t:10, b:40, l:150, r:20}}, config);
```

#### Chart 6: Lasso Coefficients — Diverging Bar
```javascript
// Positive = increases target, Negative = decreases target
const coefs = {{LASSO_COEFS}};
Plotly.newPlot('chart-lasso', [{
    x: coefs,
    y: {{LASSO_FEATURES}},
    type: 'bar',
    orientation: 'h',
    marker: { color: coefs.map(v => v > 0 ? RED : TEAL) },
    hovertemplate: '<b>%{y}</b><br>Coefficient: %{x:.4f}<extra></extra>'
}], {
    ...plotlyLayout(),
    shapes: [{
        type: 'line', x0: 0, x1: 0, y0: -0.5, y1: {{N_FEATURES}} - 0.5,
        line: { color: MUTED, width: 1, dash: 'dot' }
    }]
}, config);
```

#### Chart 7: Model Comparison — Grouped Bar
```javascript
// Show R² for each model, highlight best
const r2s = {{MODEL_R2S}};
const bestR2 = Math.max(...r2s);
Plotly.newPlot('chart-models', [{
    x: {{MODEL_NAMES}},
    y: r2s,
    type: 'bar',
    marker: { color: r2s.map(v => v === bestR2 ? RED : GOLD) }
}], {
    ...plotlyLayout(),
    yaxis: {
        ...plotlyLayout().yaxis,
        range: [Math.min(...r2s) - 0.02, Math.max(...r2s) + 0.02]
    }
}, config);
```

#### Chart 8: PCA Cluster Scatter
```javascript
// Data from: cluster_results['pca_x'], pca_y, pca_labels
const clusterColors = ['#b5271f', '#9a7c2e', '#2a6496', '#2a9d8f'];
const clusterNames = {{CLUSTER_NAMES}};  // From Ollama
const k = {{OPTIMAL_K}};

const traces = Array.from({length: k}, (_, i) => {
    const mask = {{PCA_LABELS}}.map((l, idx) => l === i ? idx : -1).filter(x => x >= 0);
    return {
        x: mask.map(idx => {{PCA_X}}[idx]),
        y: mask.map(idx => {{PCA_Y}}[idx]),
        type: 'scatter', mode: 'markers',
        name: clusterNames[i],
        marker: { color: clusterColors[i], size: 4, opacity: 0.65 }
    };
});

Plotly.newPlot('chart-clusters', traces, {
    ...plotlyLayout(),
    showlegend: true,
    xaxis: { ...plotlyLayout().xaxis,
        title: { text: `PC1 ({{PCA_V1}}% variance)`, font: {size:10} }
    },
    yaxis: { ...plotlyLayout().yaxis,
        title: { text: `PC2 ({{PCA_V2}}% variance)`, font: {size:10} }
    }
}, config);
```

#### Chart 9: Elbow Curve
```javascript
Plotly.newPlot('chart-elbow', [{
    x: {{ELBOW_K}},
    y: {{ELBOW_INERTIAS}},
    type: 'scatter', mode: 'lines+markers',
    line: { color: RED, width: 2.5 },
    marker: {
        color: {{ELBOW_K}}.map(k => k === {{OPTIMAL_K}} ? GOLD : RED),
        size: {{ELBOW_K}}.map(k => k === {{OPTIMAL_K}} ? 12 : 6)
    }
}], {
    ...plotlyLayout(),
    shapes: [{
        type: 'line',
        x0: {{OPTIMAL_K}}, x1: {{OPTIMAL_K}},
        y0: 0, y1: Math.max(...{{ELBOW_INERTIAS}}),
        line: { color: GOLD, width: 1.5, dash: 'dot' }
    }],
    annotations: [{
        x: {{OPTIMAL_K}}, y: {{ELBOW_INERTIAS}}[{{OPTIMAL_K}} - {{ELBOW_K}}[0]],
        text: `  ← K={{OPTIMAL_K}} optimal`,
        font: { color: GOLD, size: 10 }, showarrow: false
    }]
}, config);
```

---

## Phase 7 — Non-Chart Visual Elements

### Exact HTML for Every Repeating Component

#### Big Number Stat Box (3-column grid)
```html
<!-- Data: any scalar number from Phase 5 -->
<div class="stat-row">
  <div class="stat-cell">
    <div class="stat-big">{{NUMBER}}<span class="stat-unit">{{UNIT}}</span></div>
    <div class="stat-label">{{SHORT_LABEL}}</div>
    <div class="stat-context">{{ONE_SENTENCE_CONTEXT}}</div>
  </div>
  <!-- repeat for each stat -->
</div>
```

#### Model Comparison Cards (4-column grid)
```html
<!-- Data: model_results['models'] dict -->
<div class="model-grid">
  <div class="model-card {{#if best}}best{{/if}}">
    <div class="model-name">{{MODEL_NAME}}</div>
    <div class="metric-label">R² Score</div>
    <div class="metric-value {{#if best}}highlight{{/if}}">{{R2}}</div>
    <div class="metric-bar">
      <div class="metric-fill" style="width:{{R2_PCT}}%"></div>
    </div>
    <div class="metric-label">RMSE</div>
    <div class="metric-value">{{RMSE}}</div>
  </div>
</div>
```

#### Cluster Cards (4-column grid)
```html
<!-- Data: cluster_results + Ollama names/descriptions -->
<!-- border-color cycles: red, gold, blue, teal -->
<div class="cluster-grid">
  <div class="cluster-card" style="border-left-color:{{COLOR}}">
    <div class="cluster-size">{{SIZE}} records · {{PCT}}% of total</div>
    <div class="cluster-name">{{OLLAMA_NAME}}</div>
    <div class="cluster-desc">{{OLLAMA_DESCRIPTION}}</div>
  </div>
</div>
```

#### Pull Quote
```html
<!-- Source: most counterintuitive finding from Ollama -->
<div class="pull-quote">
  <p>"{{SURPRISING_FINDING_AS_SENTENCE}}"</p>
  <cite>— RecordsReveal Analysis · {{DATASET_NAME}} {{YEAR}}</cite>
</div>
```

#### Fact Box
```html
<!-- Source: secondary finding that needs context -->
<div class="fact-box">
  <div class="fact-box-label">{{SHORT_LABEL}}</div>
  <p>{{2_3_SENTENCES_OF_CONTEXT}}</p>
</div>
```

#### Ranking Table with Progress Bars
```html
<!-- Data: eda_results['top_groups'], highlight specific rows -->
<table class="ranking-table">
  <thead>
    <tr>
      <th>#</th><th>Name</th><th>State</th>
      <th>Count</th><th>Volume</th>
    </tr>
  </thead>
  <tbody>
    <!-- For each item in top 15: -->
    <tr class="{{#if highlight}}highlight-row{{/if}}">
      <td class="rank-num">{{RANK}}</td>
      <td>{{NAME}}</td>
      <td>{{STATE_OR_CATEGORY}}</td>
      <td>{{COUNT}}</td>
      <td>
        <div class="rank-bar-bg">
          <div class="rank-bar" style="width:{{PCT_OF_MAX}}%"></div>
        </div>
      </td>
    </tr>
  </tbody>
</table>
```

#### "4 More Things" Finding Cards (2×2 grid)
```html
<!-- Source: findings 5-8 from Ollama, alternating accent/hot styles -->
<div class="finding-grid">
  <div class="finding-card {{hot|accent}}">
    <div class="finding-num">{{05|06|07|08}}</div>
    <div class="finding-title">{{HEADLINE}}</div>
    <div class="finding-desc">{{2_3_SENTENCES}}</div>
  </div>
</div>
```

---

## Phase 8 — Story Writing Template

### Section Structure (use for every section)
```
[KICKER]     9px red uppercase — category label e.g. "Finding #1"
[HEADLINE]   Serif bold — surprising finding as declarative statement
[SUBHEADING] 80% gray italic — dataset source + record count
[LEDE]       1.1rem — hook paragraph, sets up the tension
[BODY]       0.98rem — 2-3 paragraphs explaining the finding
[VISUAL]     Chart or stat boxes
[CALLOUT]    Pull quote or fact box with secondary finding
```

### Headline Formulas
```
Formula A: "[Specific number] [surprising implication]."
  → "Horror films return 1,001% ROI. Action films return 188%."

Formula B: "The [superlative] [thing] for [topic] is [surprising answer]."
  → "The most dangerous moment of your flight is the last 3 minutes."

Formula C: "We [analyzed/ranked/found] [N] [things]. [Counterintuitive finding]."
  → "We analyzed 4,803 movies. Budget is not the top predictor of success."

Formula D: "[Topic] has a [hidden property]. [Data] reveals it."
  → "Hollywood has a formula. 4,803 movies reveal it."
```

### Lede Formula
```
[Setup conventional assumption] → [Reveal data contradicts it] → [State finding]

Example:
"Every year, Hollywood spends billions making movies that flop.
Big budgets, famous directors, A-list stars — and somehow the film 
earns less than it cost. Meanwhile, a horror movie shot for $500,000 
grosses $50 million. What's going on? We found the answer in 4,803 films."
```

### Ask Ollama to Write Each Section
```python
def write_investigation_section(finding_number, data_result, topic):
    prompt = f"""
Write one section of an investigative data journalism article about {topic}.

Finding #{finding_number} data:
{data_result}

Write:
1. KICKER: 2-3 word category label (e.g. "Finding #{finding_number}")
2. HEADLINE: One punchy declarative sentence with specific numbers
3. LEDE: One paragraph (3-4 sentences) hooking the reader
4. BODY: Two paragraphs explaining the finding in plain English
5. PULL_QUOTE: One quotable sentence with a specific number

Rules:
- Write for curious general readers, not data scientists
- Use specific numbers, not vague descriptions
- Contradict conventional wisdom where possible
- No jargon (no "R²", "coefficient", "clustering")
"""
    return ask_ollama_write(prompt)
```

---

## Phase 9 — HTML Page Assembly

### Page Layout (Always the Same)
```
1. Site header + navigation
2. Ad slot — leaderboard (728x90)
3. Hero stats bar (4-5 key numbers, dark background)
4. Two-column layout:
   LEFT (main content, ~65%):
     a. Hero section — biggest finding + lede
     b. Section 1 — trend chart + story
     c. Ad slot — rectangle (336x280)
     d. Stat boxes row — 3 key numbers
     e. Section 2 — ranking chart + story
     f. Share bar
     g. Section 3 — distribution/phase chart + story
     h. Ad slot — rectangle
     i. Section 4 — ML finding + feature importance chart
     j. Section 5 — clustering + 4 archetype cards + PCA chart
     k. "4 more things" finding cards
     l. Share bar
     m. Methodology box
   RIGHT sidebar (~35%):
     - Ad slot (300x250)
     - Newsletter signup
     - Related investigations
     - Key numbers
     - Ad slot (300x250)
5. Footer
```

### CSS Design System (Copy Exactly)
```css
:root {
    /* Colors */
    --red: #b5271f;          /* Primary accent — headlines, bars */
    --red2: #d4302a;         /* Hover state */
    --gold: #9a7c2e;         /* Secondary accent — highlights */
    --ink: #1c1c1c;          /* Body text */
    --ink2: #4a4a4a;         /* Secondary text */
    --ink3: #888;            /* Muted text, labels */
    --paper: #f8f6f1;        /* Page background */
    --white: #ffffff;        /* Card backgrounds */
    --cream: #f0ece3;        /* Callout backgrounds */
    --border: #ddd9ce;       /* Dividers */
    --border2: #c8c3b5;      /* Stronger dividers */

    /* Plotly colors (JavaScript) */
    /* RED = '#b5271f' */
    /* GOLD = '#9a7c2e' */
    /* MUTED = 'rgba(181,39,31,0.4)' */
    /* TEAL = '#2a9d8f' */
    /* GRID = 'rgba(0,0,0,0.05)' */
}

/* Typography */
/* Headlines: Libre Baskerville (serif), 700 weight */
/* Body: Barlow (sans-serif), 400 weight */
/* Data labels: Barlow Condensed, 700 weight */
/* Article body: Libre Baskerville, 400 weight */
```

### Reusable Plotly Layout Function (JavaScript)
```javascript
const RED = '#b5271f', GOLD = '#9a7c2e', TEAL = '#2a9d8f';
const MUTED = 'rgba(181,39,31,0.4)', GRID = 'rgba(0,0,0,0.05)';

const plotlyLayout = (extra = {}) => ({
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Barlow, sans-serif', color: '#4a4a4a', size: 11 },
    margin: { t: 10, b: 50, l: 60, r: 20 },
    xaxis: { gridcolor: GRID, zerolinecolor: GRID, tickfont: { size: 10 } },
    yaxis: { gridcolor: GRID, zerolinecolor: GRID, tickfont: { size: 10 } },
    showlegend: false,
    ...extra
});

const config = { responsive: true, displayModeBar: false };
```

### AdSense Slots (4 required per page)
```html
<!-- Replace XXXXXXXXXX with real slot IDs from AdSense dashboard -->
<!-- Publisher ID: ca-pub-9045696717764033 -->

<!-- Top leaderboard 728x90 -->
<ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px"
     data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>

<!-- Mid-content rectangle 336x280 (×2) -->
<ins class="adsbygoogle" style="display:inline-block;width:336px;height:280px"
     data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>

<!-- Sidebar 300x250 (×2) -->
<ins class="adsbygoogle" style="display:inline-block;width:300px;height:250px"
     data-ad-client="ca-pub-9045696717764033" data-ad-slot="XXXXXXXXXX"></ins>

<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

### Social Share Buttons (Copy Exactly)
```html
<div class="share-bar">
    <span class="share-label">Share this story</span>
    <button class="share-btn x" onclick="shareX()">Post on X</button>
    <button class="share-btn fb" onclick="shareFB()">Share on Facebook</button>
    <button class="share-btn" onclick="copyLink()">Copy Link</button>
</div>

<script>
const SHARE_URL = encodeURIComponent(window.location.href);
const SHARE_TEXT = encodeURIComponent('{{VIRAL_HOOK_TEXT}}');

function shareX(){
    window.open(`https://twitter.com/intent/tweet?text=${SHARE_TEXT}&url=${SHARE_URL}`, '_blank');
}
function shareFB(){
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${SHARE_URL}`, '_blank');
}
function copyLink(){
    navigator.clipboard.writeText(window.location.href).then(() => {
        document.querySelectorAll('.share-btn').forEach(b => {
            if(b.textContent.includes('Copy')){
                b.textContent = 'Copied!';
                setTimeout(() => b.textContent = 'Copy Link', 2000);
            }
        });
    });
}
</script>
```

---

## Phase 10 — Deploy

### Full Deployment Checklist
```bash
# 1. Verify AdSense publisher ID is real (not placeholder)
grep "ca-pub-XXXX" investigations/your-investigation.html
# Should return nothing

# 2. Verify ads.txt exists
cat ~/Documents/Claude/Projects/recordsreveal-site/ads.txt
# Should show: google.com, pub-9045696717764033, DIRECT, f08c47fec0942fa0

# 3. Add investigation to homepage
# In index.html: add new story card in .story-grid section
# Change "Coming Soon" to live card with onclick and link
# Update date bar: X Investigations Published

# 4. Deploy
cd ~/Documents/Claude/Projects/recordsreveal-site
git add .
git commit -m "Add {{TOPIC}} investigation #00X"
git push origin main
# Cloudflare deploys in ~30 seconds

# 5. Verify live
curl -I https://recordsreveal.com/investigations/your-investigation.html
# Should return HTTP/2 200
```

### Social Media Launch Posts
```python
def generate_social_posts(findings, topic, url_slug):
    prompt = f"""
Write social media launch posts for a data investigation about {topic}.

Key findings:
{findings}

Write:
1. X POST (under 280 chars): shocking stat hook + link
2. FACEBOOK POST (150-200 words): personal/relatable angle, mention specific cities/states if relevant
3. REDDIT POST (r/dataisbeautiful format): bullet points with specific numbers, methodology mention

URL: recordsreveal.com/investigations/{url_slug}.html
"""
    return ask_ollama_write(prompt)
```

---

## Complete Pipeline Function

### Run Everything in One Call
```python
def build_investigation(csv_path, config):
    """
    config = {
        'topic': 'FAA Wildlife Strikes',
        'slug': 'bird-strikes',
        'investigation_number': '001',
        'target_col': 'DAMAGE_LEVEL',
        'target_encoding': {'N':0, 'M':1, 'M?':2, 'S':3, 'D':4},
        'date_col': 'INCIDENT_YEAR',
        'group_col': 'AIRPORT',
        'feature_cols': ['SIZE','AC_MASS','PHASE_OF_FLIGHT','INDICATED_DAMAGE',
                         'TIME_OF_DAY','TYPE_ENG','NUM_ENGS','AC_CLASS',
                         'INCIDENT_MONTH','STATE'],
        'cluster_features': ['SIZE','AC_MASS','PHASE_OF_FLIGHT',
                             'INDICATED_DAMAGE','NUM_ENGS'],
        'numeric_cols': ['HEIGHT','SPEED','NUM_ENGS'],
        'categorical_cols': ['PHASE_OF_FLIGHT','SIZE','AC_CLASS'],
        'highlight_group': 'HARTSFIELD',  # highlight in ranking chart
        'top_n': 15
    }
    """
    import json

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"  {len(df):,} rows, {df.shape[1]} columns")

    print("Running EDA...")
    eda = run_eda(df, config)

    print("Running regression...")
    models, _ = run_regression_pipeline(
        df, config['target_col'],
        config['feature_cols'],
        config.get('target_encoding')
    )

    print("Running clustering...")
    clusters, cluster_df = run_clustering_pipeline(
        df, config['cluster_features']
    )

    print("Extracting page numbers...")
    numbers = extract_page_numbers(eda, models, clusters)

    print("Asking Ollama for insights...")
    eda_insights = ask_ollama_eda_insights(eda, config['topic'])
    model_insights = ask_ollama_model_insights(models, config['topic'])
    cluster_names = ask_ollama_cluster_names(
        clusters, config['topic'], config['cluster_features']
    )

    print("Generating social posts...")
    social = generate_social_posts(
        eda_insights, config['topic'], config['slug']
    )

    # Save everything
    output = {
        'config': config,
        'numbers': numbers,
        'eda_insights': eda_insights,
        'model_insights': model_insights,
        'cluster_names': cluster_names,
        'social_posts': social
    }

    with open(f"{config['slug']}_analysis.json", 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nDone! Results saved to {config['slug']}_analysis.json")
    print(f"Best model: {models['best_model']} R²={models['best_r2']:.4f}")
    print(f"Optimal clusters: K={clusters['optimal_k']}")

    return output
```

---

## Quick Reference

### Key Numbers for the Homepage Update
When adding a new investigation to `index.html`, update:
1. Date bar: `X Investigations Published · Y In Progress`
2. Stat strip: `X` in "Investigations Live" item
3. Coming Soon count: decrement by 1
4. Story grid: change the investigation card from `.coming-soon` to live
5. Sidebar: add new "Live Now" item at top of Top Stories

### File Naming Convention
```
investigations/bird-strikes.html      ← consumer article
investigations/bird-strikes-data.html ← technical deep dive (optional)
investigations/hollywood.html
investigations/car-crashes.html
investigations/food-nutrition.html
```

### AdSense Notes
- Apply at adsense.google.com once site has 3+ pages of content
- Approval takes 1-7 days
- Replace `data-ad-slot="XXXXXXXXXX"` with real slot IDs once approved
- Each ad unit needs its own unique slot ID
- `ads.txt` must exist at root domain

### Ollama Model Selection
| Task | Model | Why |
|---|---|---|
| Python code generation | `qwen2.5-coder:7b` | Trained specifically on code |
| Plain English writing | `llama3.2` | Better at natural language |
| Cluster interpretation | `llama3.2` | Needs creative naming ability |
| Quick analysis questions | `qwen2.5-coder:7b` | Faster for short responses |
