#!/bin/bash
#
# RecordsReveal Full Pipeline
# CSV → Profile → Analyses → Merge → Extract → Write → Build HTML
#
# Features:
# - Google Analytics 4: G-7B3KBBGVWE (automatically included in all pages)
# - Google AdSense: ca-pub-9045696717764033 (automatically included in all pages)
# - Geocoding: Nominatim API for location names
# - Auto-updates: Homepage index.html updated with new investigations
#

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║             RECORDSREVEAL FULL PIPELINE                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: ./run_full_pipeline.sh <csv_file> [output_dir]"
    echo ""
    echo "Example:"
    echo "  ./run_full_pipeline.sh test_dataset_crashes.csv"
    echo ""
    exit 1
fi

CSV_FILE="$1"
OUTPUT_DIR="${2:-pipeline_output}"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Error: CSV file not found: $CSV_FILE"
    exit 1
fi

echo "📁 Input CSV: $CSV_FILE"
echo "📂 Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

TIMER_START=$(date +%s)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Profile Dataset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/profile-dataset/profile.py "$CSV_FILE" "$OUTPUT_DIR"

if [ ! -f "$OUTPUT_DIR/recommendations.json" ]; then
    echo "❌ Error: Profiling failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Run Recommended Analyses"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Read recommendations and extract analysis names
SKILL_COUNT=$(python3 -c "import json; print(len(json.load(open('$OUTPUT_DIR/recommendations.json'))['recommended_skills']))")
echo "Running $SKILL_COUNT analyses..."
echo ""

# Run each recommended skill
for i in $(seq 0 $((SKILL_COUNT - 1))); do
    SKILL_NAME=$(python3 -c "import json; print(json.load(open('$OUTPUT_DIR/recommendations.json'))['recommended_skills'][$i]['skill'])")
    
    echo "🔄 Running: $SKILL_NAME"
    
    case $SKILL_NAME in
        temporal-analysis)
            # Auto-detect temporal column
            TIME_COL=$(python3 -c "import pandas as pd; df = pd.read_csv('$CSV_FILE'); cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]; print(cols[0] if cols else '')")
            if [ -n "$TIME_COL" ]; then
                python3 .opencode/skills/temporal-analysis/analyze.py "$CSV_FILE" "$TIME_COL" "$OUTPUT_DIR"
            fi
            ;;
        geographic-analysis)
            # Auto-detect lat/lon columns
            LAT_COL=$(python3 -c "import pandas as pd; df = pd.read_csv('$CSV_FILE'); cols = [c for c in df.columns if 'lat' in c.lower()]; print(cols[0] if cols else '')")
            LON_COL=$(python3 -c "import pandas as pd; df = pd.read_csv('$CSV_FILE'); cols = [c for c in df.columns if 'lon' in c.lower()]; print(cols[0] if cols else '')")
            if [ -n "$LAT_COL" ] && [ -n "$LON_COL" ]; then
                python3 .opencode/skills/geographic-analysis/analyze.py "$CSV_FILE" "$LAT_COL" "$LON_COL" "$OUTPUT_DIR"
            fi
            ;;
        categorical-analysis)
            # Auto-detect categorical column (exclude geographic/location columns)
            CAT_COL=$(python3 -c "
import pandas as pd
df = pd.read_csv('$CSV_FILE')

# Geographic keywords to exclude
geo_keywords = ['borough', 'city', 'state', 'county', 'zip', 'postal', 'location', 'address', 'street', 'lat', 'lon', 'coord']

# Find categorical columns (object type, 2-50 unique values)
candidates = [c for c in df.columns if df[c].dtype == 'object' and 2 <= df[c].nunique() <= 50]

# Exclude geographic columns
non_geo = [c for c in candidates if not any(kw in c.lower() for kw in geo_keywords)]

# Prefer columns with these keywords (type, factor, category, class, cause, reason)
priority_keywords = ['type', 'factor', 'category', 'class', 'cause', 'reason', 'vehicle', 'contributing']
priority_cols = [c for c in non_geo if any(kw in c.lower() for kw in priority_keywords)]

# Pick priority column first, otherwise first non-geo column
if priority_cols:
    print(priority_cols[0])
elif non_geo:
    print(non_geo[0])
elif candidates:
    print(candidates[0])  # Fallback to any categorical if no better option
else:
    print('')
")
            if [ -n "$CAT_COL" ]; then
                python3 .opencode/skills/categorical-analysis/analyze.py "$CSV_FILE" "$CAT_COL" "$OUTPUT_DIR"
            fi
            ;;
        classification-analysis)
            # Auto-detect target column (prefer outcome/result columns over geographic)
            TARGET_COL=$(python3 -c "
import pandas as pd
df = pd.read_csv('$CSV_FILE')

# Geographic keywords to exclude
geo_keywords = ['borough', 'city', 'state', 'county', 'zip', 'postal', 'location', 'address', 'street']

# Find classification targets (object type, 2-20 classes)
candidates = [c for c in df.columns if df[c].dtype == 'object' and 2 <= df[c].nunique() <= 20]

# Exclude geographic columns
non_geo = [c for c in candidates if not any(kw in c.lower() for kw in geo_keywords)]

# Prefer columns with outcome/result keywords
priority_keywords = ['severity', 'damage', 'level', 'status', 'outcome', 'result', 'type', 'category', 'class']
priority_cols = [c for c in non_geo if any(kw in c.lower() for kw in priority_keywords)]

# Pick priority column first, otherwise first non-geo column
if priority_cols:
    print(priority_cols[0])
elif non_geo:
    print(non_geo[0])
elif candidates:
    print(candidates[0])  # Fallback
else:
    print('')
")
            if [ -n "$TARGET_COL" ]; then
                python3 .opencode/skills/classification-analysis/analyze.py "$CSV_FILE" "$TARGET_COL" "$OUTPUT_DIR"
            fi
            ;;
        clustering-analysis)
            python3 .opencode/skills/clustering-analysis/analyze.py "$CSV_FILE" "$OUTPUT_DIR"
            ;;
    esac
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Merge Insights"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 merge_insights.py "$OUTPUT_DIR"

