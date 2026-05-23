# Enhanced Domain-Specific Visualizations

**Generated:** May 20, 2026  
**Dataset:** 1,000 sample crash records  
**Target:** NUMBER OF PERSONS INJURED

---

## 📊 Generated Charts

### 1. **hourly_pattern.html**
**What it shows:** Crash patterns by hour of day (0-23)
- **Dual-axis chart:**
  - Orange bars: Total injuries per hour
  - Black line: Crash frequency per hour
- **Insight:** Shows 5:00 PM (17:00) peak in both injuries and frequency
- **Like your manual chart:** Matches the "chart-hourly" from car-crashes.html

---

### 2. **day_of_week.html**
**What it shows:** Crash totals by day of week
- **Bar chart** with peak day highlighted in orange
- **Insight:** Identifies which day has most crashes
- **Like your manual chart:** Matches the "chart-dow" showing Saturday peak

---

### 3. **geographic_breakdown.html**
**What it shows:** Crashes by borough/region
- **Horizontal bar chart** (easy to read long names)
- **Top 2 highlighted** in theme colors
- **Insight:** Brooklyn vs Queens vs Manhattan comparison
- **Like your manual chart:** Matches the "chart-borough" analysis

---

### 4. **category_breakdown_1.html**
**What it shows:** Top 10 contributing factors
- **Horizontal bar chart** for causes
- **Highlights** most common factors
- **Insight:** Driver inattention, failure to yield, etc.
- **Like your manual chart:** Matches the "chart-factors" analysis

---

### 5. **target_distribution.html**
**What it shows:** Distribution of injury counts
- **Histogram** showing how many crashes have 0, 1, 2, 3+ injuries
- **Insight:** Most crashes = 0-1 injured, rare to have 3+
- **Purpose:** Understand target variable distribution

---

### 6. **metric_comparison.html**
**What it shows:** Motorist vs Pedestrian vs Cyclist injuries
- **Side-by-side bar comparison**
- **Insight:** Which road user type gets injured most
- **Purpose:** Compare injury types for policy decisions

---

## 🎯 Key Improvements Over Generic ML Charts

| Generic ML Chart | Enhanced Domain Chart | Benefit |
|-----------------|----------------------|---------|
| Model comparison (R² scores) | Hourly crash patterns | Tells a story |
| Correlation heatmap | Geographic breakdown | Actionable insights |
| PCA cluster plot | Contributing factors | Policy implications |
| Elbow method | Day of week trends | Human-readable |
| Feature importance bars | Metric comparisons | Clear comparisons |

---

## ✅ Auto-Detection Success

The script **automatically detected**:
- ✅ `CRASH TIME` → Generated hourly pattern
- ✅ `CRASH DATE` → Generated day-of-week pattern
- ✅ `BOROUGH` → Generated geographic breakdown
- ✅ `CONTRIBUTING FACTOR` → Generated category breakdown
- ✅ Multiple injury columns → Generated metric comparison
- ✅ Target distribution → Always generated

**No manual configuration needed!**

---

## 🎨 Styling

All charts use:
- **Theme color:** `#d2691e` (RecordsReveal orange)
- **Accent color:** `#b5271f` (red for emphasis)
- **Faded bars:** `rgba(210, 105, 30, 0.4)` for non-highlighted items
- **Fixed dimensions:** 1000px width for consistency
- **Clean typography:** Matching RecordsReveal aesthetic

---

## 🚀 Next Steps

These visualizations will be **automatically generated** when you run:

```bash
python3 analyze_v2.py dataset.csv "TARGET_COLUMN"
```

The HTML builder will **automatically embed** them into your investigation pages.

**No more manual chart creation needed!**
