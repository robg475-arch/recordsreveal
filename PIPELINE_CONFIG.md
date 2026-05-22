# RecordsReveal Pipeline Configuration

## Tracking & Analytics

### Google Analytics 4
- **Measurement ID**: `G-7B3KBBGVWE`
- **Included in**: All generated pages (main articles + technical reports)
- **Template locations**:
  - `.opencode/skills/build-html-page/build.py` (line 454, 459)
  - `.opencode/skills/build-technical-page/build_technical.py` (line 857, 862)
- **Static pages**: `index.html`, `about/`, `contact/`, `privacy/`

### Google AdSense
- **Publisher ID**: `ca-pub-9045696717764033`
- **Status**: Under review (submitted May 21, 2026)
- **Ad placements**:
  - Main articles: 4 ad units (leaderboard + 3 sidebar rectangles)
  - Technical reports: 3 ad units (after findings, after ML, before footer)
- **Ad slots**: Currently using placeholder `data-ad-slot="XXXXXXXXXX"`
  - Replace with real slot IDs after approval

## SEO Configuration

### Sitemap
- **Location**: `/sitemap.xml`
- **Auto-updated**: No (manual update needed when adding investigations)
- **Includes**: Homepage, static pages, all investigations (main + technical)

### Robots.txt
- **Location**: `/robots.txt`
- **Allows**: All search engines, ads.txt verification
- **Disallows**: Test folders, pipeline directories, Python scripts

### Meta Tags
All pages include:
- `<title>` with site name
- `<meta name="description">` for SEO
- `<meta property="og:title">` for social sharing
- `<meta property="og:description">` for social previews

## Pipeline Architecture

### 8-Step Process
1. **Profile**: Analyze dataset structure and quality
2. **Analyze**: Run 5 parallel analyses (temporal, geographic, categorical, classification, clustering)
3. **Merge**: Combine insights into unified document
4. **Extract**: Generate page data with geocoding (Nominatim API)
5. **Write**: Generate journalism prose (Claude Sonnet 4.5, ~$0.02)
6. **Build HTML**: Create main article page with charts
7. **Build Technical**: Create technical report with detailed analysis
8. **Update Index**: Automatically update homepage with new investigation

### Cost Per Run
- **Ollama analysis**: $0.00 (local/remote server at 192.168.1.153:11434)
- **Claude writing**: ~$0.02 (API call to Anthropic)
- **Total**: ~$0.02 per investigation

### Runtime
- **Average**: ~90 seconds for full pipeline
- **Depends on**: Dataset size, number of analyses, API response times

## Automatic Inclusions

Every generated investigation automatically includes:

### JavaScript Libraries
- **Plotly.js**: v2.27.0 (for interactive charts)
- **Google Analytics**: G-7B3KBBGVWE
- **Google AdSense**: ca-pub-9045696717764033

### Typography
- **Main articles**: Libre Baskerville (headlines), Barlow (body), Barlow Condensed (numbers)
- **Technical reports**: Bebas Neue (titles), DM Sans (body), DM Mono (code)
- **Font source**: Google Fonts CDN

### Color Schemes
- **Main articles**: Cream (#f8f6f1), RED (#b5271f), ORANGE (#d2691e)
- **Technical reports**: Dark (#0d0d0d), RED (#D62828), ORANGE (#F77F00)

### Charts
- **Main articles**: 3-4 charts (hero stat + findings visualizations)
- **Technical reports**: 7-8 charts (hero + ML models + clustering + PCA)
- **Validation**: Charts are validated before rendering (skipped if 100% at midnight, etc.)

### Homepage Updates
- **Hero story**: Latest investigation becomes the featured story
- **Sidebar stats**: Top 3 KPIs from latest investigation
- **Top stories**: Updated with new investigation link
- **Footer links**: Updated with new investigation (max 4)
- **Counters**: "Investigations Live" incremented automatically
- **Topic emoji**: Auto-detected (👮 police, 🚗 crash, 🚨 crime, 📊 default)

## Data Sources

### Geocoding
- **Service**: Nominatim (OpenStreetMap)
- **Rate limit**: 1 request per second
- **User-Agent**: RecordsReveal
- **Timeout**: 5 seconds
- **Fallback**: Displays raw coordinates if API fails

### AI Models
- **Analysis**: Ollama deepseek-r1:14b (remote at 192.168.1.153:11434)
- **Writing**: Claude Sonnet 4.5 (Anthropic API)
- **Cost optimization**: Use free Ollama for heavy analysis, paid Claude for final prose

## Maintenance

### To Update Google Analytics ID
```bash
# Replace G-7B3KBBGVWE with new ID
find . -type f \( -name "*.html" -o -name "*.py" \) -exec sed -i '' 's/G-7B3KBBGVWE/G-NEWID/g' {} \;
git commit -am "Update GA4 Measurement ID"
git push
```

### To Update AdSense Publisher ID
```bash
# Replace ca-pub-9045696717764033 with new ID
find . -type f \( -name "*.html" -o -name "*.py" \) -exec sed -i '' 's/ca-pub-9045696717764033/ca-pub-NEWID/g' {} \;
git commit -am "Update AdSense Publisher ID"
git push
```

### To Add Ad Slot IDs (After Approval)
1. Get ad unit IDs from AdSense dashboard
2. Replace `data-ad-slot="XXXXXXXXXX"` with real IDs
3. Update templates in `.opencode/skills/build-html-page/build.py` and `build-technical-page/build_technical.py`

### To Update Sitemap
```bash
# After adding new investigations manually
# Edit sitemap.xml to add new <url> entries
git add sitemap.xml
git commit -m "Update sitemap with new investigations"
git push
```

## Verification

### Test GA4 Tracking
1. Visit https://recordsreveal.com
2. Open https://analytics.google.com
3. Go to Reports → Realtime
4. Your visit should appear within 30 seconds

### Test New Investigation Build
```bash
# Run full pipeline on test dataset
./run_full_pipeline.sh test_dataset.csv

# Check that generated HTML includes:
# - Google Analytics: G-7B3KBBGVWE
# - Google AdSense: ca-pub-9045696717764033
# - All charts render properly
# - Homepage was updated automatically
```

## Contact
- **Tips**: tips@recordsreveal.com
- **Corrections**: corrections@recordsreveal.com
- **General**: hello@recordsreveal.com
- **Press**: press@recordsreveal.com

## Last Updated
May 21, 2026
