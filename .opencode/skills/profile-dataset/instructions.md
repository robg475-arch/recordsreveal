# Profile Dataset Skill

## Purpose
Quickly profile a CSV dataset and recommend which analysis skills to run next.

This is the **FIRST STEP** in the modular RecordsReveal analysis pipeline.

## What It Does

1. **Loads and profiles the CSV**
   - Counts rows and columns
   - Identifies column data types (numeric, text, dates)
   - Detects missing values
   - Calculates basic statistics

2. **Detects patterns**
   - Temporal columns (dates, times)
   - Geographic columns (lat/lon, addresses, zip codes)
   - Categorical columns (text with limited unique values)
   - Numeric columns (continuous values)

3. **Recommends analysis skills**
   - Based on detected patterns, suggests which analysis skills to run
   - Provides example commands
   - Estimates time and cost for each analysis

## Usage

```bash
# Profile a dataset
python .opencode/skills/profile-dataset/profile.py data.csv

# Custom output directory
python .opencode/skills/profile-dataset/profile.py data.csv my_results
```

## Outputs

### `profile.json`
Complete dataset profile with:
- Shape (rows × columns)
- Column names and types
- Missing value counts
- Basic statistics (min, max, mean, etc.)
- Detected patterns

### `recommendations.json`
Actionable recommendations:
```json
{
  "recommended_skills": [
    {
      "skill": "temporal-analysis",
      "reason": "Found 2 datetime columns: CRASH_DATE, CRASH_TIME",
      "command": "python temporal-analysis/analyze.py data.csv CRASH_TIME",
      "estimated_time": "30 seconds",
      "cost": "$0.00 (Ollama)"
    },
    {
      "skill": "geographic-analysis",
      "reason": "Found coordinate columns: LATITUDE, LONGITUDE",
      "command": "python geographic-analysis/analyze.py data.csv LATITUDE LONGITUDE",
      "estimated_time": "45 seconds",
      "cost": "$0.00 (Ollama)"
    }
  ]
}
```

## Example Workflow

```bash
# Step 1: Profile the dataset
$ python profile-dataset/profile.py crashes.csv

OUTPUT:
  📊 Dataset: 5,000 rows × 16 columns
  ✓ Found temporal patterns → recommend temporal-analysis
  ✓ Found geographic patterns → recommend geographic-analysis
  ✓ Found 9 categories → recommend classification-analysis
  
  Recommendations saved to: analysis_results/recommendations.json

# Step 2: Read recommendations
$ cat analysis_results/recommendations.json

# Step 3: Run recommended analyses
$ python temporal-analysis/analyze.py crashes.csv CRASH_TIME
$ python geographic-analysis/analyze.py crashes.csv LATITUDE LONGITUDE
```

## Detection Logic

### Temporal Columns
Detected if column name contains:
- `date`, `time`, `year`, `month`, `day`
- `hour`, `minute`, `timestamp`

OR if values parse as dates/times.

### Geographic Columns
Detected if column name contains:
- `lat`, `lon`, `latitude`, `longitude`
- `address`, `city`, `state`, `zip`, `postal`
- `location`, `place`, `borough`

### Categorical Columns
Detected if:
- Text column with < 50 unique values
- OR column with repeated values

### Numeric Columns
Detected if:
- Column dtype is int or float
- Contains numeric values

## Recommendations Generated

| Pattern Detected | Skill Recommended |
|-----------------|-------------------|
| Temporal columns | `temporal-analysis` |
| Geographic columns | `geographic-analysis` |
| Categorical + target | `classification-analysis` |
| Large dataset (1K+ rows) | `clustering-analysis` |
| Categorical columns | `categorical-analysis` |

## Speed
- **Very fast**: 2-5 seconds for most datasets
- No ML training
- No Ollama calls
- Just reads CSV and profiles structure

## Next Steps
After profiling, run the recommended analysis skills:
1. `temporal-analysis` - Time-based patterns
2. `geographic-analysis` - Location-based patterns
3. `classification-analysis` - ML predictions
4. `clustering-analysis` - Find hidden groups
5. `categorical-analysis` - Category breakdowns
