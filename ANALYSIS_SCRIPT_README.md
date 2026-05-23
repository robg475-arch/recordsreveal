# RecordsReveal Enhanced Analysis Script v2.0

## 🚀 What It Does

Automatically analyzes any tabular dataset and intelligently chooses the right machine learning approach:

- **Auto-detects data type** (regression vs classification)
- **Runs appropriate ML models** (Linear, Ridge, Lasso, Random Forest, XGBoost)
- **Creates visualizations** (correlation heatmaps, confusion matrices, cluster plots)
- **Exports everything as JSON** + interactive HTML charts

## ✨ Key Features

### 1. Intelligent Auto-Detection
```
✓ Regression (continuous targets like sales, temperature, casualties)
✓ Binary Classification (yes/no, true/false, 0/1)
✓ Multi-Class Classification (categories: A/B/C)
✓ Count Variables (0, 1, 2, 3... injuries, items, etc.)
✓ Time Series Columns (dates, timestamps)
✓ Geographic Columns (lat/long coordinates)
✓ Text Columns (reviews, descriptions)
```

### 2. Models Included

**Regression:**
- Linear Regression
- Ridge Regression (with regularization)
- Lasso Regression (with feature selection)
- Random Forest Regressor
- XGBoost Regressor

**Classification:**
- Logistic Regression
- Random Forest Classifier
- XGBoost Classifier

**Always:**
- K-Means Clustering (K=4)
- PCA Visualization

### 3. Visualizations Generated

- Correlation heatmap (feature relationships)
- Target distribution plot
- Model comparison charts
- Confusion matrix (classification only)
- Cluster visualization (PCA 2D)
- Elbow curve (optimal K selection)

### 4. Metrics Reported

**Regression:**
- R² Score (model fit quality)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Feature importance

**Classification:**
- Accuracy, Precision, Recall, F1-Score
- ROC-AUC (binary only)
- Confusion matrix
- Feature importance

## 📦 Installation

### Prerequisites

```bash
# Install required Python packages
pip3 install pandas numpy scikit-learn plotly xgboost

# For Mac users (XGBoost requires OpenMP)
brew install libomp
```

### Download Script

```bash
# Save analyze_v2.py to your project directory
cp analyze_v2.py ~/your-project/
chmod +x ~/your-project/analyze_v2.py
```

## 🎯 Usage

### Basic Usage (Auto-detect target)

```bash
python3 analyze_v2.py dataset.csv
```

The script will automatically find the most likely target variable by looking for columns named:
- `target`, `label`, `class`, `outcome`, `result`
- `casualties`, `revenue`, `price`, `damage`, `rating`, `score`
- `survived`, `churn`, `fraud`

### Specify Target Column

```bash
python3 analyze_v2.py dataset.csv "TOTAL_CASUALTIES"
```

### Real Examples

```bash
# NYC Car Crashes (regression - count variable)
python3 analyze_v2.py crashes.csv "NUMBER OF PERSONS INJURED"

# Hospital Readmissions (binary classification)
python3 analyze_v2.py hospital.csv "READMITTED_30_DAY"

# Movie Success (regression)
python3 analyze_v2.py movies.csv "REVENUE"

# Customer Churn (binary classification)
python3 analyze_v2.py customers.csv "CHURNED"
```

## 📊 Output Structure

```
your-dataset/
└── analysis_results/
    ├── results.json              # All metrics and findings
    └── visualizations/
        ├── correlation_heatmap.html
        ├── target_distribution.html
        ├── model_comparison.html (or confusion_matrix.html)
        ├── cluster_plot.html
        └── elbow_plot.html
```

### results.json Structure

```json
{
  "dataset": "crashes.csv",
  "profile": {
    "shape": [1000000, 29],
    "numeric_cols": [...],
    "categorical_cols": [...],
    "datetime_cols": [...],
    "target_type": "regression",
    "class_imbalance": null
  },
  "eda": {
    "basic_stats": {...},
    "correlations": {...}
  },
  "models": {
    "regression": {
      "Linear Regression": {
        "r2_score": 0.0296,
        "rmse": 0.5817,
        "mae": 0.3214,
        "feature_importance": {...}
      },
      ...
    },
    "best_model": "XGBoost"
  },
  "clustering": {
    "optimal_k": 4,
    "pca_variance_explained": {...},
    "cluster_sizes": {...}
  }
}
```

## 🔍 How Auto-Detection Works

