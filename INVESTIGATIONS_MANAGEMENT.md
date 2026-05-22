# Managing Investigations - Dynamic Registry System

## Overview

The RecordsReveal site now uses a **centralized investigations registry** (`investigations_registry.json`) to dynamically populate:
1. **"All Investigations" sidebar** on each investigation page
2. **"INVESTIGATIONS" column** in the footer

This eliminates hardcoded investigation lists and makes adding/removing investigations a single-file update.

---

## Registry File: `investigations_registry.json`

### Location
```
/investigations_registry.json
```

### Structure
```json
{
  "investigations": [
    {
      "id": "investigation-20260521-114147",
      "title": "Police Use of Force · Live",
      "headline": "Police use of force patterns reveal troubling disparities",
      "category": "SAFETY",
      "status": "LIVE NOW",
      "url": "investigation-20260521-114147.html",
      "order": 1,
      "active": true
    }
  ]
}
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | string | Yes | Unique identifier for the investigation | `"bird-strikes"` |
| `title` | string | Yes | Display title (used in footer) | `"Bird Strikes · Live"` |
| `headline` | string | Yes | Full headline (used in sidebar) | `"35 years of FAA data reveals..."` |
| `category` | string | Yes | Investigation category (uppercase) | `"AVIATION"`, `"SAFETY"`, `"HEALTH"` |
| `status` | string | Yes | Current status | `"LIVE NOW"`, `"COMING SOON"` |
| `url` | string | Yes | Relative URL to investigation page | `"bird-strikes.html"`, `"#"` |
| `order` | integer | Yes | Display order (1 = first, 2 = second, etc.) | `1`, `2`, `3` |
| `active` | boolean | Yes | Whether to show on site | `true`, `false` |

---

## How It Works

### 1. **Build Script Integration**

The main article builder (`.opencode/skills/build-html-page/build.py`) loads the registry automatically:

```python
# Load investigations registry
investigations = load_investigations_registry()

# Generate dynamic sidebar HTML
sidebar_html = generate_investigations_sidebar_html(investigations)

