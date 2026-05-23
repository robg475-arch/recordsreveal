# 📊 Analysis Examples

This folder contains example output from the **analyze_v2.py** script.

## 📁 What's Here

```
analysis_examples/
├── README.md                  (this file)
├── WHAT_YOU_GET.md           (detailed guide on using the outputs)
└── car-crashes-50k/          (example analysis of 50,000 NYC crashes)
    ├── results.json          (all metrics and findings)
    └── visualizations/       (interactive HTML charts)
        ├── correlation_heatmap.html
        ├── target_distribution.html
        ├── model_comparison.html
        ├── cluster_plot.html
        └── elbow_plot.html
```

---

## 🚀 Quick Start - View the Results

### **1. Open the Visualizations**

Double-click any HTML file in `car-crashes-50k/visualizations/` to open in your browser:

- **correlation_heatmap.html** - See which features are related
- **target_distribution.html** - Histogram of injury counts
- **model_comparison.html** - R² scores across all models
- **cluster_plot.html** - 4 crash types visualized in 2D
- **elbow_plot.html** - Why K=4 is optimal for clustering

### **2. Open results.json**

Open `car-crashes-50k/results.json` in any text editor to see:
- All model metrics (R², RMSE, MAE)
- Feature importance rankings
- Cluster profiles
- Dataset statistics

Or view it formatted:
```bash
cat analysis_examples/car-crashes-50k/results.json | python3 -m json.tool
```

---

## 📊 What This Example Shows

**Dataset:** 50,000 NYC motor vehicle crashes  
**Target:** NUMBER OF PERSONS INJURED (count variable 0-14)  
**Analysis Type:** Regression (auto-detected)

### Key Findings:

1. **Best Model:** Ridge Regression
   - R² = 0.9726 (excellent fit)
   - RMSE = 0.1302
   - MAE = 0.0317

2. **Top Predictors:**
   - Motorist injuries: 82.9%
   - Pedestrian injuries: 9.7%
   - Cyclist injuries: 7.0%

3. **Cluster Analysis:**
   - Cluster 0: Normal crashes (99.2%)
   - Cluster 1: High-severity outliers (0.1%)
   - Cluster 2: Multi-vehicle incidents (0.1%)
   - Cluster 3: Pedestrian strikes (0.5%)

4. **Model Comparison:**
   - Ridge Regression: 0.9726 (best)
   - Linear Regression: 0.9726
   - Random Forest: 0.9707
   - XGBoost: 0.9668
   - Lasso: 0.7778

---

## 💡 How to Use This for Your Investigation

### For Your Main Article:

**Extract key stats from results.json:**
```json
"best_model": "Ridge Regression"
"r2_score": 0.9726
"feature_importance": {
  "NUMBER OF MOTORIST INJURED": 0.8294
}
```

**Write your lede:**
> "Machine learning analysis of 50,000 NYC crashes reveals that motorist 
> injuries are by far the strongest predictor of total casualties, accounting 
> for 82.9% of the model's decision-making."

### For Your Technical Data Page:

**Embed the charts:**
- Copy the HTML from `model_comparison.html` into your page
- Or screenshot the visualizations

**Add the methodology:**
> "We trained five regression models on 40,000 samples and tested on 10,000. 
> Ridge Regression achieved the best performance with R²=0.9726, RMSE=0.1302, 
> and MAE=0.0317."

---

## 🎯 Comparing to Your Earlier Analysis

### Earlier Analysis (v1.0):
- Target: TOTAL_CASUALTIES (created variable)
- Features: Hour, day, borough, vehicle type, factor
- Result: R² = 0.0296 (very low - casualties unpredictable)

### This Analysis (v2.0):
- Target: NUMBER OF PERSONS INJURED
- Features: Includes other injury types (motorist, pedestrian, cyclist)
- Result: R² = 0.9726 (very high - highly predictable)

### Why Different?

**Earlier:** Tried to predict casualties from CRASH CHARACTERISTICS  
→ Hard! Crashes are random.

**This:** Predicts total injuries from INJURY SUBCATEGORIES  
→ Easy! It's basically addition (motorist + pedestrian + cyclist = total).

### The Real Story:

> "Machine learning can predict total injuries with 97% accuracy when you 
> already know the breakdown of WHO got hurt. But predicting casualties from 
> basic crash features? Nearly impossible (3% accuracy). This suggests that 
> severity is fundamentally unpredictable from time, location, and vehicle type 
> alone."

---

## 📂 File Details

### results.json (11 KB)
- Complete analysis results in JSON format
- All model metrics
- Feature importance rankings
- Cluster profiles
- Dataset statistics

### Visualizations (1.4 MB total)

| File | Size | Description |
|------|------|-------------|
| cluster_plot.html | 1.3 MB | 4 crash types in PCA space |
| target_distribution.html | 73 KB | Injury count histogram |
| correlation_heatmap.html | 12 KB | Feature relationships |
| model_comparison.html | 8 KB | R² comparison bar chart |
| elbow_plot.html | 8 KB | Optimal K selection |
| confusion_matrix.html | 8 KB | (not used for regression) |

---

## 🔧 How to Generate More Examples

Run the script on any dataset:

```bash
# From your project root
python3 analyze_v2.py path/to/dataset.csv "TARGET_COLUMN"

# Example: Full 2M crash dataset
python3 analyze_v2.py ~/Downloads/crashes.csv "NUMBER OF PERSONS INJURED"

# The results will be in: path/to/dataset/analysis_results/
```

---

## 📖 More Information

- **WHAT_YOU_GET.md** - Detailed guide on understanding the outputs
- **ANALYSIS_SCRIPT_README.md** (in project root) - Full script documentation
- **analyze_v2.py** (in project root) - The analysis script itself

---

## 🎉 Next Steps

1. ✅ **Open the HTML visualizations** to see what they look like
2. ✅ **Open results.json** to see the metrics
3. ✅ **Read WHAT_YOU_GET.md** for detailed explanations
4. ⏳ **Run analyze_v2.py on your next dataset** to generate new results

---

**This is what you get every time you run analyze_v2.py!** 🚀
