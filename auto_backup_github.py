"""
Auto-Backup to GitHub
Automatically commits and pushes changes to GitHub
Excludes temporary files, logs, sessions, and other non-essential files
Run this periodically or add to scheduler
"""
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=False,  # Más seguro
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120  # Aumentado a 2 minutos para repos grandes
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out (120s)"
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
    """Check if there are pending changes (excluding ignored files)"""
    success, output, _ = run_command(["git", "status", "--porcelain"])
    if not success:
        return False, []
    
    # Parse changes
    changes = []
    for line in output.strip().split('\n'):
        if line.strip():
            status = line[:2].strip()
            file = line[3:].strip()
            changes.append({'status': status, 'file': file})
    
    return len(changes) > 0, changes

def filter_important_files(changes):
    """Filter to show only important files in summary"""
    # Archivos que SÍ queremos mostrar en el resumen
    important_extensions = {'.py', '.html', '.js', '.css', '.md', '.txt', '.json', '.yml', '.yaml'}
    important_folders = {'agent', 'templates', 'static', 'plugins'}
    
    important = []
    ignored_count = 0
    
    for change in changes:
        file = change['file']
        ext = Path(file).suffix.lower()
        parent = Path(file).parts[0] if Path(file).parts else ''
        
        # Incluir si es extensión importante o está en carpeta importante
        if ext in important_extensions or parent in important_folders:
            important.append(change)
        else:
            ignored_count += 1
    
    return important, ignored_count

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
    has_changes, changes = get_pending_changes()
    if not has_changes:
        print("✅ No changes to backup")
        return True
    
    print(f"📦 Changes detected: {len(changes)} file(s)")
    print()
    
    # Show important files summary
    important_files, ignored_count = filter_important_files(changes)
    if important_files:
        print("📝 Important files changed:")
        for change in important_files[:10]:  # Mostrar máximo 10
            status_icon = "✨" if change['status'] == 'A' else "📝" if change['status'] == 'M' else "🗑️"
            print(f"   {status_icon} {change['file']}")
        if len(important_files) > 10:
            print(f"   ... and {len(important_files) - 10} more")
        if ignored_count > 0:
            print(f"\n   (Ignored {ignored_count} temporary/cache files)")
        print()
    
    # Add all changes
    print("1. Adding files...")
    success, _, stderr = run_command(["git", "add", "."])
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return False
    print("   ✅ Files added")
    
    # Create commit
    print("2. Creating commit...")
    if not message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        # Generar mensaje inteligente basado en cambios
        if important_files:
            modified_py = sum(1 for c in important_files if c['file'].endswith('.py') and c['status'] == 'M')
            added_files = sum(1 for c in important_files if c['status'] == 'A')
            
            if modified_py > 0:
                message = f"🔄 Update: {modified_py} Python file(s) modified"
            elif added_files > 0:
                message = f"✨ New: {added_files} file(s) added"
            else:
                message = f"📝 Updates: {len(important_files)} file(s) changed"
        else:
            message = f"🔄 Auto-backup: {timestamp}"
    
    success, _, stderr = run_command(["git", "commit", "-m", message])
    if not success:
        # Might be no changes after add
        if "nothing to commit" in stderr.lower():
            print("   ℹ️  Nothing to commit")
            return True
        print(f"❌ Failed to commit: {stderr}")
        return False
    print("   ✅ Commit created")
    
    # Detect current branch
    print("3. Detecting branch...")
    success, branch_output, _ = run_command(["git", "branch", "--show-current"])
    current_branch = branch_output.strip() if success else "main"
    print(f"   📍 Branch: {current_branch}")
    
    # Push to GitHub
    print(f"4. Pushing to GitHub ({current_branch})...")
    success, output, stderr = run_command(["git", "push", "origin", current_branch])
    if not success:
        print(f"❌ Failed to push: {stderr}")
        print("   💡 Check your GitHub credentials and connection")
        print("   💡 Try: git push --set-upstream origin " + current_branch)
        return False
    
    print("   ✅ Pushed to GitHub")
    print()
    
    # Show summary
    print("="*60)
    print("  ✅ BACKUP SUCCESSFUL")
    print("="*60)
    print()
    print(f"Message: {message}")
    print(f"Branch: {current_branch}")
    print()
    
    # Show recent commits
    success, output, _ = run_command(["git", "log", "--oneline", "-3"])
    if success:
        print("Recent commits:")
        for line in output.strip().split('\n'):
            print(f"   {line}")
    
    print()
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
