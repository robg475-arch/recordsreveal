# Lessons Learned: Dark Money Investigation
## Critical Checklist for Next Dataset

**Date:** May 23, 2026  
**Investigation:** Dark Money in Swing Districts  
**Status:** ✅ Complete and deployed

---

## 🎯 Complete Workflow (Use This Every Time)

### Phase 1: Investigation (Data Analysis + Journalism)

```bash
python3 investigate.py data/your_dataset.csv
```

**Output:** `investigation_output/investigation-YYYYMMDD-HHMMSS.json`

**What happens:**
- Ollama analyzes data (free, ~2 min)
- Claude writes journalism ($0.02-0.08, ~30 sec)
- Saves structured JSON

---

### Phase 2: Render Complete Page (ALL FEATURES)

```bash
python3 render_complete.py investigation_output/investigation-YYYYMMDD-HHMMSS.json
```

**Output:** `investigations/investigation-YYYYMMDD-HHMMSS.html`

**What gets included automatically:**
- ✅ Leonardo.ai hero image (~30 sec)
- ✅ Claude visualization design (~20 sec)
- ✅ 3 AdSense placements in content
- ✅ Sidebar with ads
- ✅ "More Investigations" links
- ✅ Data download button
- ✅ Share buttons (X, Facebook, Copy Link)
- ✅ **"🔬 For Data Nerds" link** (NEW!)

---

### Phase 3: Create Data Science Deep Dive (CRITICAL!)

**⚠️ DO NOT SKIP THIS STEP!**

1. **Copy the template:**
   ```bash
   cp investigations/dark-money-data-analysis.html investigations/YOUR-INVESTIGATION-data-analysis.html
   ```

