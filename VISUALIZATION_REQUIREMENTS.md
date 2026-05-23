# RecordsReveal Visualization Requirements
## Based on INVESTIGATION_PLAYBOOK.md Phases 5, 6, 7

---

## Overview

Our current modular pipeline creates `combined_insights.json` but we need to:
1. **Extract publishable numbers** (Phase 5)
2. **Generate chart specifications** (Phase 6)
3. **Create visual components** (Phase 7)

---

## Current Gap Analysis

### ✅ What We Have (from temporal + geographic analysis)

**temporal_insights.json:**
```json
{
  "patterns": {
    "hourly": {
      "distribution": {0: 113, 1: 45, ..., 17: 608},
      "peak_hour": 17,
      "peak_count": 608
    },
    "day_of_week": {
      "distribution": {"Monday": 800, ...},
      "busiest_day": "Wednesday"
    },
    "monthly": {
      "distribution": {"Jan": 400, ...},
      "busiest_month": "May"
    }
  }
}
```

**geographic_insights.json:**
```json
{
  "patterns": {
    "hotspots": [
      {"lat": 40.60, "lon": -73.96, "count": 63, "percent": 1.3}
    ],
    "locations": {
      "BOROUGH": {
        "top_10": {"Brooklyn": 1537, "Queens": 1244, ...}
      }
    }
  }
}
```

### ❌ What We're Missing

From INVESTIGATION_PLAYBOOK.md, we need these additional analyses and visualizations:

---

## Required Chart Types (Phase 6)

### Chart 1: Trend Line (Change Over Time) ⏳
**Status:** NOT COLLECTING THIS DATA YET  
**What it shows:** How crashes/events change over time (yearly, monthly)  
**Data needed:**
- `trend_x`: Array of time periods (e.g., [2020, 2021, 2022, 2023])
- `trend_y`: Array of counts for each period
- `trend_peak_year`: Year with most events
- `trend_peak_count`: Count at peak

**Where to get it:** Need to add to `temporal-analysis` skill
- Parse full dates (not just time)
- Group by year/month
- Calculate trend

**Chart type:** Line chart with fill

---

### Chart 2: Horizontal Bar — Rankings ✅
**Status:** HAVE THIS (from geographic analysis)  
**What it shows:** Top locations/categories ranked  
**Data we have:**
- `RANKING_NAMES`: ["Brooklyn", "Queens", "Manhattan", ...]
- `RANKING_COUNTS`: [1537, 1244, 915, ...]

**Chart type:** Horizontal bar (already specified in playbook)

---

### Chart 3: Donut/Pie — Distribution ⏳
**Status:** PARTIALLY HAVE (but need better structure)  
**What it shows:** Breakdown by category (e.g., vehicle types, injury severity)  
**Data needed:**
- `TARGET_LABELS`: Array of category names
- `TARGET_COUNTS`: Array of counts per category
- `MAJORITY_PCT`: Percentage of largest category
- `MAJORITY_LABEL`: Name of largest category

**Where to get it:** Need new `categorical-analysis` skill
- Analyze categorical columns
- Get distribution
- Identify majority

**Chart type:** Donut chart

---

### Chart 4: Bar with Log Scale ⏳
**Status:** NOT HAVE  
**What it shows:** Skewed distributions (e.g., 89% no damage, 11% destroyed)  
**Data needed:** Same as Chart 3 but rendered with log scale  
**Use case:** When one category dominates heavily

---

### Chart 5: Feature Importance — Horizontal Bar ⏳
**Status:** NOT HAVE (need classification analysis)  
**What it shows:** Which features matter most for predictions  
**Data needed:**
- `FEAT_NAMES`: ["hour", "borough", "vehicle_type", ...]
- `FEAT_IMPORTANCE`: [0.34, 0.28, 0.19, ...]
- `TOP_FEATURE`: "hour"
- `TOP_FEATURE_PCT`: "34%"

**Where to get it:** Need `classification-analysis` skill (not built yet)

**Chart type:** Horizontal bar with color coding

---

