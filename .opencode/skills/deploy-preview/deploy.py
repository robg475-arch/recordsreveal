#!/usr/bin/env python3
"""
RecordsReveal Deploy Preview Skill
Creates a preview branch with new investigation for review before production
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    if description:
        print(f"   {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr}")
        return None

def create_preview_branch(investigation_id):
    """Create a new preview branch for the investigation"""
    
    branch_name = f"preview/{investigation_id}"
    
    print(f"\n🌿 Creating preview branch: {branch_name}")
    
    # Check if we have uncommitted changes
    status = run_command("git status --porcelain")
    if status:
        print("   📝 Staging all changes...")
        run_command("git add .", "Adding files")
        
        commit_msg = f"Add investigation: {investigation_id}"
        run_command(f'git commit -m "{commit_msg}"', "Committing changes")
    
    # Create and checkout new branch
    current_branch = run_command("git branch --show-current")
    
    if current_branch != "main":
        print(f"   ⚠️  Currently on branch: {current_branch}")
        print(f"   🔄 Switching to main first...")
        run_command("git checkout main", "Switching to main")
        run_command("git pull origin main", "Pulling latest main")
    
    # Create preview branch
    run_command(f"git checkout -b {branch_name}", f"Creating branch {branch_name}")
    
    return branch_name

def push_preview_branch(branch_name):
    """Push preview branch to GitHub"""
    
    print(f"\n📤 Pushing preview branch to GitHub...")
    
    result = run_command(
        f"git push -u origin {branch_name}",
        f"Pushing {branch_name}"
    )
    
    if result is not None:
        print(f"   ✅ Branch pushed successfully")
        return True
    else:
        print(f"   ❌ Failed to push branch")
        return False

def create_preview_instructions(investigation_id, branch_name, html_file):
    """Create instructions for reviewing the preview"""
    
    print(f"\n📋 Creating preview instructions...")
    
    # Get the investigation title from HTML file
    title = "New Investigation"
    try:
        with open(html_file, 'r') as f:
            content = f.read()
            if '<title>' in content:
                title = content.split('<title>')[1].split('</title>')[0]
                title = title.replace(' | RecordsReveal', '')
    except:
        pass
    
    instructions = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    PREVIEW READY FOR REVIEW                          ║
╚══════════════════════════════════════════════════════════════════════╝

Investigation: {title}
Branch: {branch_name}
File: {html_file}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: REVIEW LOCALLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open in your browser:
  open {html_file}

Or view the entire site locally:
  python3 -m http.server 8000
  
Then visit: http://localhost:8000

Review:
  ✓ Hero image looks good
  ✓ Article content is accurate
  ✓ Charts display correctly
  ✓ Links work
  ✓ Sidebar shows up
  ✓ Mobile responsive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2A: APPROVE & DEPLOY TO PRODUCTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you like it, run:
  python3 .opencode/skills/deploy-preview/approve.py {branch_name}

This will:
  1. Merge {branch_name} into main
  2. Push to production (recordsreveal.com)
  3. Delete the preview branch
  4. Clean up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2B: REJECT & DISCARD CHANGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you don't like it, run:
  python3 .opencode/skills/deploy-preview/reject.py {branch_name}

This will:
  1. Switch back to main
  2. Delete the preview branch (local & remote)
  3. Discard all changes
  4. Clean up

Nothing will be deployed to production.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    print(instructions)
    
    # Save to file
    preview_file = f"PREVIEW_{investigation_id}.txt"
    with open(preview_file, 'w') as f:
        f.write(instructions)
    
    print(f"\n💾 Instructions saved to: {preview_file}")
    
    return preview_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy.py <investigation_html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        print(f"❌ Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    # Extract investigation ID from filename
    investigation_id = os.path.basename(html_file).replace('.html', '')
    
    print("=" * 70)
    print("🚀 RECORDSREVEAL DEPLOY PREVIEW")
    print("=" * 70)
    print(f"Investigation: {investigation_id}")
    print(f"HTML file: {html_file}")
    print("=" * 70)
    
    # Create preview branch
    branch_name = create_preview_branch(investigation_id)
    
    if not branch_name:
        print("\n❌ Failed to create preview branch")
        sys.exit(1)
    
    # Push to GitHub
    if not push_preview_branch(branch_name):
        print("\n❌ Failed to push preview branch")
        sys.exit(1)
    
    # Create instructions
    create_preview_instructions(investigation_id, branch_name, html_file)
    
    print("\n✅ Preview branch created successfully!")
    print(f"\nYou are now on branch: {branch_name}")
    print(f"Review the changes and then approve or reject.")

if __name__ == "__main__":
    main()
