# Preview & Deploy Workflow

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RUN FULL PIPELINE                              │
│                   ./run_full_pipeline.sh                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Profile Data           → profile.json                       │
│ STEP 2: Run 5 Analyses         → 5 analysis JSONs                   │
│ STEP 3: Merge Insights         → combined_insights.json             │
│ STEP 4: Extract Page Data      → page_data.json                     │
│ STEP 5: Write Article (Claude) → article_content.json               │
│ STEP 5.5: Generate Hero Image  → images/heroes/{id}.jpg             │
│ STEP 6: Build HTML Page        → investigation-{id}.html            │
│ STEP 7: Build Technical Page   → investigation-{id}-technical.html  │
│ STEP 8: Update Homepage        → index.html (updated)               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: CREATE PREVIEW BRANCH                                       │
│                                                                     │
│  • Creates: preview/investigation-{id}                              │
│  • Commits all changes                                              │
│  • Pushes to GitHub                                                 │
│  • Generates review instructions                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        REVIEW LOCALLY                               │
│                                                                     │
│  Option A: open investigations/investigation-{id}.html              │
│  Option B: python3 -m http.server 8000                              │
│            → http://localhost:8000                                  │
│                                                                     │
│  Check:                                                             │
│   ✓ Hero image                                                      │
│   ✓ Article content                                                 │
│   ✓ Charts & data                                                   │
│   ✓ Sidebar                                                         │
│   ✓ Links                                                           │
│   ✓ Mobile responsive                                               │
│   ✓ Homepage updated                                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
              ✅ APPROVE          ❌ REJECT
                    │                   │
                    ↓                   ↓
    ┌───────────────────────┐   ┌──────────────────┐
    │ approve.py            │   │ reject.py        │
    │                       │   │                  │
    │ 1. Switch to main     │   │ 1. Switch to main│
    │ 2. Merge preview      │   │ 2. Delete preview│
    │ 3. Push to production │   │    (local)       │
    │ 4. Delete preview     │   │ 3. Delete preview│
    │    branch             │   │    (remote)      │
    │ 5. Clean up           │   │ 4. Clean up      │
    └───────────────────────┘   └──────────────────┘
                    │                   │
                    ↓                   ↓
    ┌───────────────────────┐   ┌──────────────────┐
    │ 🎉 LIVE!              │   │ ❌ DISCARDED     │
    │                       │   │                  │
    │ recordsreveal.com     │   │ Nothing changed  │
    │ (30 seconds)          │   │ in production    │
    └───────────────────────┘   └──────────────────┘
```

## Branch Strategy

### Main Branch (Production)
- **Name:** `main`
- **Status:** Protected
- **Purpose:** Production code (live at recordsreveal.com)
- **Updates:** Only via approved preview branches

### Preview Branches
- **Name:** `preview/investigation-YYYYMMDD-HHMMSS`
- **Status:** Temporary
- **Purpose:** Review before production
- **Lifetime:** Created → Reviewed → Merged/Deleted

## Commands Summary

```bash
# 1. Run pipeline (creates preview automatically)
./run_full_pipeline.sh your_data.csv

# 2. Review locally
open investigations/investigation-20260522-083817.html
# or
python3 -m http.server 8000

# 3a. Approve & deploy
python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817

# 3b. Reject & discard
python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817
```

## Safety Checkpoints

### ✅ Before Creating Preview
- All changes are committed
- Preview branch is created
- Nothing touches production yet

### ✅ Before Approving
- Manual review required
- Confirmation prompt: "Deploy to PRODUCTION?"
- Can cancel at any time

### ✅ Before Rejecting
- Manual review required
- Confirmation prompt: "DELETE all changes?"
- Can cancel at any time

## File Structure

```
recordsreveal-site/
├── investigations/
│   ├── investigation-20260522-083817.html      # Journalism page
│   └── investigation-20260522-083817-technical.html  # Technical page
├── images/
│   └── heroes/
│       └── investigation-20260522-083817.jpg   # Hero image
├── index.html                                  # Updated homepage
├── investigations_registry.json                # Updated registry
└── PREVIEW_investigation-20260522-083817.txt   # Review instructions
```

## Timeline Example

```
09:00 AM - Run pipeline: ./run_full_pipeline.sh police_data.csv
09:02 AM - Pipeline complete, preview branch created
09:05 AM - Review investigation locally
09:10 AM - Looks good! Run approve.py
09:11 AM - LIVE at recordsreveal.com
```

## Recovery Scenarios

### Scenario 1: Made a mistake in preview
```bash
# You're already on the preview branch, just fix it
git add .
git commit -m "Fix typo"
git push
# Review again, then approve
```

### Scenario 2: Want to start over
```bash
# Reject the preview
python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817

# Run pipeline again
./run_full_pipeline.sh your_data.csv
```

### Scenario 3: Deployed but want to rollback
```bash
# Check git history
git log --oneline -5

# Revert the merge commit
git revert <merge-commit-sha>
git push origin main

# Or reset to previous commit (dangerous!)
git reset --hard <previous-commit-sha>
git push origin main --force
```

## Best Practices

1. **Always review locally** before approving
2. **Test on mobile** (resize browser window)
3. **Check all links** work correctly
4. **Verify data accuracy** in charts
5. **Read the full article** for typos
6. **Check homepage** is updated correctly
7. **When in doubt, reject** and regenerate

## What Gets Deployed

When you approve:
- ✅ New investigation HTML (journalism + technical)
- ✅ New hero image
- ✅ Updated homepage (index.html)
- ✅ Updated registry (investigations_registry.json)
- ✅ Any other changed files

When you reject:
- ❌ Nothing (all changes discarded)
