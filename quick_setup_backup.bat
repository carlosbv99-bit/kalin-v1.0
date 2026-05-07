@echo off
REM Quick Setup for GitHub Auto-Backup
REM Run this to configure automatic backups

echo ========================================
echo KALIN AI - QUICK BACKUP SETUP
echo ========================================
echo.

REM Step 1: Check Git
echo [1/4] Checking Git installation...
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed!
    echo Download from: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo OK - Git found
echo.

REM Step 2: Check if git repo exists
echo [2/4] Checking Git repository...
if not exist .git (
    echo Initializing Git repository...
    git init
    echo OK - Repository initialized
) else (
    echo OK - Repository exists
)
echo.

REM Step 3: Check remote
echo [3/4] Checking GitHub remote...
git remote -v | findstr "github.com" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo OK - GitHub remote configured
    git remote -v
) else (
    echo WARNING: No GitHub remote configured
    echo.
    echo To add a remote, run:
    echo   git remote add origin https://github.com/YOUR_USERNAME/kalin.git
    echo.
    set /p ADD_REMOTE="Do you want to add a remote now? (y/n): "
    if /i "%ADD_REMOTE%"=="y" (
        set /p REPO_URL="Enter GitHub repository URL: "
        git remote add origin !REPO_URL!
        echo OK - Remote added
    )
)
echo.

REM Step 4: Test backup
echo [4/4] Testing backup...
python auto_backup_github.py -m "Initial auto-backup setup"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Your code has been backed up to GitHub.
    echo.
    echo To enable automatic backups, run:
    echo   python setup_auto_backup.py
    echo.
) else (
    echo.
    echo ========================================
    echo BACKUP FAILED
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. No GitHub remote configured
    echo 2. Not authenticated with GitHub
    echo 3. No internet connection
    echo.
    echo To fix authentication:
    echo   git push --dry-run
    echo.
)

pause
