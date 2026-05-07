# GitHub Auto-Backup Guide

## Current Status
❌ **No automatic backup is configured** - You need to set it up manually.

## Setup Options

### Option 1: Manual Backup (Simple)
Run this command whenever you want to backup:
```bash
python auto_backup_github.py
```
Or double-click: `auto_backup.bat`

### Option 2: Automatic Backup (Recommended)
Configure Windows Task Scheduler to backup automatically:

```bash
# Run setup script (requires Administrator)
python setup_auto_backup.py
```

This will guide you through setting up automatic backups with these options:
- ⏰ Every hour
- ⏰ Every 4 hours  
- ⏰ Twice daily (9 AM, 6 PM) ← **Default**
- ⏰ Daily at 6 PM

### Option 3: Git Hook (Advanced)
Add to `.git/hooks/post-commit`:
```bash
#!/bin/bash
cd /e/kalin
python auto_backup_github.py --force
```

## Prerequisites

Before using auto-backup, ensure:

1. **Git is installed**
   ```bash
   git --version
   ```

2. **GitHub remote is configured**
   ```bash
   git remote -v
   ```
   
   If not configured:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   ```

3. **You're authenticated with GitHub**
   ```bash
   # Test authentication
   git push --dry-run
   ```

## Usage Examples

### Manual Backup
```bash
# Simple backup with auto message
python auto_backup_github.py

# Custom commit message
python auto_backup_github.py -m "Fixed bug in executor.py"

# Force backup even without changes
python auto_backup_github.py --force
```

### Scheduled Backup
After running `setup_auto_backup.py`, backups happen automatically.

To check scheduled tasks:
```bash
schtasks /query /tn "Kalin Auto-Backup"
```

To delete scheduled task:
```bash
schtasks /delete /tn "Kalin Auto-Backup" /f
```

## How It Works

1. **Check for changes** - Only backs up if files changed
2. **Add all files** - `git add .`
3. **Create commit** - With timestamp or custom message
4. **Push to GitHub** - Pushes to `main` or `master` branch
5. **Show summary** - Displays recent commits

## Troubleshooting

### Error: "No GitHub remote configured"
```bash
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### Error: "Authentication failed"
```bash
# Use GitHub Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

### Error: "Permission denied"
Run as Administrator or use your user account:
```bash
# Change task to run as current user
schtasks /change /tn "Kalin Auto-Backup" /ru YOUR_USERNAME
```

### Backup runs but nothing happens
Check if there are actual changes:
```bash
git status
```

If no changes, backup correctly skips.

## Best Practices

✅ **Commit often** - Small, frequent backups are better  
✅ **Use meaningful messages** - Describe what changed  
✅ **Review before pushing** - Check `git status` first  
✅ **Keep .env private** - Already in .gitignore  
✅ **Test after restore** - Verify code works after pulling  

❌ **Don't backup secrets** - API keys, passwords  
❌ **Don't force push** - Can lose history  
❌ **Don't ignore errors** - Fix authentication issues  

## Monitoring Backups

### Check last backup
```bash
git log -1 --oneline
```

### View backup history
```bash
git log --oneline -10
```

### See what will be backed up
```bash
git status
```

## Files Created

- ✅ `auto_backup_github.py` - Main backup script
- ✅ `auto_backup.bat` - Quick batch file
- ✅ `setup_auto_backup.py` - Scheduler setup wizard
- ✅ `GITHUB_AUTO_BACKUP.md` - This guide

## Security Notes

⚠️ **Important**: 
- Never commit `.env` file (contains API keys)
- Use GitHub Personal Access Tokens for authentication
- Review commits before pushing sensitive projects
- Consider making repo private if contains proprietary code

## Next Steps

1. **Setup GitHub repository** (if not done):
   ```bash
   git init
   git remote add origin https://github.com/USERNAME/kalin.git
   ```

2. **Configure automatic backup**:
   ```bash
   python setup_auto_backup.py
   ```

3. **Test manual backup**:
   ```bash
   python auto_backup_github.py -m "Initial setup"
   ```

4. **Verify on GitHub**:
   - Visit your repository
   - Check commits tab
   - Confirm files uploaded

---

*For questions or issues, check logs in console output*
