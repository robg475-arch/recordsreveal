# RecordsReveal Quick Start
## From CSV to Published Investigation in 4 Hours

**Last Updated:** May 23, 2026

---

## 📋 30-Second Checklist

```bash
# 1. Investigate (3 min)
python3 investigate.py data/your_data.csv

# 2. Render (1 min)
python3 render_complete.py investigation_output/investigation-*.json

# 3. Create data science page (1 hour)
cp investigations/dark-money-data-analysis.html investigations/your-topic-data-analysis.html
# Edit: schema, stats, formulas, code

# 4. Verify (5 min)
open investigations/investigation-*.html
open investigations/your-topic-data-analysis.html

# 5. Deploy
git add . && git commit -m "Investigation: [Topic]" && git push
```

---

## ✅ Pre-Flight Checklist

**Before you start:**
- [ ] CSV file cleaned and in `data/` folder
- [ ] `.env` has `ANTHROPIC_API_KEY` and `LEONARDO_API_KEY`
- [ ] Ollama running at `192.168.1.153:11434`
- [ ] You have 4 hours available

---

## 🚀 Step-by-Step

### Step 1: Investigate (3 minutes)

```bash
python3 investigate.py data/campaign_finance/your_data.csv
```

**Wait for:**
- Ollama analysis (~2 min)
- Claude journalism (~30 sec)
- JSON output: `investigation_output/investigation-YYYYMMDD-HHMMSS.json`

**Verify:**
```bash
cat investigation_output/investigation-*.json | jq .headline
```

---

### Step 2: Render Complete Page (1 minute)

```bash
python3 render_complete.py investigation_output/investigation-YYYYMMDD-HHMMSS.json
```

**Wait for:**
- Leonardo.ai hero image (~30 sec)
- Claude visualization (~20 sec)
- HTML output: `investigations/investigation-YYYYMMDD-HHMMSS.html`

**Verify:**
```bash
open investigations/investigation-*.html
```

**Check:**
- [ ] Hero image displays
- [ ] 4 charts render
- [ ] Sidebar present
- [ ] "🔬 For Data Nerds" button visible (orange)

---

### Step 3: Create Data Science Deep Dive (1 hour)

```bash
# Copy template
cp investigations/dark-money-data-analysis.html \
   investigations/YOUR-TOPIC-data-analysis.html
```

**Edit these sections:**

1. **Title** (line ~8)
   ```html
   <title>Statistical Analysis: YOUR TOPIC | RecordsReveal</title>
   ```

2. **Back link** (line ~149)
   ```html
   <a href="investigation-YYYYMMDD-HHMMSS.html">Back to Main Investigation: YOUR TOPIC</a>
   ```

3. **Headline** (line ~163)
   ```html
   <h1>Statistical Analysis: YOUR TOPIC</h1>
   ```

4. **Dataset info callout** (line ~173)
   - Update source file path
   - Update record count
   - Update variable count

5. **Schema table** (line ~186)
   - Replace with your CSV columns
   - Update data types
   - Add descriptions

6. **Descriptive statistics** (line ~233)
   - Calculate mean, median, min, max from your data
   - Update stat cards

7. **Key findings calculations** (line ~285)
   - Show formulas for each major finding
   - Include Python code snippets
   - Verify math is correct

8. **Statistical tests** (line ~420)
   - Run t-tests if comparing groups
   - Calculate Cohen's d for effect size
   - Report p-values

9. **Outlier analysis** (line ~515)
   - Use IQR method on key variables
   - List outlier records
   - Explain why they're interesting

10. **Limitations** (line ~585)
    - List dataset-specific caveats
    - Note any data quality issues
    - Explain what you can't claim

**Verify:**
```bash
open investigations/YOUR-TOPIC-data-analysis.html
```

---

### Step 4: Quality Control (5 minutes)

