"""
Auto-Backup to GitHub
Automatically commits and pushes changes to GitHub
Run this periodically or add to scheduler
"""
import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_git_configured():
    """Check if git is properly configured"""
    if not os.path.exists('.git'):
        print("❌ Not a git repository")
        return False
    
    # Check remote
    success, output, _ = run_command("git remote -v")
    if not success or 'origin' not in output:
        print("❌ No GitHub remote configured")
        print("Configure with: git remote add origin https://github.com/USER/REPO.git")
        return False
    
    return True

def get_pending_changes():
    """Check if there are pending changes"""
    success, output, _ = run_command("git status --porcelain")
    if not success:
        return False
    
    return len(output.strip()) > 0

def auto_backup(message=None):
    """Perform automatic backup to GitHub"""
    print("="*60)
    print("  KALIN AI - AUTO BACKUP TO GITHUB")
    print("="*60)
    print()
    
    # Check git configuration
    if not check_git_configured():
        return False
    
    # Check for changes
    if not get_pending_changes():
        print("✅ No changes to backup")
        return True
    
    print("📦 Changes detected, creating backup...")
    print()
    
    # Add all changes
    print("1. Adding files...")
    success, _, stderr = run_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return False
    print("   ✅ Files added")
    
    # Create commit
    print("2. Creating commit...")
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🔄 Auto-backup: {timestamp}"
    
    success, _, stderr = run_command(f'git commit -m "{message}"')
    if not success:
        # Might be no changes after add
        if "nothing to commit" in stderr.lower():
            print("   ℹ️  Nothing to commit")
            return True
        print(f"❌ Failed to commit: {stderr}")
        return False
    print("   ✅ Commit created")
    
    # Push to GitHub
    print("3. Pushing to GitHub...")
    success, output, stderr = run_command("git push origin main")
    if not success:
        # Try master branch
        print("   ⚠️  Trying 'master' branch...")
        success, output, stderr = run_command("git push origin master")
        
        if not success:
            print(f"❌ Failed to push: {stderr}")
            print("   💡 Check your GitHub credentials and connection")
            return False
    
    print("   ✅ Pushed to GitHub")
    print()
    
    # Show summary
    print("="*60)
    print("  BACKUP SUCCESSFUL")
    print("="*60)
    print()
    print(f"Message: {message}")
    print()
    
    # Show recent commits
    success, output, _ = run_command("git log --oneline -3")
    if success:
        print("Recent commits:")
        print(output)
    
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-backup Kalin AI to GitHub')
    parser.add_argument('-m', '--message', help='Custom commit message')
    parser.add_argument('--force', action='store_true', help='Force backup even without changes')
    
    args = parser.parse_args()
    
    try:
        success = auto_backup(message=args.message)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Backup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
