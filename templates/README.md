# RecordsReveal HTML Templates

This folder contains reference HTML templates showing the complete structure of both investigation page types.

## Files

### 1. `investigation-page-template.html`
**Main Article Page** - Journalism-focused newspaper style

**Design:**
- **Theme:** RecordsReveal newspaper aesthetic
- **Fonts:** Libre Baskerville (headlines), Barlow (body), Barlow Condensed (numbers)
- **Colors:** Cream background (#f8f6f1), RED (#b5271f), ORANGE (#d2691e)
- **Layout:** Two-column (main article + right sidebar)

**Sections:**
- Header with navigation (Home/About/Contact/Privacy)
- Leaderboard ad (728×90)
- Technical report banner (dark with gold button)
- Hero stats banner (4 key statistics)
- Main article (headline, byline, body paragraphs)
- 3 charts integrated into article flow
- Methodology box with publication/updated dates
- Sidebar:
  - Newsletter signup
  - All Investigations list
  - Key Numbers
  - Ads (300×250)
- Footer (4-column: brand, investigations, publication, data sources)

**Integrations:**
- Google Analytics 4: `G-7B3KBBGVWE`
- Google AdSense: `ca-pub-9045696717764033`
- Plotly.js for interactive charts
- Responsive design (mobile hides sidebar)

---

### 2. `technical-page-template.html`
**Technical Report Page** - Data science / researcher focused

**Design:**
- **Theme:** Dark technical dashboard
- **Fonts:** Bebas Neue (titles), DM Sans (body), DM Mono (code/data)
- **Colors:** Dark background (#0d0d0d), RED (#D62828), ORANGE (#F77F00)
- **Layout:** Full-width single column

**Sections:**
- Navigation with internal anchor links (Findings/Models/Clustering)
- Hero section with technical subtitle
- Stats bar (4 key metrics)
- **Section 1:** Key Findings
  - Executive summary
  - 2 main visualizations
- **Section 2:** Predictive Models
  - Feature importance chart
  - Confusion matrix
  - ROC curve
  - Model performance table
- **Section 3:** Clustering Analysis
  - K-Means PCA scatter plot
  - Cluster size distribution
  - Silhouette scores
- **Section 4:** Methodology
  - Dataset information
  - Analysis pipeline
  - Tools & libraries (code block)
  - Reproducibility notes
- Footer with link back to main article

**Integrations:**
- Same GA4 and AdSense as main page
- Plotly.js with dark theme configurations
- Responsive grid layouts

---

## How Templates Are Used

These are **reference templates** showing the complete HTML structure. The actual page generation happens in:

**Main Article Builder:**
`.opencode/skills/build-html-page/build.py`
- Reads data from `merged_insights.json` and chart files
- Replaces placeholder variables (e.g., `{INVESTIGATION_TITLE}`)
- Generates final HTML with real data

**Technical Report Builder:**
`.opencode/skills/build-technical-page/build_technical.py`
- Reads same data sources
- Creates additional technical charts (feature importance, PCA, etc.)
- Generates dark-themed technical page

---

## Variable Placeholders

Templates use placeholders that get replaced during build:

### Common Variables:
```
{INVESTIGATION_TITLE}          - Main headline
{INVESTIGATION_DESCRIPTION}    - Meta description
{PUBLICATION_DATE}             - e.g., "May 21, 2026"
{DATA_SOURCE}                  - e.g., "FAA Wildlife Database"
{investigation_id}             - e.g., "investigation-20260521-114147"
```

### Chart Data:
```
{CHART_1_DATA}                 - Plotly data array
{CHART_1_LAYOUT}               - Plotly layout config
{CHART_1_TITLE}                - Chart title text
```

### Statistics:
```
{STAT_1_VALUE}                 - e.g., "5,000"
{STAT_1_LABEL}                 - e.g., "Records Analyzed"
{KEY_NUMBER_1}                 - Sidebar key stat
```

### Technical Page Specific:
```
{EXECUTIVE_SUMMARY_TEXT}       - Summary paragraph
{N_CLUSTERS}                   - Number of K-Means clusters
{SILHOUETTE_SCORE}             - Cluster quality metric
{AUC_SCORE}                    - Model performance metric
{FEATURE_IMPORTANCE_DATA}      - Feature ranking chart data
{PCA_SCATTER_DATA}             - Cluster visualization data
```

---

## Customization

To modify the design:

1. **Edit templates** for reference/documentation
2. **Edit Python build scripts** (`.opencode/skills/build-*-page/build*.py`) for actual generation
3. **Test changes** by running: `./run_full_pipeline.sh`

---

## Styling Guidelines

### Investigation Page (Newspaper Style)
- **Serif fonts** for headlines and article text (readability)
- **Light background** (cream/paper texture)
- **High contrast** for text (dark ink on light paper)
- **Traditional layout** (column-based)
- **Red accent color** for branding and CTAs

### Technical Page (Dashboard Style)
- **Sans-serif fonts** for titles, monospace for code
- **Dark background** (reduces eye strain for data analysis)
- **Muted colors** with bright accents for data points
- **Grid layouts** for charts and tables
- **Orange/red accents** for emphasis

---

## File Sizes
- `investigation-page-template.html`: ~18KB
- `technical-page-template.html`: ~16KB

Both templates include all CSS inline for portability and fast loading.

---

## Updates

**Last Updated:** May 21, 2026

**Recent Changes:**
- Added "All Investigations" sidebar section
- Standardized "View Technical Report" banner
- Updated footer to 4-column layout
- Added publication dates to methodology sections
- Integrated GA4 and AdSense tracking
- Standardized fonts across all pages