### Regression Detection
```
✓ Many unique values (> 10)
✓ Float data type
✓ Count variables (0, 1, 2, 3...)
```

### Binary Classification Detection
```
✓ Exactly 2 unique values
✓ Boolean type
✓ Yes/No, True/False, 0/1
```

### Multi-Class Classification Detection
```
✓ Few unique values (< 10)
✓ String/object type (categories)
✓ Non-sequential integers (e.g., 1, 3, 7, 9)
```

## 🎨 Example Output

### Regression Example (NYC Crashes)

```
🎯 Target Variable: NUMBER OF PERSONS INJURED
   Unique values: 8
   Data type: int64
   ✓ Detected: REGRESSION (count variable: 8 values)

🤖 REGRESSION MODELS
   Training Linear Regression...
      R² = 0.0062, RMSE = 0.5891, MAE = 0.3214
   
   Training XGBoost...
      R² = 0.0296, RMSE = 0.5817, MAE = 0.3018
   
   🏆 Best Model: XGBoost (R² = 0.0296)
```

### Classification Example (Hospital Readmissions)

```
🎯 Target Variable: READMITTED_30_DAY
   Unique values: 2
   Data type: object
   ✓ Detected: BINARY CLASSIFICATION (2 categories)
   
   Class distribution:
      No: 8234 (89.2%)
      Yes: 998 (10.8%)
   ⚠️  Class imbalance detected (ratio: 8.3:1)

🤖 CLASSIFICATION MODELS
   Training Logistic Regression...
      Accuracy = 0.8912, Precision = 0.7234, 
      Recall = 0.6543, F1 = 0.6871, AUC = 0.8523
   
   Training XGBoost...
      Accuracy = 0.9234, Precision = 0.8012,
      Recall = 0.7345, F1 = 0.7662, AUC = 0.9101
   
   🏆 Best Model: XGBoost
```

## ⚙️ Customization

### Adjust K-Means Clusters

Edit line ~548:
```python
optimal_k = 4  # Change to 3, 5, 6, etc.
```

### Adjust Train/Test Split

Edit line ~278 (regression) or ~397 (classification):
```python
test_size=0.2  # Change to 0.3 for 70/30 split
```

### Add More Models

Add to the `models` dictionary in `run_regression_models()` or `run_classification_models()`:

```python
from sklearn.ensemble import GradientBoostingRegressor

models['Gradient Boosting'] = GradientBoostingRegressor(
    n_estimators=100, 
    max_depth=5, 
    random_state=42
)
```

## 🐛 Troubleshooting

### "XGBoost Library could not be loaded"

**Mac:**
```bash
brew install libomp
```

**Linux:**
```bash
sudo apt-get install libgomp1
```

### "No module named 'pandas'"

```bash
pip3 install pandas numpy scikit-learn plotly xgboost
```

### "Target column not found"

Make sure the column name matches exactly (case-sensitive):
```bash
# Check column names first
python3 -c "import pandas as pd; print(pd.read_csv('data.csv').columns.tolist())"

# Then use exact name
python3 analyze_v2.py data.csv "EXACT_COLUMN_NAME"
```

### "ValueError: The least populated class..."

This happens with extreme class imbalance. The script now handles this automatically with non-stratified splits.

## 📈 Best Practices

1. **Clean your data first** - Remove obvious junk rows, handle extreme outliers
2. **Use meaningful column names** - Helps auto-detection
3. **Specify target explicitly** - More reliable than auto-detect
4. **Check class balance** - Script warns you about imbalanced data
5. **Inspect results.json** - Verify detection was correct

## 🔮 Future Enhancements

Planned for v3.0:
- Time series forecasting (ARIMA, Prophet)
- Spatial analysis for lat/long data
- NLP/sentiment analysis for text columns
- SHAP values for model explainability
- Automated hyperparameter tuning
- Feature engineering suggestions

## 📝 Version History

### v2.0 (Current)
- ✅ Auto-detection of regression vs classification
- ✅ XGBoost models
- ✅ Classification metrics (ROC, confusion matrix)
- ✅ Correlation heatmaps
- ✅ Handles class imbalance
- ✅ Better feature importance
- ✅ JSON + HTML export

### v1.0 (Legacy)
- Basic regression only
- Manual feature selection
- Limited visualizations

## 📧 Support

For issues or questions:
1. Check this README
2. Review `results.json` for clues
3. Run with smaller sample first to test
4. Check that all dependencies are installed

---

**Happy Data Investigating! 🔍📊**
