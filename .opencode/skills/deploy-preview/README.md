# Deploy Preview Skill

Preview investigations locally before deploying to production (recordsreveal.com).

## How It Works

```
Pipeline → Preview Branch → Local Review → Approve/Reject
                                          ↓           ↓
                                    Production    Discard
```

## Usage

### Step 1: Create Preview (Automatic in Pipeline)

The pipeline automatically creates a preview branch:

```bash
./run_full_pipeline.sh your_data.csv
```

At the end, you'll see:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    PREVIEW READY FOR REVIEW                          ║
╚══════════════════════════════════════════════════════════════════════╝

Investigation: Police Use of Force in NYC
Branch: preview/investigation-20260522-083817

STEP 1: REVIEW LOCALLY
  open investigations/investigation-20260522-083817.html
  
STEP 2A: APPROVE & DEPLOY
  python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817
  
STEP 2B: REJECT & DISCARD
  python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817
```

### Step 2: Review Locally

**Option A - Direct file:**
```bash
open investigations/investigation-20260522-083817.html
```

**Option B - Local web server:**
```bash
python3 -m http.server 8000
```
Then visit: http://localhost:8000

**Check:**
- ✓ Hero image looks good
- ✓ Article content is accurate
- ✓ Charts display correctly
- ✓ Links work
- ✓ Sidebar shows up
- ✓ Mobile responsive
- ✓ Homepage updated correctly
- ✓ Footer counter incremented

### Step 3A: Approve & Deploy to Production

If everything looks good:

```bash
python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817
```

This will:
1. ✅ Merge preview branch into `main`
2. ✅ Push to production (GitHub)
3. ✅ Deploy to recordsreveal.com (via Cloudflare)
4. ✅ Delete preview branch
5. ✅ Clean up

**Result:** Investigation is LIVE at recordsreveal.com in ~30 seconds!

### Step 3B: Reject & Discard Changes

If you don't like it:

```bash
python3 .opencode/skills/deploy-preview/reject.py preview/investigation-20260522-083817
```

This will:
1. ✅ Switch back to `main`
2. ✅ Delete preview branch (local & remote)
3. ✅ Discard ALL changes
4. ✅ Clean up

**Result:** Nothing changes in production. Start over if needed.

## Manual Usage

If you need to create a preview manually:

```bash
python3 .opencode/skills/deploy-preview/deploy.py investigations/investigation-20260522-083817.html
```

## What Gets Created

**Preview Branch:**
- Name: `preview/investigation-YYYYMMDD-HHMMSS`
- Location: GitHub repository
- Contains: New investigation + all updated files (index.html, registry, etc.)

**Instructions File:**
- Name: `PREVIEW_investigation-YYYYMMDD-HHMMSS.txt`
- Contains: Review steps and approve/reject commands
- Auto-deleted after approval/rejection

## Safety Features

**Before Approval:**
- ✅ Confirmation prompt: "This will deploy to PRODUCTION. Continue?"
- ✅ Shows exactly what will be deployed
- ✅ Can cancel at any time

**Before Rejection:**
- ✅ Confirmation prompt: "This will DELETE all changes. Continue?"
- ✅ Can cancel at any time

**No Accidents:**
- ❌ Can't accidentally deploy
- ❌ Can't accidentally delete
- ❌ Always asks for confirmation

## Benefits

1. **Review First** - See exactly what will go live
2. **No Mistakes** - Catch errors before production
3. **Safe Testing** - Test locally without affecting live site
4. **Easy Rollback** - Just reject if you don't like it
5. **Clean Workflow** - One command to approve or reject

## Integration with Pipeline

Fully integrated into `run_full_pipeline.sh` as final step (Step 9).

No manual work required - just review and approve/reject!

## Example Session

```bash
# Run pipeline
./run_full_pipeline.sh police_data.csv

# Review locally
open investigations/investigation-20260522-083817.html

# Looks good? Deploy!
python3 .opencode/skills/deploy-preview/approve.py preview/investigation-20260522-083817

# Done! Live at recordsreveal.com
```

## Troubleshooting

**Preview branch already exists?**
```bash
git branch -D preview/investigation-20260522-083817
git push origin --delete preview/investigation-20260522-083817
```

**Want to make changes to preview?**
```bash
# You're already on the preview branch
# Just make your edits and commit
git add .
git commit -m "Fix typo"
```

**Lost the preview instructions?**
```bash
# Check your current branch
git branch --show-current

# If you're on preview/..., you can approve/reject using that name
```