2. **Edit with investigation-specific data:**
   - Update title and headline
   - Replace dataset schema table (use actual columns from CSV)
   - Update descriptive statistics (mean, median, min, max)
   - Replace key finding calculations with actual formulas used
   - Update Python code snippets with real calculations
   - Add statistical tests (t-tests, Cohen's d, correlations)
   - Document outliers found
   - List limitations specific to this dataset

3. **Verify the back link works:**
   ```html
   <a href="investigation-YYYYMMDD-HHMMSS.html">Back to Main Investigation</a>
   ```

4. **Test in browser:**
   ```bash
   open investigations/YOUR-INVESTIGATION-data-analysis.html
   ```

---

### Phase 4: Quality Control Checklist

**Before claiming success, verify:**

- [ ] Investigation HTML ends with `</html>` (not cut off)
- [ ] Hero image displays correctly (not broken link)
- [ ] All 4 Chart.js charts render
- [ ] 3 AdSense placements visible in content
- [ ] Sidebar scrolls WITH main content (not independently)
- [ ] "🔬 For Data Nerds" orange button present in sidebar
- [ ] Data science deep dive page created
- [ ] Back link from deep dive to main investigation works
- [ ] CSV download button points to correct file
- [ ] All statistical formulas are accurate
- [ ] Python code snippets are valid and tested

---

## 💡 Key Lessons

### 1. Sidebar Must Scroll With Content

**Problem:** Original design had `position: sticky` on sidebar, causing independent scrolling.

**Solution:**
```css
.sidebar {
    /* Removed sticky positioning for synchronized scrolling */
}
```

**File:** `render_complete.py` line ~390

---

### 2. Data Science Page is NOT Optional

**Why it matters:**
- Builds credibility with technical audiences
- Allows peer review and fact-checking
- Shows transparency in methodology
- Differentiates from clickbait journalism
- Attracts academic/researcher traffic

**What to include:**
- Complete dataset schema
- All descriptive statistics
- Every formula with LaTeX or code notation
- Statistical significance tests (t-tests, p-values)
- Effect size analysis (Cohen's d)
- Outlier detection methods
- Reproducible Python code
- Limitations and caveats
- References and further reading

---

### 3. Orange Button in Sidebar Gets Attention

**CSS for prominence:**
```css
.sidebar-section:has(.download-btn[style*="d2691e"]) {
    background: #fff9f0;
    border: 2px solid var(--orange);
}
```

**Button color:**
```html
<a href="..." style="background: #d2691e;">📊 Statistical Analysis</a>
```

**Explainer text below button:**
```html
<p style="font-size: 0.85rem; color: #666;">
    See all formulas, calculations, and statistical tests behind this investigation.
</p>
```

---

### 4. Validation Before Success Messages

**Don't trust Claude's output blindly:**

```python
# Check HTML completeness
if not html.endswith("</html>"):
    print("❌ HTML incomplete!")
    
# Check chart count matches canvas count
chart_count = html.count("new Chart(")
canvas_count = html.count("<canvas")
if chart_count != canvas_count:
    print("⚠️ Chart mismatch!")

# Check markdown artifacts stripped
if "```" in html:
    print("⚠️ Markdown not cleaned!")
```

---

### 5. Hero Image Generation Can Fail

**Always handle gracefully:**

```python
hero_image = generate_hero_image(investigation, investigation_id)

# If fails, continue without image
if not hero_image:
    print("⚠️ Skipping hero image (generation failed)")
    # Template still works without hero
```

**File:** `render_complete.py` has this built-in

---

### 6. Cost Transparency Matters

**Always report:**
- Ollama: $0.00 (local inference)
- Claude journalism: $0.02-0.08
- Claude visualization: $0.02-0.04
- Leonardo.ai: $0.00 (free tier)
- **Total: $0.04-0.12 per investigation**

**Include in methodology page and data science deep dive**

---

## 📋 Next Dataset Workflow (Copy-Paste Checklist)

### Day 1: Investigation

```bash
# 1. Add dataset to data/ folder
cp ~/Downloads/your_data.csv data/your_category/

# 2. Run investigation
python3 investigate.py data/your_category/your_data.csv

# 3. Verify JSON output
cat investigation_output/investigation-*.json | jq .

# 4. Render complete page
python3 render_complete.py investigation_output/investigation-*.json

# 5. Open and verify in browser
open investigations/investigation-*.html
```

**Checklist:**
- [ ] JSON has all required fields (headline, lede, findings, stat_boxes)
- [ ] HTML renders completely (no cutoff)
- [ ] Hero image generated
- [ ] Charts render
- [ ] Sidebar present

---

### Day 2: Data Science Deep Dive

```bash
# 1. Copy template
cp investigations/dark-money-data-analysis.html \
   investigations/YOUR-TOPIC-data-analysis.html

# 2. Update content (see Phase 3 above)
# - Schema table
# - Statistics
# - Formulas
# - Code snippets
# - Tests

# 3. Verify back link
# Edit line ~149: update investigation filename

# 4. Test in browser
open investigations/YOUR-TOPIC-data-analysis.html
```

**Checklist:**
- [ ] Dataset schema accurate (all columns documented)
- [ ] Descriptive statistics match CSV
- [ ] Key finding calculations shown with formulas
- [ ] Python code snippets tested and valid
- [ ] Statistical tests documented (p-values, effect sizes)
- [ ] Outlier analysis included
- [ ] Limitations section filled out
- [ ] Back link to main investigation works

---

### Day 3: Deployment & Marketing

```bash
# 1. Final QA
open investigations/investigation-*.html
open investigations/*-data-analysis.html

# 2. Add to investigations index
# Edit: investigations.html

# 3. Update homepage with latest
# Edit: index.html

# 4. Commit to git
git add .
git commit -m "Investigation: [Topic] - $X.XB in findings"
git push

# 5. Deploy to production
# (Your deployment process here)

# 6. Share on social media
# - X/Twitter with key stat
# - LinkedIn with methodology link
# - Reddit r/dataisbeautiful with viz screenshot
```

---

## 🎨 Design Standards (Never Compromise)

### Colors
- **RED:** `#b5271f` (headlines, critical stats, CTAs)
- **ORANGE:** `#d2691e` (data science callouts, accents)
- **CREAM:** `#f8f6f1` (background)
- **INK:** `#1a1a1a` (body text)

### Fonts
- **Headlines:** Barlow Condensed, 700, uppercase, letter-spacing 0.02-0.04em
- **Body:** Barlow, 400, 1.05rem, line-height 1.6
- **Numbers:** Barlow Condensed, 700, 2.5rem+
- **Code:** JetBrains Mono, 400, 0.9rem

### Spacing
- **Section margin:** 60px top
- **Paragraph margin:** 20px bottom
- **Card padding:** 20px
- **Grid gap:** 20px

---

## 🚨 Common Pitfalls (Avoid These!)

### ❌ DON'T: Skip the data science page
**Why:** Kills credibility, prevents peer review, looks like clickbait

### ❌ DON'T: Use sticky sidebar
**Why:** Independent scrolling is jarring UX

### ❌ DON'T: Trust first render blindly
**Why:** Claude sometimes cuts off mid-sentence or leaves markdown artifacts

### ❌ DON'T: Forget to test hero image
**Why:** Broken images look unprofessional

### ❌ DON'T: Hardcode investigation links
**Why:** They'll break when you add new investigations

### ❌ DON'T: Claim statistical significance without tests
**Why:** Data scientists will call you out

### ❌ DON'T: Hide methodology
**Why:** Transparency is your brand differentiator

---

## ✅ DO THESE EVERY TIME

### ✅ DO: Include Python code snippets in deep dive
**Why:** Shows reproducibility, attracts technical audience

### ✅ DO: Document limitations honestly
**Why:** Shows intellectual honesty, prevents misinterpretation

### ✅ DO: Run statistical tests (t-test, Cohen's d)
**Why:** Differentiates you from amateur data viz sites

### ✅ DO: Link back and forth between pages
**Why:** Keeps users engaged, improves SEO

### ✅ DO: Make data download prominent
**Why:** Shows transparency, enables peer review

### ✅ DO: Report costs transparently
**Why:** Shows efficiency, helps others replicate

### ✅ DO: Test on mobile
**Why:** Sidebar should stack below on mobile

---

## 📦 Files Created This Investigation

```
recordsreveal-site/
├── investigate.py                      # Step 1: Ollama + Claude
├── render_complete.py                  # Step 2: Full render (UPDATED)
├── investigation_output/
│   └── investigation-20260523-090450.json
├── investigations/
│   ├── investigation-20260523-133019.html      # Main investigation
│   └── dark-money-data-analysis.html           # Data science deep dive (NEW!)
├── images/heroes/
│   └── investigation-20260523-133019.jpg
├── methodology.html                    # General methodology (NEW!)
├── COMPLETE_WORKFLOW.md               # User guide
├── PROMPT_CHAIN.md                    # AI prompts documented
├── NEW_WORKFLOW.md                    # System overview
└── LESSONS_LEARNED.md                 # THIS FILE
```

---

## 🔮 Future Improvements

### For Next Investigation

1. **Automate data science page generation**
   - Script that reads investigation JSON
   - Extracts all statistics
   - Auto-generates formulas and code snippets
   - Saves 1-2 hours per investigation

2. **Create investigation index updater**
   - Automatically adds new investigation to investigations.html
   - Extracts headline, date, key stat
   - Updates "More Investigations" sidebar links

3. **Add automated testing**
   - Selenium tests for HTML rendering
   - Verify all links work
   - Check image loading
   - Validate AdSense placement count

4. **Mobile responsive testing**
   - Test on iPhone, iPad, Android
   - Verify sidebar stacking
   - Check chart responsiveness

5. **SEO optimization**
   - Add meta descriptions
   - Open Graph tags for social sharing
   - Schema.org markup for rich results

---

## 📊 Success Metrics

### Technical Quality
- ✅ HTML validates (no errors)
- ✅ All links work (no 404s)
- ✅ Images load (no broken)
- ✅ Charts render (all 4)
- ✅ Mobile responsive (sidebar stacks)
- ✅ AdSense compliant (3+ placements)

### Content Quality
- ✅ Data science page exists
- ✅ All formulas documented
- ✅ Python code valid
- ✅ Statistical tests included
- ✅ Limitations documented
- ✅ References provided

### User Experience
- ✅ Columns scroll together
- ✅ Hero image loads fast
- ✅ Charts interactive
- ✅ Download button works
- ✅ Share buttons functional
- ✅ "For Data Nerds" prominent

---

## 💰 Cost Per Investigation

| Component | Tool | Cost | Time |
|-----------|------|------|------|
| Data analysis | Ollama | $0.00 | ~2 min |
| Journalism | Claude | $0.02-0.08 | ~30 sec |
| Hero image | Leonardo.ai | $0.00 | ~30 sec |
| Visualization | Claude | $0.02-0.04 | ~20 sec |
| Template | Python | $0.00 | instant |
| Data science page | Manual | $0.00 | ~1 hour |
| **TOTAL** | | **$0.04-0.12** | **~3-4 min automated + 1 hour manual** |

**Goal for next investigation:** Automate data science page to reduce manual time to <15 minutes.

---

## 📝 Template for Data Science Page

**Location:** `investigations/dark-money-data-analysis.html`

**Sections Required:**
1. Dataset schema table
2. Descriptive statistics (mean, median, min, max)
3. Key finding calculations (with formulas)
4. Statistical validation (t-tests, p-values)
5. Effect size analysis (Cohen's d)
6. Outlier detection (IQR method)
7. Reproducible Python code
8. Limitations and caveats
9. References

**Styling:**
- JetBrains Mono for code
- Tables with red headers
- Orange callout boxes
- Formula boxes with border-left
- Stats cards with red numbers

---

## ✍️ Final Checklist Before Publishing

**Investigation Page:**
- [ ] Headline accurate and compelling
- [ ] Lede sets context clearly
- [ ] All findings have supporting evidence
- [ ] Statistics cited correctly
- [ ] Pull quotes memorable
- [ ] Hero image relevant and high-quality
- [ ] Charts labeled and interactive
- [ ] 3 AdSense placements visible
- [ ] Sidebar has all components
- [ ] "🔬 For Data Nerds" link works

**Data Science Page:**
- [ ] Schema matches actual CSV
- [ ] All statistics recalculated and verified
- [ ] Formulas shown in clear notation
- [ ] Python code tested and runs
- [ ] Statistical tests documented with p-values
- [ ] Effect sizes calculated (Cohen's d)
- [ ] Outliers identified and explained
- [ ] Limitations listed honestly
- [ ] Back link to main investigation works
- [ ] References and citations complete

**Technical Quality:**
- [ ] Both pages render completely
- [ ] All images load
- [ ] All links work
- [ ] Mobile responsive
- [ ] Sidebar scrolls with content
- [ ] CSV download works
- [ ] Share buttons functional
- [ ] No console errors
- [ ] No markdown artifacts
- [ ] AdSense tags valid

**Ready to deploy!** 🚀

---

## 🎓 What We Learned

1. **Data science deep dives are essential** - They're what separates us from clickbait
2. **Sidebar scrolling matters** - UX details make or break the experience
3. **Validation before success** - Never trust AI output blindly
4. **Orange gets attention** - Visual prominence for important CTAs
5. **Cost transparency builds trust** - Always report what things actually cost
6. **Hero images can fail** - Always handle gracefully
7. **Mobile matters** - Test sidebar stacking on small screens
8. **Documentation is destiny** - Future you will thank current you

---

**Next Investigation:** Apply this entire checklist start to finish. Goal: <4 hours from raw CSV to published investigation with data science deep dive.
