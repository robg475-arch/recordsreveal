# Preview Workflow - Complete Guide

## What Changed

Your pipeline now includes a **preview-approve-reject workflow** that lets you review investigations locally before deploying to production (recordsreveal.com).

## New Pipeline Flow

```
Step 1-8: Generate Investigation (same as before)
   ↓
Step 9: Create Preview Branch (NEW!)
   ↓
Review Locally (you decide)
   ↓
Approve → Production  OR  Reject → Discard
```

## How To Use

### 1. Run Pipeline (Same as Before)

```bash
./run_full_pipeline.sh your_data.csv
```

**What's different:** At the end, you'll see:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    ✅ PIPELINE COMPLETE                              ║
╚══════════════════════════════════════════════════════════════════════╝

📊 Preview created successfully!
  • Branch: preview/investigation-20260522-083817
  • Review instructions: PREVIEW_investigation-20260522-083817.txt

🔍 Review locally:
  open investigations/investigation-20260522-083817.html
  python3 -m http.server 8000

✅ To approve and deploy to production:
  python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817

❌ To reject and discard changes:
  python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817
```

### 2. Review Locally

**Option A - Quick preview:**
```bash
open investigations/investigation-20260522-083817.html
```

**Option B - Full site preview:**
```bash
python3 -m http.server 8000
```
Then open: http://localhost:8000

**Check everything:**
- ✓ Hero image looks professional
- ✓ Article content is accurate
- ✓ Charts display correctly
- ✓ All links work
- ✓ Sidebar shows properly
- ✓ Mobile responsive (resize browser)
- ✓ Homepage updated correctly
- ✓ Footer counter incremented

### 3a. Approve & Deploy to Production

If everything looks good:

```bash
python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817
```

**What happens:**
1. Asks: "This will deploy to PRODUCTION. Continue? (yes/no)"
2. Type `yes`
3. Merges preview into main
4. Pushes to GitHub
5. Deploys to recordsreveal.com (via Cloudflare)
6. Deletes preview branch
7. Cleans up

**Result:** Investigation is LIVE at recordsreveal.com in ~30 seconds! 🎉

### 3b. Reject & Discard Changes

If you don't like it:

```bash
python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817
```

**What happens:**
1. Asks: "This will DELETE all changes. Continue? (yes/no)"
2. Type `yes`
3. Switches back to main
4. Deletes preview branch (local & remote)
5. Discards all changes
6. Cleans up

**Result:** Nothing changes in production. You can run the pipeline again if needed.

## Safety Features

✅ **Can't accidentally deploy** - Always asks for confirmation
✅ **Can't accidentally delete** - Always asks for confirmation
✅ **Can cancel anytime** - Just type `no` at the prompt
✅ **Nothing touches production** - Until you explicitly approve

## Example Session

```bash
# 1. Run pipeline
./run_full_pipeline.sh police_data.csv
# Wait ~90 seconds...

# 2. Review locally
open investigations/investigation-20260522-083817.html
# Looks good!

# 3. Deploy to production
python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817
# Type: yes

# 4. Done! Check it live
open https://recordsreveal.com
```

## What Gets Created

**Preview Branch (GitHub):**
- Name: `preview/investigation-YYYYMMDD-HHMMSS`
- Contains: All changes (new investigation, updated homepage, etc.)
- Temporary: Deleted after approve/reject

**Preview Instructions (Local):**
- File: `PREVIEW_investigation-YYYYMMDD-HHMMSS.txt`
- Contains: Review steps and commands
- Auto-deleted after approve/reject

## Common Questions

**Q: What if I want to make changes to the preview?**

A: You're already on the preview branch! Just edit and commit:
```bash
# Make your changes
git add .
git commit -m "Fix typo"
git push
# Then review again and approve
```

**Q: What if I lost the instructions?**

A: Check your current branch:
```bash
git branch --show-current
# Use that branch name in approve.py or reject.py
```

**Q: Can I have multiple previews at once?**

A: Yes! Each preview branch is independent. Just make sure to approve/reject them in order.

**Q: What if the pipeline fails at Step 9?**

A: Steps 1-8 still completed successfully. You have the HTML files. You can manually create a preview branch or just open the files directly.

**Q: Can I skip the preview and deploy directly?**

A: Not recommended, but you can manually merge to main:
```bash
git checkout main
git add .
git commit -m "Add investigation"
git push origin main
```

## Benefits

1. **No Mistakes** - Catch errors before they go live
2. **Safe Testing** - Test everything locally first
3. **Easy Rollback** - Just reject if you don't like it
4. **Peace of Mind** - Nothing goes live until you say so
5. **Professional Workflow** - Industry-standard preview → production flow

## Files Added

```
.opencode/skills/deploy-preview/
├── deploy.py           # Creates preview branch
├── approve.py          # Deploys to production
├── reject.py           # Discards changes
├── skill.json          # Metadata
├── README.md           # Documentation
└── WORKFLOW.md         # Visual workflow diagram
```

## Integration Status

✅ **Fully integrated** into `run_full_pipeline.sh` as Step 9
✅ **No manual setup** required
✅ **Works with all investigations**
✅ **Safe by default** - Always creates preview first

## Next Steps

Just use the pipeline as normal:

```bash
./run_full_pipeline.sh your_data.csv
```

The preview workflow is automatic! You'll see the review instructions at the end.

---

**Questions or issues?** Check the detailed docs:
- `.opencode/skills/deploy-preview/README.md`
- `.opencode/skills/deploy-preview/WORKFLOW.md`
