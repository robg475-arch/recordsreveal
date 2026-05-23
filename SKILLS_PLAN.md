# RecordsReveal Skills Implementation Plan

## Overview
Transform INVESTIGATION_PLAYBOOK.md into modular OpenCode skills that integrate:
- Existing Python automation scripts (analyze_v2.py, ai_writer.py, etc.)
- Remote Ollama setup (qwen2.5-coder:7b and llama3.2 at 192.168.1.153:11434)
- Proven manual workflow from playbook

---

## Proposed Skill Structure

### **Skill 1: `analyze-dataset`**
**Purpose:** Comprehensive data analysis (EDA + ML + Clustering)
**Combines:** 
- Phase 2 (EDA), Phase 3 (Regression), Phase 4 (Clustering) from playbook
- Existing `analyze_v2.py` enhanced analysis
- Ollama for insights extraction

**What it does:**
1. Loads CSV and profiles dataset
2. Runs EDA (trends, distributions, correlations)
3. Trains ML models (regression/classification)
4. Performs K-Means clustering
5. Generates domain-specific visualizations
6. Asks Ollama for narrative insights
7. Exports results.json + chart_data.json

**Ollama integration:**
- Use `qwen2.5-coder:7b` for code generation/debugging
- Use `llama3.2` for finding surprising insights from results

---

### **Skill 2: `write-investigation`**
**Purpose:** Generate journalism-quality article content
**Combines:**
- Phase 8 (Story Writing) from playbook
- Existing `ai_writer.py` and `generate_article.py`
- Ollama for cost-effective prose generation

**What it does:**
1. Reads analysis results
2. Extracts key findings
3. Generates headlines, ledes, findings sections
4. Creates pull quotes
5. Writes methodology section
6. Outputs article_content.json

**Ollama vs Claude:**
- Use **Ollama (llama3.2)** for: Finding insights, cluster names, pull quotes (FREE)
- Use **Claude Sonnet 4.5** for: Final prose polish if needed ($0.02)
- Makes user choose cost vs quality

---

### **Skill 3: `build-html-page`**
**Purpose:** Generate complete HTML investigation page
**Combines:**
- Phase 6 (Charts), Phase 7 (Components), Phase 9 (Assembly) from playbook
- Existing `build_investigation_html.py`
- Chart specifications from playbook

**What it does:**
1. Reads article_content.json and chart_data.json
2. Generates inline JavaScript charts (RecordsReveal style)
3. Assembles HTML with proper sections
4. Adds stat boxes, pull quotes, finding cards
5. Embeds AdSense slots
6. Outputs complete investigation-XXX.html

**Key improvement:**
- Use inline JS chart rendering (not exported Plotly HTML)
- Match playbook chart specifications exactly

---

### **Skill 4: `deploy-investigation`**
**Purpose:** Publish to site and update homepage
**Combines:**
- Phase 10 (Deploy) from playbook
- Existing `update_homepage.py`
- Git deployment workflow

**What it does:**
1. Validates HTML (AdSense IDs, links)
2. Updates index.html with new investigation card
3. Updates homepage stats
4. Creates git commit
5. Pushes to GitHub (triggers Cloudflare deploy)
6. Generates social media posts (via Ollama)

---

## Integration Points

### **Use Existing Scripts As Modules:**
```python
# In skills, import existing work:
from analyze_v2 import EnhancedAnalyzer
from generate_article import generate_article_content
from export_chart_data import export_all_chart_data
from update_homepage import update_homepage
```

### **Add Ollama Helper:**
```python
# ollama_helper.py (from playbook)
import requests

OLLAMA_HOST = "http://192.168.1.153:11434"

def ask_ollama_code(prompt):
    """Use qwen2.5-coder:7b for code tasks"""
    r = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": "qwen2.5-coder:7b", "prompt": prompt, "stream": False},
        timeout=120
    )
    return r.json()["response"]

def ask_ollama_write(prompt):
    """Use llama3.2 for writing tasks"""
    r = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False},
        timeout=120
    )
    return r.json()["response"]
```

