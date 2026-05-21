# Update Index Skill

Automatically updates `index.html` when a new investigation is published.

## What It Does

When you run the full pipeline, Step 8 calls this skill to update the homepage with the latest investigation:

### 1. Makes New Investigation the Hero Story
- Replaces the current hero with the new investigation
- Includes: icon, category, headline, lede, stats, link

### 2. Moves Previous Hero to "Also Live Now"
- Previous hero investigation moves down to secondary position
- Maintains chronological order (newest → oldest)

### 3. Updates Sidebar Stats ("From Our Latest Investigation")
- Extracts 3 compelling stats from `page_data.json`
- Automatically selects:
  - **Stat 1 (RED)**: Majority category, peak hour, or primary finding
  - **Stat 2 (GOLD)**: Busiest day, best model accuracy, or secondary finding
  - **Stat 3 (BLACK)**: Trend change, cluster count, or tertiary finding

### 4. Updates "Top Stories" Sidebar
- Adds new investigation to top of list
- Keeps 3 most recent live investigations
- Maintains 2 "Coming Soon" items

### 5. Updates Footer Links
- Adds new investigation to footer navigation
- Keeps up to 4 most recent investigations
- Auto-generates short link text based on topic

### 6. Updates Stat Strip
- Increments "Investigations Live" counter
- Reflects total published investigations

## Usage

Automatically called by `run_full_pipeline.sh` (Step 8):

```bash
python3 .opencode/skills/update-index/update_index.py \
  pipeline_output/article_content.json \
  pipeline_output/page_data.json \
  investigation-20260521-104346.html
```

## Inputs

1. **article_content.json**: Contains headline, lede, findings
2. **page_data.json**: Contains stats, chart data, analysis results
3. **html_filename**: Name of the generated investigation HTML file

## Outputs

Updates `index.html` in-place with:
- New hero section
- Updated sidebar stats
- Updated top stories
- Updated footer links
- Incremented stat counter

## Smart Detection

The script automatically detects investigation type from headline keywords:

- **Police/Force** → 👮 POLICE DATA
- **Crash/Traffic** → 🚗 TRAFFIC
- **Crime** → 🚨 CRIME DATA
- **Default** → 📊 DATA ANALYSIS

## Duplicate Prevention

If the investigation HTML filename already exists in `index.html`, the script skips the update to prevent duplicates.

## Example Output

```
======================================================================
🏠 UPDATING INDEX.HTML (COMPLETE REFRESH)
======================================================================

📂 Loading article and page data...
✅ Loaded

🔢 Next investigation number: #005

📊 Extracting key stats for sidebar...
✅ Found 3 stats

🎨 Creating hero section...
✅ Hero created

✍️  Updating hero section...
✅ Hero updated

✍️  Updating sidebar stats...
✅ Sidebar stats updated

✍️  Updating top stories...
✅ Top stories updated

✍️  Updating footer links...
✅ Footer links updated

✍️  Updating stat strip...
✅ Stat strip updated

======================================================================
✅ INDEX UPDATE COMPLETE
======================================================================

Investigation #005 is now:
  • Hero story
  • In sidebar stats ('From Our Latest Investigation')
  • In top stories
  • In footer links
  • Link: investigations/investigation-20260521-104346.html
```

## Manual Updates

If you need to manually adjust which investigation is featured, you can:

1. Edit `index.html` directly for the hero section
2. Re-run this script to regenerate sidebar/footer from any investigation
3. Keep older investigations as hero by skipping Step 8 in the pipeline

## Future Enhancements

- Auto-generate better short headlines for sidebar
- Support for custom stat selection
- Archive old investigations to separate page
- RSS feed generation