if [ ! -f "$OUTPUT_DIR/combined_insights.json" ]; then
    echo "❌ Error: Merge failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Extract Page Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 extract_page_numbers.py "$OUTPUT_DIR/combined_insights.json" "$OUTPUT_DIR/page_data.json"

if [ ! -f "$OUTPUT_DIR/page_data.json" ]; then
    echo "❌ Error: Extraction failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Write Investigation Article"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/write-investigation/write.py "$OUTPUT_DIR/combined_insights.json" "$OUTPUT_DIR/page_data.json" "$OUTPUT_DIR"

if [ ! -f "$OUTPUT_DIR/article_content.json" ]; then
    echo "❌ Error: Article writing failed"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5.5: Generate Hero Image"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Generate investigation ID from timestamp
INVESTIGATION_ID="investigation-$(date +%Y%m%d-%H%M%S)"
python3 .opencode/skills/generate-hero-image/generate.py "$OUTPUT_DIR/combined_insights.json" "$INVESTIGATION_ID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Build HTML Page"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/build-html-page/build.py "$OUTPUT_DIR/article_content.json" "$OUTPUT_DIR/page_data.json" investigations

# Find the generated HTML file
HTML_FILE=$(ls -t investigations/investigation-*.html | head -1)

# Extract investigation ID from the HTML filename
INVESTIGATION_ID=$(basename "$HTML_FILE" .html)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7: Build Technical Page"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/build-technical-page/build_technical.py "$OUTPUT_DIR/page_data.json" "$INVESTIGATION_ID" investigations

# Find the generated technical HTML file
TECH_FILE=$(ls -t investigations/${INVESTIGATION_ID}-technical.html | head -1)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8: Update Homepage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/update-index/update_index.py "$OUTPUT_DIR/article_content.json" "$OUTPUT_DIR/page_data.json" "$(basename $HTML_FILE)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 9: Create Preview Branch"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 .opencode/skills/deploy-preview/deploy.py "$HTML_FILE"

TIMER_END=$(date +%s)
DURATION=$((TIMER_END - TIMER_START))

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ PIPELINE COMPLETE                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  Total time: ${DURATION}s"
echo "💰 Total cost: \$0.00 (all Ollama)"
echo ""
echo "📊 Preview created successfully!"
echo "  • Branch: preview/$INVESTIGATION_ID"
echo "  • Review instructions: PREVIEW_$INVESTIGATION_ID.txt"
echo ""
echo "📂 Generated files:"
echo "  • Insights: $OUTPUT_DIR/combined_insights.json"
echo "  • Page data: $OUTPUT_DIR/page_data.json"
echo "  • Article: $OUTPUT_DIR/article_content.json"
echo "  • HTML: $HTML_FILE"
echo "  • Technical: $TECH_FILE"
echo "  • Homepage: index.html (updated)"
echo ""
echo "🔍 Review locally:"
echo "  open $HTML_FILE"
echo "  python3 -m http.server 8000"
echo ""
echo "✅ To approve and deploy to production:"
echo "  python3 .opencode/skills/deploy-preview/approve.py preview/$INVESTIGATION_ID"
echo ""
echo "❌ To reject and discard changes:"
echo "  python3 .opencode/skills/deploy-preview/reject.py preview/$INVESTIGATION_ID"
echo ""
