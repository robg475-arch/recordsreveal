# Analyze Dataset Skill

## Purpose
Perform comprehensive data analysis for RecordsReveal investigations, combining:
- Exploratory Data Analysis (EDA)
- Machine Learning (Regression/Classification)
- Clustering (K-Means)
- AI-powered insights (via Ollama)

## Workflow

### Phase 1: Dataset Profiling
1. Load CSV file
2. Profile dataset characteristics:
   - Shape, columns, data types
   - Missing values
   - Detect temporal columns (dates/times)
   - Detect geographic columns (lat/lon, locations)
   - Detect categorical vs numeric columns
3. Print summary to user

### Phase 2: Exploratory Data Analysis (EDA)
1. Generate descriptive statistics
2. Identify correlations
3. Detect temporal patterns (hourly, daily, monthly)
4. Detect geographic patterns (if lat/lon present)
5. Identify top categories
6. **Ask Ollama**: "What's surprising or newsworthy in these patterns?"

### Phase 3: Machine Learning
1. Auto-detect problem type (regression vs classification)
2. Train multiple models:
   - Linear/Logistic Regression
   - Random Forest
   - XGBoost (if available)
3. Evaluate performance
4. Extract feature importance
5. **Ask Ollama**: "What do these predictions tell us about the data?"

### Phase 4: Clustering
1. Run K-Means clustering (k=3-5)
2. Profile each cluster
3. **Ask Ollama**: "Give each cluster a descriptive name based on its characteristics"

### Phase 5: Domain-Specific Visualizations
1. Call `enhance_visualizations.py` to generate:
   - Hourly patterns (if temporal data)
   - Day-of-week patterns (if temporal data)
   - Geographic breakdown (if location data)
   - Category breakdown (if categorical data)
   - Model comparison charts
2. Export charts as HTML and JSON

### Phase 6: Export Results
1. Compile all findings into `results.json`:
   - Dataset profile
   - EDA findings
   - ML results
   - Cluster profiles
   - AI insights
2. Export chart data to `chart_data.json` for inline rendering
3. Save visualizations to `analysis_results/`

## Usage

```bash
# From command line
python .opencode/skills/analyze-dataset/analyze.py path/to/data.csv

# From OpenCode
opencode skill:analyze-dataset data.csv
```

## Outputs

- `analysis_results/results.json` - Full analysis results
- `analysis_results/chart_data.json` - Chart data for HTML rendering
- `analysis_results/*.html` - Interactive visualizations
- Console output with AI insights

## Dependencies

- `analyze_v2.py` - Core ML analysis engine
- `enhance_visualizations.py` - Domain-specific charts
- `export_chart_data.py` - Chart data extraction
- `ollama_helper.py` - AI insights via Ollama

## Ollama Integration

The skill uses Ollama (free) for AI insights:

1. **EDA Insights** (llama3.2):
   - Identifies surprising patterns
   - Suggests follow-up questions
   - Highlights newsworthy findings

2. **Cluster Naming** (llama3.2):
   - Generates descriptive cluster names
   - Explains what makes each cluster unique

3. **Prediction Interpretation** (llama3.2):
   - Explains what ML models reveal
   - Identifies most important features
   - Suggests investigation angles

## Example Output

```
🔍 ANALYZING DATASET CHARACTERISTICS
====================================
Dataset: 5,000 rows × 29 columns
Temporal columns: CRASH DATE, CRASH TIME
Geographic columns: LATITUDE, LONGITUDE
Categorical columns: BOROUGH, CONTRIBUTING FACTOR

📊 EXPLORATORY DATA ANALYSIS
====================================
Peak hour: 5:00 PM (487 crashes)
Top borough: Brooklyn (1,234 crashes)
Most common factor: Driver Inattention/Distraction

🤖 OLLAMA INSIGHTS
====================================
"The spike at 5 PM is 3x higher than the morning rush,
suggesting evening fatigue may be a bigger factor than
congestion alone. Brooklyn's dominance isn't just about
population—it has 40% more crashes per capita than Queens."

🎯 MACHINE LEARNING RESULTS
====================================
Problem type: Classification (predicting injury severity)
Best model: XGBoost (accuracy: 0.87)
Top features: 
  1. VEHICLE_TYPE_CODE (importance: 0.34)
  2. HOUR (importance: 0.28)
  3. BOROUGH (importance: 0.19)

🧩 CLUSTERING RESULTS
====================================
Cluster 0: "Rush Hour Manhattan" (32% of crashes)
Cluster 1: "Weekend Brooklyn" (28% of crashes)
Cluster 2: "Late Night Outer Boroughs" (40% of crashes)

✅ ANALYSIS COMPLETE
Exported: results.json, chart_data.json, 11 visualizations
```

## Tips for Best Results

1. **Clean data first**: Remove empty rows, fix date formats
2. **Include temporal columns**: Name them with DATE/TIME keywords
3. **Include location columns**: Name them LAT/LON/LATITUDE/LONGITUDE
4. **Categorical columns**: Keep values consistent (e.g., "Brooklyn" not "brooklyn")
5. **Large datasets**: Works best with 1K-100K rows (samples if larger)

## Troubleshooting

**"Cannot connect to Ollama server"**
- Check if 192.168.1.153:11434 is accessible
- Run `python3 ollama_helper.py` to test connection

**"XGBoost not available"**
- Install: `pip install xgboost`
- Or skip: Analysis will use Random Forest instead

**"No visualizations generated"**
- Check if `enhance_visualizations.py` exists
- Verify dataset has temporal/geographic/categorical columns

**"Charts look wrong"**
- Regenerate with `export_chart_data.py`
- Check `chart_data.json` format