### Chart 6: Lasso Coefficients — Diverging Bar ⏳
**Status:** NOT HAVE  
**What it shows:** Positive/negative feature impacts  
**Data needed:**
- `LASSO_FEATURES`: ["age", "income", ...]
- `LASSO_COEFS`: [0.45, -0.23, ...]
- `LASSO_ELIMINATED`: Features set to zero

**Where to get it:** Classification skill with Lasso model

**Chart type:** Diverging horizontal bar

---

### Chart 7: Model Comparison — Grouped Bar ⏳
**Status:** NOT HAVE  
**What it shows:** R² scores for different ML models  
**Data needed:**
- `MODEL_NAMES`: ["Linear Reg", "Random Forest", "XGBoost"]
- `MODEL_R2S`: [0.72, 0.85, 0.87]
- `BEST_MODEL`: "XGBoost"

**Where to get it:** Classification skill

**Chart type:** Grouped bar chart

---

### Chart 8: PCA Cluster Scatter ⏳
**Status:** NOT HAVE  
**What it shows:** How clusters separate in 2D space  
**Data needed:**
- `PCA_X`: Array of PC1 coordinates
- `PCA_Y`: Array of PC2 coordinates
- `PCA_LABELS`: Cluster assignment for each point
- `CLUSTER_NAMES`: Ollama-generated names
- `PCA_V1`: Variance explained by PC1
- `PCA_V2`: Variance explained by PC2

**Where to get it:** Need `clustering-analysis` skill

**Chart type:** Scatter plot with color-coded clusters

---

### Chart 9: Elbow Curve ⏳
**Status:** NOT HAVE  
**What it shows:** Optimal number of clusters  
**Data needed:**
- `ELBOW_K`: [1, 2, 3, 4, 5, 6]
- `ELBOW_INERTIAS`: [15000, 8000, 4000, 2500, 2000, 1900]
- `OPTIMAL_K`: 4

**Where to get it:** Clustering skill

**Chart type:** Line chart with annotation

---

## Required Visual Components (Phase 7)

### Component 1: Big Number Stat Boxes ✅
**Status:** CAN EXTRACT FROM CURRENT DATA  
**What it shows:** 3-4 key statistics at top of page  
**Data we have:**
- Total records: 5,000
- Peak hour: 17:00 (608 crashes)
- Top location: Brooklyn (1,537 crashes, 30.7%)
- Date range: (need to add)

**HTML structure:** 3-column grid with large numbers

---

### Component 2: Model Comparison Cards ⏳
**Status:** NEED CLASSIFICATION SKILL  
**What it shows:** 4 cards showing model performance  
**Data needed:**
- Model name
- R² score
- RMSE
- Highlight best model

**HTML structure:** 4-column grid of cards

---

### Component 3: Cluster Cards ⏳
**Status:** NEED CLUSTERING SKILL  
**What it shows:** 4 cards describing each cluster  
**Data needed:**
- Cluster size
- Cluster percentage
- Ollama-generated name
- Ollama-generated description

**HTML structure:** 4-column grid with colored borders

---

### Component 4: Pull Quotes ✅
**Status:** HAVE (from Ollama insights)  
**What it shows:** Compelling quote from analysis  
**Data we have:**
- Temporal insight: "People's daily routines reveal secrets about our cities' rhythms"
- Geographic insight: "In the heart of Manhattan, a tiny pinpoint holds the key..."

**HTML structure:** Blockquote with citation

---

### Component 5: Ranking Tables ✅
**Status:** CAN BUILD FROM CURRENT DATA  
**What it shows:** Top 15 items with progress bars  
**Data we have:**
- Borough rankings with counts
- Can calculate percentages

**HTML structure:** Table with inline progress bars

---

## Action Plan: Data Collection Enhancement

### Priority 1: Enhance Existing Skills ⭐⭐⭐

#### 1A: Enhance `temporal-analysis` to collect trend data
```python
# Add to temporal_insights.json:
"patterns": {
  "trend_over_time": {
    "x": [2020, 2021, 2022, 2023],
    "y": [1000, 1200, 1400, 1600],
    "peak_period": "2023",
    "peak_count": 1600,
    "pct_change": "+60%"
  }
}
```

