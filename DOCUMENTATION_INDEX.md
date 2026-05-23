# RecordsReveal Documentation Index
## Find What You Need Fast

**Last Updated:** May 23, 2026

---

## 🚦 Start Here

### New to RecordsReveal?
👉 **[README.md](README.md)** - Project overview, features, tech stack

### Want to run your first investigation?
👉 **[QUICK_START.md](QUICK_START.md)** - 30-second checklist, 4-hour workflow

### Running your SECOND investigation?
👉 **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** ⭐ - Complete QA checklist, common pitfalls

---

## 📚 By Use Case

### "I want to analyze a new dataset"
1. [QUICK_START.md](QUICK_START.md) - Fast workflow
2. [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Quality checklist
3. Template: `investigations/dark-money-data-analysis.html`

### "I need to understand how the AI works"
1. [NEW_WORKFLOW.md](NEW_WORKFLOW.md) - System architecture
2. [PROMPT_CHAIN.md](PROMPT_CHAIN.md) - Exact AI prompts
3. [methodology.html](methodology.html) - Public methodology page

### "I want to customize the output"
1. [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) - All features explained
2. `render_complete.py` - Main rendering script
3. [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Design standards

### "Something broke, how do I fix it?"
1. [QUICK_START.md](QUICK_START.md) - Troubleshooting section
2. [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Common mistakes
3. [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) - FAQ section

### "I want to see an example"
1. `investigations/investigation-20260523-133019.html` - Main investigation
2. `investigations/dark-money-data-analysis.html` - Data science deep dive
3. `investigation_output/investigation-20260523-090450.json` - Raw data

---

## 📖 Complete Documentation

### Core Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **[README.md](README.md)** | Project overview | First time setup |
| **[QUICK_START.md](QUICK_START.md)** | Fast workflow guide | Every investigation |
| **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** ⭐ | Complete checklist | MUST READ before 2nd investigation |
| **[COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md)** | Detailed feature guide | When you need details |
| **[NEW_WORKFLOW.md](NEW_WORKFLOW.md)** | System architecture | Understanding the system |
| **[PROMPT_CHAIN.md](PROMPT_CHAIN.md)** | AI prompts | Modifying AI behavior |

### Public Pages

| File | Purpose | Audience |
|------|---------|----------|
| **[methodology.html](methodology.html)** | General methodology | Public (data scientists) |
| **investigations/dark-money-data-analysis.html** | Specific investigation | Public (deep dive template) |

---

## 🎯 By Experience Level

### Beginner (First Investigation)
1. Read: [README.md](README.md)
2. Follow: [QUICK_START.md](QUICK_START.md)
3. Reference: [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md)

**Time:** 4-6 hours  
**Output:** Basic investigation without data science page

### Intermediate (Second+ Investigation)
1. Review: [LESSONS_LEARNED.md](LESSONS_LEARNED.md)
2. Follow: [QUICK_START.md](QUICK_START.md)
3. Create: Data science deep dive from template

**Time:** 2-4 hours  
**Output:** Complete investigation with deep dive

### Advanced (Customization)
1. Study: [NEW_WORKFLOW.md](NEW_WORKFLOW.md)
2. Modify: [PROMPT_CHAIN.md](PROMPT_CHAIN.md)
3. Edit: `render_complete.py`, `investigate.py`

**Time:** Variable  
**Output:** Custom workflows and designs

---

## 🔍 By Topic

### Workflow & Process
- [QUICK_START.md](QUICK_START.md) - Fast reference
- [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) - Detailed steps
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Best practices

### AI & Prompts
- [NEW_WORKFLOW.md](NEW_WORKFLOW.md) - AI architecture
- [PROMPT_CHAIN.md](PROMPT_CHAIN.md) - Exact prompts
- [methodology.html](methodology.html) - Public explanation

### Design & Layout
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Design standards
- [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) - Customization guide
- `render_complete.py` - Implementation

### Data Science Deep Dives
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Creation checklist
- `investigations/dark-money-data-analysis.html` - Template
- [methodology.html](methodology.html) - Statistical methods

### Technical Setup
- [README.md](README.md) - Requirements & installation
- [QUICK_START.md](QUICK_START.md) - Troubleshooting
- `.env.example` - API keys needed

---

## 🎓 Learning Path

### Week 1: Understanding
- [ ] Read [README.md](README.md) completely
- [ ] Skim [NEW_WORKFLOW.md](NEW_WORKFLOW.md) for architecture
- [ ] Review example: `investigations/investigation-20260523-133019.html`

### Week 2: First Investigation
- [ ] Follow [QUICK_START.md](QUICK_START.md) with sample data
- [ ] Create basic investigation (skip data science page)
- [ ] Review output, identify improvements

### Week 3: Complete Workflow
- [ ] Study [LESSONS_LEARNED.md](LESSONS_LEARNED.md) in detail
- [ ] Run second investigation with ALL steps
- [ ] Create data science deep dive from template
- [ ] QA checklist before publishing

### Week 4: Mastery
- [ ] Understand [PROMPT_CHAIN.md](PROMPT_CHAIN.md)
- [ ] Customize prompts for your needs
- [ ] Modify design in `render_complete.py`
- [ ] Document your changes

---

## 📊 Documentation Stats

| Metric | Count |
|--------|-------|
| **Total documentation files** | 6 core + 2 public |
| **Total pages** | ~8,000 words |
| **Code files** | 3 main scripts |
| **Templates** | 1 (data science deep dive) |
| **Examples** | 1 complete investigation |

---

## 🔄 Update History

| Date | Update | Files Changed |
|------|--------|---------------|
| May 23, 2026 | Complete system documentation | All files created |
| May 23, 2026 | Added data science deep dives | LESSONS_LEARNED.md, template |
| May 23, 2026 | Fixed sidebar scrolling | render_complete.py |

---

## 🚀 Quick Command Reference

```bash
# Investigation
python3 investigate.py data/your_data.csv

# Render (complete)
python3 render_complete.py investigation_output/investigation-*.json

# Render (fast)
python3 render_hybrid.py investigation_output/investigation-*.json

# Create data science page
cp investigations/dark-money-data-analysis.html \
   investigations/your-topic-data-analysis.html

# Verify output
open investigations/investigation-*.html
open investigations/*-data-analysis.html

# Deploy
git add . && git commit -m "Investigation: [Topic]" && git push
```

---

## ❓ Common Questions

### "Which doc should I read first?"
**[QUICK_START.md](QUICK_START.md)** - Gets you running fastest

### "What's the most important doc?"
**[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** - Prevents mistakes, saves hours

### "How do I customize the AI?"
**[PROMPT_CHAIN.md](PROMPT_CHAIN.md)** - All prompts documented

### "What if something breaks?"
**[QUICK_START.md](QUICK_START.md)** - Troubleshooting section

### "Where's the example?"
**`investigations/investigation-20260523-133019.html`** - Complete example

---

## 📧 Support

**Can't find what you need?**
- Email: data@recordsreveal.com
- Check: [LESSONS_LEARNED.md](LESSONS_LEARNED.md) FAQ section
- Review: [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) troubleshooting

---

## ✅ Documentation Completeness Checklist

- [x] Project overview (README.md)
- [x] Quick start guide (QUICK_START.md)
- [x] Complete workflow (COMPLETE_WORKFLOW.md)
- [x] Lessons learned (LESSONS_LEARNED.md)
- [x] System architecture (NEW_WORKFLOW.md)
- [x] AI prompts (PROMPT_CHAIN.md)
- [x] Public methodology (methodology.html)
- [x] Data science template (dark-money-data-analysis.html)
- [x] This index (DOCUMENTATION_INDEX.md)

**Status:** ✅ Complete

---

## 🎯 TL;DR

**First investigation?** → [QUICK_START.md](QUICK_START.md)  
**Second investigation?** → [LESSONS_LEARNED.md](LESSONS_LEARNED.md) ⭐  
**Need details?** → [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md)  
**Customizing AI?** → [PROMPT_CHAIN.md](PROMPT_CHAIN.md)  
**Understanding system?** → [NEW_WORKFLOW.md](NEW_WORKFLOW.md)

**Most important:** [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - Read before 2nd investigation!

---

**Navigation:**
- [← Back to README](README.md)
- [Quick Start →](QUICK_START.md)
- [Lessons Learned →](LESSONS_LEARNED.md)
