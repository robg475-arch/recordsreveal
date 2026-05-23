#!/usr/bin/env python3
"""
Approve and deploy preview to production
"""

import sys
import subprocess

def run_command(cmd, description=""):
    """Run a shell command"""
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python approve.py <preview_branch_name>")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    
    print("=" * 70)
    print("✅ APPROVING & DEPLOYING TO PRODUCTION")
    print("=" * 70)
    print(f"Branch: {branch_name}")
    print("=" * 70)
    
    # Confirm
    response = input("\n⚠️  This will deploy to PRODUCTION (recordsreveal.com). Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Deployment cancelled")
        sys.exit(0)
    
    print("\n📋 Deploying to production...")
    
    # Switch to main
    print("\n1️⃣ Switching to main branch...")
    run_command("git checkout main", "Checking out main")
    
    # Pull latest
    print("\n2️⃣ Pulling latest main...")
    run_command("git pull origin main", "Pulling main")
    
    # Merge preview branch
    print(f"\n3️⃣ Merging {branch_name} into main...")
    result = run_command(f"git merge {branch_name} --no-edit", f"Merging {branch_name}")
    
    if result is None:
        print("\n❌ Merge failed! Resolve conflicts manually.")
        sys.exit(1)
    
    # Push to production
    print("\n4️⃣ Pushing to production...")
    result = run_command("git push origin main", "Pushing to main")
    
    if result is None:
        print("\n❌ Push failed!")
        sys.exit(1)
    
    # Delete preview branch (local)
    print(f"\n5️⃣ Cleaning up preview branch...")
    run_command(f"git branch -d {branch_name}", f"Deleting local branch {branch_name}")
    
    # Delete preview branch (remote)
    run_command(f"git push origin --delete {branch_name}", f"Deleting remote branch {branch_name}")
    
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 70)
    print("\n✅ Changes are now live at: https://recordsreveal.com")
    print("✅ Preview branch deleted")
    print("✅ You are back on main branch")
    print("\n⏱️  Cloudflare will deploy in ~30 seconds")
    print()

if __name__ == "__main__":
    main()