# Generate dynamic footer HTML
footer_html = generate_investigations_footer_html(investigations)
```

**Functions:**
- `load_investigations_registry()` - Reads JSON, filters active investigations, sorts by order
- `generate_investigations_sidebar_html(investigations)` - Creates sidebar section
- `generate_investigations_footer_html(investigations)` - Creates footer section

### 2. **Automatic Updates**

When you run the pipeline (`./run_full_pipeline.sh`), new investigations automatically include:
- ✅ Current list of all investigations in sidebar
- ✅ Current list of all investigations in footer
- ✅ Sorted by `order` field
- ✅ Only `active: true` investigations shown

### 3. **Existing Pages**

To update existing investigation pages with the current registry, run:

```bash
python3 update_investigations_sections.py
```

This script:
- Reads `investigations_registry.json`
- Updates all 5 existing investigation HTML files
- Replaces both sidebar and footer sections
- Preserves all other page content

---

## Adding a New Investigation

### Step 1: Add to Registry

Edit `investigations_registry.json`:

```json
{
  "id": "climate-data",
  "title": "Climate Data · Live",
  "headline": "50 years of temperature data reveals acceleration patterns",
  "category": "ENVIRONMENT",
  "status": "LIVE NOW",
  "url": "climate-data.html",
  "order": 5,
  "active": true
}
```

### Step 2: Update Existing Pages

```bash
python3 update_investigations_sections.py
```

This updates all existing investigation pages to show the new investigation.

### Step 3: Build New Investigation

When you run the pipeline to generate the new investigation:

```bash
./run_full_pipeline.sh
```

The new investigation page will automatically include all investigations from the registry.

### Step 4: Commit Changes

```bash
git add investigations_registry.json investigations/*.html
git commit -m "Add Climate Data investigation to registry"
git push
```

---

## Removing/Hiding an Investigation

### Option 1: Soft Delete (Hide from site)

Set `active: false` in the registry:

```json
{
  "id": "old-investigation",
  "active": false
}
```

The investigation won't appear in sidebars or footers, but the file remains on the server.

### Option 2: Hard Delete (Remove completely)

1. Remove the entry from `investigations_registry.json`
2. Delete the HTML file: `rm investigations/old-investigation.html`
3. Run update script: `python3 update_investigations_sections.py`
4. Commit changes

---

## Changing Display Order

Simply change the `order` field:

```json
{
  "id": "bird-strikes",
  "order": 1   // Shows first
},
{
  "id": "hollywood",
  "order": 2   // Shows second
}
```

Then run the update script:

```bash
python3 update_investigations_sections.py
git add investigations/*.html investigations_registry.json
git commit -m "Reorder investigations"
git push
```

---

## Changing Status

To mark an investigation as "Coming Soon":

```json
{
  "id": "future-investigation",
  "status": "COMING SOON",
  "url": "#"   // Use # for unreleased investigations
}
```

To mark as live:

```json
{
  "id": "future-investigation",
  "status": "LIVE NOW",
  "url": "future-investigation.html"
}
```

---

## Testing the Registry

### Validate JSON Syntax

```bash
python3 -c "import json; json.load(open('investigations_registry.json')); print('✅ Valid JSON')"
```

### Test Registry Loading

```bash
python3 -c "
import json
data = json.load(open('investigations_registry.json'))
print(f'✅ {len(data[\"investigations\"])} investigations loaded')
for inv in data['investigations']:
    print(f'  - {inv[\"title\"]} (order: {inv[\"order\"]}, active: {inv[\"active\"]})')
"
```

### Check Build Script

```bash
python3 -m py_compile .opencode/skills/build-html-page/build.py
echo "✅ Build script syntax OK"
```

---

## Current Investigations (as of May 21, 2026)

| Order | ID | Title | Status | Category |
|-------|----|----|--------|----------|
| 1 | investigation-20260521-114147 | Police Use of Force · Live | LIVE NOW | SAFETY |
| 2 | car-crashes | NYC Traffic Crashes · Live | LIVE NOW | SAFETY |
| 3 | hollywood | Hollywood Box Office · Live | LIVE NOW | ENTERTAINMENT |
| 4 | bird-strikes | Bird Strikes · Live | LIVE NOW | AVIATION |
| 5 | food-nutrition | Food Nutrition · Soon | COMING SOON | HEALTH |
| 6 | crime-statistics | Crime Statistics · Soon | COMING SOON | CRIME |

---

## Troubleshooting

### Issue: "Could not load investigations registry"

**Cause:** Build script can't find `investigations_registry.json`

**Fix:**
```bash
# Check if file exists
ls -lh investigations_registry.json

# Verify JSON is valid
python3 -c "import json; json.load(open('investigations_registry.json'))"
```

### Issue: Investigations not showing on page

**Cause 1:** `active: false` in registry  
**Fix:** Set `active: true` and run update script

**Cause 2:** Old page not updated  
**Fix:** Run `python3 update_investigations_sections.py`

### Issue: Wrong order in sidebar/footer

**Cause:** `order` field not set correctly  
**Fix:** Update `order` values (1, 2, 3...) and run update script

---

## Best Practices

1. **Always use unique IDs** - No duplicate `id` values
2. **Sequential order numbers** - Use 1, 2, 3, 4... (not 1, 5, 10)
3. **Update existing pages** - Run `update_investigations_sections.py` after registry changes
4. **Test before committing** - Validate JSON syntax first
5. **Keep titles short** - Footer has limited space (~50 characters)
6. **Use descriptive headlines** - Sidebar has more room for detail
7. **Set active: false** instead of deleting - Easier to restore later

---

## Files Modified by This System

**Registry:**
- `investigations_registry.json` - Central list of all investigations

**Build Scripts:**
- `.opencode/skills/build-html-page/build.py` - Reads registry, generates HTML

**Update Scripts:**
- `update_investigations_sections.py` - Updates existing investigation pages

**Investigation Pages (all updated automatically):**
- `investigations/bird-strikes.html`
- `investigations/hollywood.html`
- `investigations/car-crashes.html`
- `investigations/investigation-20260521-114147.html`
- `investigations/investigation-20260521-104346.html`
- (Future investigations generated by pipeline)

---

## Summary

✅ **Single source of truth:** `investigations_registry.json`  
✅ **Automatic propagation:** Build script reads registry  
✅ **Easy updates:** Edit JSON, run update script  
✅ **Consistent across site:** All pages show same investigation list  
✅ **Order control:** Simple numeric ordering  
✅ **Show/hide toggle:** `active` field  

**To add a new investigation:**
1. Add entry to `investigations_registry.json`
2. Run `python3 update_investigations_sections.py`
3. Commit and push

That's it!