### **Add Playbook Functions:**
```python
# playbook_utils.py
# Copy key functions from playbook:
# - evaluate_dataset()
# - run_eda()
# - extract_page_numbers()
# - ask_ollama_eda_insights()
# - ask_ollama_cluster_names()
```

---

## Skill File Structure

```
.opencode/skills/
├── analyze-dataset/
│   ├── skill.json          # Skill metadata
│   ├── instructions.md     # Instructions for Claude
│   ├── analyze.py          # Main analysis script
│   └── prompts/            # Ollama prompt templates
├── write-investigation/
│   ├── skill.json
│   ├── instructions.md
│   ├── writer.py
│   └── prompts/
├── build-html-page/
│   ├── skill.json
│   ├── instructions.md
│   ├── builder.py
│   └── templates/
└── deploy-investigation/
    ├── skill.json
    ├── instructions.md
    └── deploy.py
```

---

## Cost Savings with Ollama

### **Current Pipeline (All Claude):**
- AI writing: $0.02 per investigation
- Total: $0.02

### **Hybrid Pipeline (Ollama + Claude):**
- Ollama insights: FREE
- Ollama cluster names: FREE
- Ollama pull quotes: FREE
- Claude prose polish (optional): $0.02
- Total: $0.00 - $0.02

### **Full Ollama Pipeline:**
- Everything via Ollama: FREE
- Quality: 70-80% of Claude
- Speed: Faster (local GPU)
- Total: $0.00

---

## Next Steps (Priority Order)

### **Step 1: Create `ollama_helper.py`** ⭐⭐⭐
- Copy from playbook
- Test connection to 192.168.1.153:11434
- Verify models are available

### **Step 2: Create `analyze-dataset` skill** ⭐⭐⭐
- Combine analyze_v2.py + playbook EDA functions
- Add Ollama insight extraction
- Test on test_dataset_crashes.csv

### **Step 3: Create `write-investigation` skill** ⭐⭐
- Enhance ai_writer.py with Ollama option
- Add playbook headline formulas
- Let user choose Ollama (free) vs Claude (paid)

### **Step 4: Create `build-html-page` skill** ⭐⭐
- Rewrite chart rendering (inline JS like playbook)
- Add missing components (stat boxes, finding cards)
- Match playbook Phase 9 structure

### **Step 5: Create `deploy-investigation` skill** ⭐
- Integrate update_homepage.py
- Add git automation
- Add social post generation (Ollama)

---

## Testing Strategy

### **Test Dataset:** 
`test_dataset_crashes.csv` (5,000 NYC crashes)

### **Test Each Skill:**
1. Run skill individually
2. Verify outputs
3. Check Ollama connectivity
4. Compare quality vs manual/Claude

### **Full Pipeline Test:**
```bash
# With skills:
opencode skill:analyze-dataset test_dataset_crashes.csv
opencode skill:write-investigation
opencode skill:build-html-page
opencode skill:deploy-investigation

# Should produce Investigation #004 in <3 minutes
```

---

## Key Decisions Needed

1. **Ollama vs Claude for prose?**
   - Option A: Always use Ollama (free, faster)
   - Option B: Always use Claude (better quality)
   - Option C: Let user choose per investigation

2. **Chart rendering approach?**
   - Use playbook inline JS (more work, perfect match)
   - Keep Plotly export (easier, less perfect)

3. **Skill granularity?**
   - 4 big skills (as proposed)
   - More smaller skills (more modular)

---

## Expected Timeline

- **Today (Session 2):** Create ollama_helper + start analyze-dataset skill
- **Session 3:** Complete analyze-dataset + write-investigation skills
- **Session 4:** Build-html-page skill (chart rendering fix)
- **Session 5:** Deploy skill + full pipeline test

Total: 4-5 sessions to complete

---

## Success Criteria

✅ Skills work independently and together
✅ Ollama integration saves $0.02 per investigation
✅ Chart quality matches manual investigations
✅ Full pipeline: CSV → Published in <3 minutes
✅ Output quality: 90%+ of manual work