#### 1B: Enhance `geographic-analysis` to structure better
Already good! Just need to format for ranking table.

---

### Priority 2: Build Missing Skills ⭐⭐

#### 2A: Create `categorical-analysis` skill
**Purpose:** Analyze categorical columns for distributions  
**Output:** `categorical_insights.json`
```json
{
  "analysis_type": "categorical",
  "patterns": {
    "distributions": {
      "VEHICLE_TYPE": {
        "labels": ["Sedan", "SUV", "Taxi", ...],
        "counts": [1700, 1253, 624, ...],
        "majority_label": "Sedan",
        "majority_pct": 34.0
      }
    }
  }
}
```

#### 2B: Create `classification-analysis` skill
**Purpose:** Train ML models and get feature importance  
**Output:** `classification_insights.json`
```json
{
  "analysis_type": "classification",
  "patterns": {
    "models": {
      "Linear": {"r2": 0.72, "rmse": 0.45},
      "RandomForest": {"r2": 0.85, "rmse": 0.32},
      "XGBoost": {"r2": 0.87, "rmse": 0.29}
    },
    "best_model": "XGBoost",
    "feature_importance": [
      {"feature": "hour", "importance": 0.34},
      {"feature": "borough", "importance": 0.28}
    ],
    "lasso_coefficients": [...],
    "lasso_eliminated": [...]
  }
}
```

#### 2C: Create `clustering-analysis` skill
**Purpose:** K-Means clustering with PCA visualization  
**Output:** `clustering_insights.json`
```json
{
  "analysis_type": "clustering",
  "patterns": {
    "optimal_k": 4,
    "elbow": {
      "k_values": [1, 2, 3, 4, 5, 6],
      "inertias": [15000, 8000, 4000, 2500, 2000, 1900]
    },
    "pca": {
      "x": [...],
      "y": [...],
      "labels": [...],
      "variance_1": 45.2,
      "variance_2": 23.1
    },
    "cluster_sizes": [3616, 1362, 10, 12],
    "cluster_profiles": [...]
  },
  "ollama_insights": {
    "cluster_names": [
      "Rush Hour Pattern",
      "Weekend Crashes",
      "Late Night Incidents",
      "Outlier Group"
    ],
    "cluster_descriptions": [...]
  }
}
```

---

### Priority 3: Create Data Extraction Layer ⭐⭐⭐

#### Create `extract_page_numbers.py`
**Purpose:** Convert `combined_insights.json` into flat dict of template variables  
**Input:** `combined_insights.json`  
**Output:** `page_data.json`