**Investigation page:**
- [ ] HTML ends with `</html>`
- [ ] Hero image loads (not broken)
- [ ] All 4 charts render
- [ ] Sidebar scrolls WITH content (not sticky)
- [ ] "🔬 For Data Nerds" button visible and links correctly
- [ ] CSV download works
- [ ] Share buttons functional

**Data science page:**
- [ ] Back link to investigation works
- [ ] Schema table matches your CSV
- [ ] All statistics recalculated (not template numbers)
- [ ] Python code runs without errors
- [ ] Formulas are accurate
- [ ] No "[YOUR TOPIC]" placeholders remain

---

### Step 5: Deploy

```bash
# Add to git
git add investigations/investigation-*.html
git add investigations/*-data-analysis.html
git add images/heroes/investigation-*.jpg
git add investigation_output/investigation-*.json

# Commit
git commit -m "Investigation: [Your Topic] - [Key Stat]"

# Push
git push origin main

# Deploy (your process)
# ...
```

---

## 💰 Cost Breakdown

| Step | Time | Cost |
|------|------|------|
| 1. Investigate | 3 min | $0.02-0.08 |
| 2. Render | 1 min | $0.02-0.04 |
| 3. Data science page | 1 hour | $0.00 (manual) |
| 4. QA | 5 min | $0.00 |
| 5. Deploy | 5 min | $0.00 |
| **TOTAL** | **~1.5 hours** | **$0.04-0.12** |

---

## 🚨 Common Mistakes

### ❌ Skipping data science page
**Fix:** Always create it. It's what makes you credible.

### ❌ Not updating back link
**Fix:** Line ~149 in data science page must match your investigation filename.

### ❌ Leaving template numbers
**Fix:** Recalculate ALL statistics from your actual CSV.

### ❌ Not testing Python code
**Fix:** Run every code snippet in a Python shell before publishing.

### ❌ Forgetting mobile test
**Fix:** Open on phone, verify sidebar stacks below content.

---

## 📚 Full Documentation

- **Complete workflow:** `COMPLETE_WORKFLOW.md`
- **Lessons learned:** `LESSONS_LEARNED.md`
- **AI prompts:** `PROMPT_CHAIN.md`
- **System architecture:** `NEW_WORKFLOW.md`

---

## ❓ Troubleshooting

### Hero image not generating
```bash
# Check Leonardo API key
grep LEONARDO_API_KEY .env

# Check credits
curl https://cloud.leonardo.ai/api/rest/v1/me \
  -H "Authorization: Bearer $LEONARDO_API_KEY"
```

### Charts not rendering
- Open browser console (F12)
- Look for JavaScript errors
- Verify Chart.js CDN loaded

### Sidebar scrolling independently
- Check `render_complete.py` line ~390
- Should NOT have `position: sticky`

### Data science page 404
- Verify filename matches button link
- Check file is in `investigations/` folder
- Ensure no typos in URL

---

## 🎯 Success Criteria

**You're ready to publish when:**
- ✅ Investigation page loads completely
- ✅ All images and charts work
- ✅ Data science page exists and is accurate
- ✅ Both pages link to each other
- ✅ Mobile responsive verified
- ✅ All statistics manually verified
- ✅ Python code tested
- ✅ No placeholders remain

---

## ⏱️ Time Budget

| Task | Time | Can Rush? |
|------|------|-----------|
| CSV cleaning | 30 min | ❌ No - quality matters |
| Investigation run | 3 min | ✅ Yes - automated |
| Render | 1 min | ✅ Yes - automated |
| Data science page | 1 hour | ⚠️ Some - but don't skip sections |
| QA testing | 5 min | ❌ No - catches critical bugs |
| Deployment | 5 min | ✅ Yes - straightforward |
| **TOTAL** | **~1h 44min** | |

**Realistic timeline:** 2-4 hours from start to published.

---

**Questions?** See `LESSONS_LEARNED.md` or `COMPLETE_WORKFLOW.md`
