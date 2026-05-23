# Pre-Investigation Checklist
## Before Analyzing Your Next Dataset

**Purpose:** Ensure system readiness before starting a new investigation  
**Time:** 2 minutes  
**Run this before EVERY investigation**

---

## ✅ Quick System Check

### 1. API Keys Valid

```bash
# Check .env file exists and has keys
grep -q "ANTHROPIC_API_KEY" .env && echo "✅ Claude API key present" || echo "❌ Missing Claude API key"
grep -q "LEONARDO_API_KEY" .env && echo "✅ Leonardo.ai API key present" || echo "❌ Missing Leonardo.ai API key"
```

**Expected:** Both keys present

---

### 2. Ollama Server Accessible

```bash
# Test connection to remote Ollama
curl -s http://192.168.1.153:11434/api/tags | head -1
```

**Expected:** JSON response with models list

**If fails:**
- Check VPN/network connection
- Verify IP address: 192.168.1.153:11434
- Ensure qwen2.5-coder:7b model installed

---

### 3. Core Scripts Exist

```bash
ls -1 investigate.py render_complete.py render_hybrid.py 2>/dev/null | wc -l
```

**Expected:** 3

---

### 4. Documentation Ready

```bash
ls -1 LESSONS_LEARNED.md QUICK_START.md 2>/dev/null | wc -l
```

**Expected:** 2

---

### 5. Template Available

```bash
ls -1 investigations/dark-money-data-analysis.html 2>/dev/null | wc -l
```

**Expected:** 1

---

### 6. Directory Structure

```bash
mkdir -p data investigation_output investigations images/heroes
echo "✅ All directories ready"
```

**Expected:** No errors

---

## 📝 Investigation Preparation

### Have You Done This?

- [ ] **Dataset ready** - CSV file cleaned and in `data/` folder
- [ ] **Dataset reviewed** - Know column names, row count, data types
- [ ] **Investigation goal** - Clear idea what patterns to look for
- [ ] **Time allocated** - 1-2 hours available for complete workflow
- [ ] **LESSONS_LEARNED.md read** - Reviewed checklist before starting

---

## 🚀 Ready to Start?

### If ALL checks pass:

```bash
# Start investigation
python3 investigate.py data/YOUR_DATASET.csv
```

### If ANY check fails:

**Fix the issue first!** Don't proceed until all systems green.

---

## 📋 Post-Investigation Checklist

After running investigation, verify:

- [ ] JSON created in `investigation_output/`
- [ ] Headline makes sense
- [ ] Findings (3-7) are newsworthy
- [ ] Statistics cited in findings

Then proceed to rendering:

```bash
python3 render_complete.py investigation_output/investigation-*.json
```

---

## 🔍 Common Issues

### "Ollama connection refused"
**Fix:** Check network, VPN, IP address

### "Leonardo.ai credits exhausted"
**Fix:** Check https://app.leonardo.ai/settings - Renews monthly

### "Claude API rate limit"
**Fix:** Wait 1 minute, retry

### "CSV encoding error"
**Fix:** Convert to UTF-8: `iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv`

---

## 📚 Reference Documents

**Before investigation:**
- `LESSONS_LEARNED.md` - Complete workflow

**During investigation:**
- `QUICK_START.md` - Fast reference

**After investigation:**
- `END_TO_END_VERIFICATION.md` - Quality checks

---

**Last Updated:** May 23, 2026  
**Status:** Production Ready  
**Next:** Analyze your dataset!