```python
def extract_page_numbers(combined_insights):
    """
    Converts combined_insights.json into flat dict ready for HTML templates.
    Implements Phase 5 from INVESTIGATION_PLAYBOOK.md
    """
    temporal = combined_insights['all_patterns'].get('temporal', {})
    geographic = combined_insights['all_patterns'].get('geographic', {})
    categorical = combined_insights['all_patterns'].get('categorical', {})
    classification = combined_insights['all_patterns'].get('classification', {})
    clustering = combined_insights['all_patterns'].get('clustering', {})
    
    return {
        # Hero stats
        'TOTAL_RECORDS': f"{temporal.get('hourly', {}).get('total_records', 0):,}",
        'PEAK_HOUR': temporal.get('hourly', {}).get('peak_hour', 0),
        'PEAK_COUNT': f"{temporal.get('hourly', {}).get('peak_count', 0):,}",
        'TOP_LOCATION': list(geographic.get('locations', {}).get('BOROUGH', {}).get('top_10', {}).keys())[0],
        'TOP_LOCATION_COUNT': list(geographic.get('locations', {}).get('BOROUGH', {}).get('top_10', {}).values())[0],
        
        # Trend chart
        'TREND_X': temporal.get('trend_over_time', {}).get('x', []),
        'TREND_Y': temporal.get('trend_over_time', {}).get('y', []),
        
        # Ranking chart
        'RANKING_NAMES': list(geographic.get('locations', {}).get('BOROUGH', {}).get('top_10', {}).keys()),
        'RANKING_COUNTS': list(geographic.get('locations', {}).get('BOROUGH', {}).get('top_10', {}).values()),
        
        # Distribution chart
        'TARGET_LABELS': categorical.get('distributions', {}).get('VEHICLE_TYPE', {}).get('labels', []),
        'TARGET_COUNTS': categorical.get('distributions', {}).get('VEHICLE_TYPE', {}).get('counts', []),
        
        # Model comparison
        'MODEL_NAMES': list(classification.get('models', {}).keys()),
        'MODEL_R2S': [v['r2'] for v in classification.get('models', {}).values()],
        
        # Feature importance
        'FEAT_NAMES': [f['feature'] for f in classification.get('feature_importance', [])],
        'FEAT_IMPORTANCE': [f['importance'] for f in classification.get('feature_importance', [])],
        
        # Clustering
        'OPTIMAL_K': clustering.get('optimal_k', 0),
        'ELBOW_K': clustering.get('elbow', {}).get('k_values', []),
        'ELBOW_INERTIAS': clustering.get('elbow', {}).get('inertias', []),
        'PCA_X': clustering.get('pca', {}).get('x', []),
        'PCA_Y': clustering.get('pca', {}).get('y', []),
        'PCA_LABELS': clustering.get('pca', {}).get('labels', []),
        'CLUSTER_NAMES': clustering.get('cluster_names', []),
        
        # Pull quotes
        'TEMPORAL_QUOTE': combined_insights['all_ollama_insights'].get('temporal', ''),
        'GEOGRAPHIC_QUOTE': combined_insights['all_ollama_insights'].get('geographic', '')
    }
```

---

## Updated Skill Pipeline Architecture

```
CSV → profile-dataset → recommendations.json
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
  temporal-analysis                        geographic-analysis
  (ENHANCED: add trend)                    (already good)
        │                                           │
        │         categorical-analysis              │
        │         (NEW: distributions)              │
        │                 │                         │
        │         classification-analysis           │
        │         (NEW: ML + features)              │
        │                 │                         │
        │         clustering-analysis               │
        │         (NEW: K-means + PCA)              │
        │                 │                         │
        └─────────────────┴─────────────────────────┘
                          ↓
                 merge_insights.py
                          ↓
              combined_insights.json
                          ↓
              extract_page_numbers.py  ⭐ NEW
                          ↓
                  page_data.json
                          ↓
              write-investigation
                          ↓
              article_content.json
                          ↓
              build-html-page  ⭐ ENHANCED (use page_data.json for charts)
                          ↓
          investigation-XXX.html
          (with ALL 9 chart types + ALL visual components)
```

---

## Next Session Priorities

### Session 3 Goals:
1. ✅ Enhance `temporal-analysis` to add trend data
2. ✅ Create `categorical-analysis` skill
3. ✅ Create `extract_page_numbers.py` script
4. ✅ Test on crashes dataset

### Session 4 Goals:
5. ✅ Create `classification-analysis` skill
6. ✅ Create `clustering-analysis` skill
7. ✅ Update `build-html-page` to use all 9 chart types
8. ✅ Test full pipeline: CSV → published HTML with all visualizations

---

## Success Criteria

When complete, our `investigation-XXX.html` should have:

**Charts (9 total):**
- ✅ Hourly pattern line chart
- ✅ Borough ranking bar chart
- ⏳ Trend over time line chart
- ⏳ Category distribution donut
- ⏳ Feature importance bar
- ⏳ Model comparison bar
- ⏳ Lasso coefficients diverging bar
- ⏳ PCA cluster scatter
- ⏳ Elbow curve

**Visual Components:**
- ✅ 4 stat boxes at top
- ⏳ 4 model comparison cards
- ⏳ 4 cluster description cards
- ✅ 2-3 pull quotes
- ✅ Ranking table with progress bars
- ✅ Fact boxes

**Quality bar:** Match `car-crashes.html` manual investigation quality!
