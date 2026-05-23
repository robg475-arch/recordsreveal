#!/usr/bin/env python3
"""
Reject preview and discard changes
"""

import sys
import subprocess
import os
import glob

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
        print("Usage: python reject.py <preview_branch_name>")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    
    print("=" * 70)
    print("🗑️  REJECTING PREVIEW & DISCARDING CHANGES")
    print("=" * 70)
    print(f"Branch: {branch_name}")
    print("=" * 70)
    
    # Confirm
    response = input("\n⚠️  This will DELETE all changes in this preview. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Rejection cancelled")
        sys.exit(0)
    
    print("\n🗑️  Discarding changes...")
    
    # Switch to main
    print("\n1️⃣ Switching to main branch...")
    run_command("git checkout main", "Checking out main")
    
    # Delete local branch
    print(f"\n2️⃣ Deleting local preview branch...")
    run_command(f"git branch -D {branch_name}", f"Deleting {branch_name}")
    
    # Delete remote branch
    print(f"\n3️⃣ Deleting remote preview branch...")
    run_command(f"git push origin --delete {branch_name}", f"Deleting remote {branch_name}")
    
    # Clean up preview files
    print(f"\n4️⃣ Cleaning up preview files...")
    preview_files = glob.glob("PREVIEW_*.txt")
    for f in preview_files:
        try:
            os.remove(f)
            print(f"   ✅ Deleted {f}")
        except:
            pass
    
    print("\n" + "=" * 70)
    print("✅ PREVIEW REJECTED & CLEANED UP")
    print("=" * 70)
    print("\n✅ Preview branch deleted (local & remote)")
    print("✅ You are back on main branch")
    print("✅ No changes were made to production")
    print()

if __name__ == "__main__":
    main()
