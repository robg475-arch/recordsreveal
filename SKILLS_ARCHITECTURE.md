# RecordsReveal Skills Architecture - Visual Reference

## Complete Pipeline Flow

```
CSV → profile → [temporal, geographic, classification, clustering] → merge → write → build-html → deploy → LIVE SITE
```

## Skills Summary Table

| # | Skill Name | Status | Input | Output | Time | Cost |
|---|------------|--------|-------|--------|------|------|
| 1 | profile-dataset | ✅ Built | CSV | profile.json, recommendations.json | 5s | $0.00 |
| 2 | temporal-analysis | ✅ Built | CSV + time_col | temporal_insights.json | 30s | $0.00 |
| 3 | geographic-analysis | ✅ Built | CSV + lat/lon | geographic_insights.json | 45s | $0.00 |
| - | merge-insights | ✅ Built | *_insights.json | combined_insights.json | 1s | $0.00 |
| 4 | classification-analysis | ⏳ Future | CSV + target | classification_insights.json | 90s | $0.00 |
| 5 | clustering-analysis | ⏳ Future | CSV | clustering_insights.json | 60s | $0.00 |
| 6 | write-investigation | ⏳ Future | combined_insights.json | article_content.json | 45s | $0-0.02 |
| 7 | build-html-page | ⏳ Future | article + insights | investigation-XXX.html | 20s | $0.00 |
| 8 | deploy-investigation | ⏳ Future | HTML | Live website | 30s | $0.00 |

**Total Time**: ~5.5 minutes  
**Total Cost**: $0.00 - $0.02

## Session 2 Accomplishments

### ✅ Built (4 components)
1. **profile-dataset** - Smart profiler that recommends analyses
2. **temporal-analysis** - Time patterns + Ollama insights
3. **geographic-analysis** - Location patterns + Ollama insights
4. **merge-insights** - Combines all analyses into one JSON

### ✅ Validated
- Tested on NYC Crashes dataset (5,000 records)
- Tested on 911 Calls dataset (3,000 records)
- Both produced complete `combined_insights.json` files ready for article writing

### 📊 Files Created
- `ollama_helper.py` (Ollama integration)
- `.opencode/skills/profile-dataset/` (profile.py, skill.json, instructions.md)
- `.opencode/skills/temporal-analysis/` (analyze.py, skill.json)
- `.opencode/skills/geographic-analysis/` (analyze.py, skill.json)
- `merge_insights.py` (combiner script)
- `test_dataset_911calls.csv` (validation dataset)
- `MODULAR_SKILLS_SUMMARY.md` (documentation)
- `SKILLS_ARCHITECTURE.md` (this file)

## Next Session Priority

**Skill 6: write-investigation** - The bridge between analysis and publishing!

This skill will:
- Read `combined_insights.json`
- Generate journalism prose (headline, lede, findings, quotes)
- Output `article_content.json`
- Use Ollama (free) or Claude ($0.02) for prose quality

Once this is built, we can go from CSV → published article in one pipeline!
