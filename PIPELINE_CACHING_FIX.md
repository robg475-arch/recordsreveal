# Pipeline Caching Bug - Fixed

## The Problem

When running the pipeline on **campaign finance data**, the generated article was about **police use of force** instead. Why?

### What Happened

```
Run 1: Police Data
├── categorical_insights.json ✅ (force_type: Hands-On, Taser, etc.)
├── classification_insights.json ✅ (severity levels)
├── clustering_insights.json ✅
├── geographic_insights.json ✅ (lat/lon of incidents)
└── temporal_insights.json ✅ (timestamps)

Run 2: Campaign Finance Data
├── categorical_insights.json ❌ SKIPPED (no valid categorical column)
├── classification_insights.json ❌ SKIPPED (no target column)
├── clustering_insights.json ✅ (NEW - spending patterns)
├── geographic_insights.json ❌ SKIPPED (no lat/lon)
└── temporal_insights.json ✅ (NEW - but no actual date data)

Merge Step: Combined insights
├── Read categorical_insights.json → OLD POLICE DATA!
├── Read classification_insights.json → OLD POLICE DATA!
├── Read clustering_insights.json → ✅ Campaign finance
├── Read geographic_insights.json → OLD POLICE DATA!
└── Read temporal_insights.json → ✅ Campaign finance

Result: Article mixes campaign finance + old police data!
```

### Root Cause

The campaign finance dataset has:
- ✅ Numeric columns → clustering works
- ❌ NO categorical column (pipeline excludes "state" as geographic)
- ❌ NO classification target
- ❌ NO lat/lon coordinates
- ❌ NO actual date/time data

So 3 of the 5 analyses were **SKIPPED**, leaving old files from the police run sitting in `pipeline_output/`.

The merge step picked up those old files and combined them with the new data!

## The Solution

### Step 1.5: Surgical Cleanup

**AFTER profiling, BEFORE running analyses, delete the 5 insight files:**

```bash
# STEP 1: Profile Dataset
python3 profile.py "$CSV_FILE" "$OUTPUT_DIR"
# Creates: profile.json, recommendations.json

# STEP 1.5: Clean Old Analysis Files (NEW!)
rm -f "$OUTPUT_DIR/categorical_insights.json"
rm -f "$OUTPUT_DIR/classification_insights.json"
rm -f "$OUTPUT_DIR/clustering_insights.json"
rm -f "$OUTPUT_DIR/geographic_insights.json"
rm -f "$OUTPUT_DIR/temporal_insights.json"

# STEP 2: Run Analyses
# Only creates files for analyses that actually run

# STEP 3: Merge Insights
# Only merges files that EXIST from THIS run
```

### Why This Works

**Before:**
```
pipeline_output/
├── profile.json (run 2)
├── recommendations.json (run 2)
├── categorical_insights.json (run 1 - STALE!)
├── clustering_insights.json (run 2)
└── temporal_insights.json (run 2)

Merge finds 3 files → combines stale + fresh data ❌
```

**After:**
```
Step 1: Profile
pipeline_output/
├── profile.json ✅
└── recommendations.json ✅

Step 1.5: Clean
pipeline_output/
├── profile.json ✅
└── recommendations.json ✅
(all 5 insight files deleted)

Step 2: Run Analyses
pipeline_output/
├── profile.json ✅
├── recommendations.json ✅
├── clustering_insights.json ✅ (NEW)
└── temporal_insights.json ✅ (NEW)
(categorical, classification, geographic NOT created = skipped)

Step 3: Merge
Merges only: clustering + temporal ✅
```

## Benefits

1. **Surgical, not destructive** - Keeps profile.json and recommendations.json
2. **Blank = skipped, not error** - Missing files are expected and OK
3. **Prevents pollution** - Old data can't contaminate new runs
4. **Self-documenting** - If 5 files exist after merge, all 5 analyses ran

## Additional Fix: Dataset Name

Also fixed `merge_insights.py` to read dataset name from `profile.json` instead of from individual insight files:

```python
# OLD: Read from first insight file found
if not combined["dataset"] and "dataset" in data:
    combined["dataset"] = data["dataset"]  # Could be stale!

# NEW: Read from profile.json (single source of truth)
profile_path = os.path.join(output_dir, "profile.json")
if os.path.exists(profile_path):
    dataset_name = profile_data.get("dataset")  # Always correct
```

## Testing

Run the pipeline twice with different datasets:

```bash
# Run 1: Police data
bash run_full_pipeline.sh pipeline_police/police_use_of_force_data.csv

# Run 2: Campaign finance
bash run_full_pipeline.sh data/campaign_finance/dark_money_swing_districts_2024.csv

# Verify: Article should be about CAMPAIGN FINANCE, not police!
```

## Commits

- `cc098b0` - Fix merge_insights to use profile.json dataset name
- `f5a3f5c` - First attempt: Delete entire output directory (too aggressive)
- `924121d` - **Better fix: Clean only the 5 analysis insight files** ✅

## Files Modified

- `merge_insights.py` - Use profile.json for dataset name
- `run_full_pipeline.sh` - Added Step 1.5 cleanup

## Result

✅ **Pipeline now handles datasets with missing analysis types correctly**  
✅ **No more stale data contamination**  
✅ **Each run is truly independent**
