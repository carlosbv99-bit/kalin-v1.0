@echo off
REM Auto-backup to GitHub - Quick Script
REM Run this manually or schedule it

echo ========================================
echo KALIN AI - AUTO BACKUP TO GITHUB
echo ========================================
echo.

REM Check if git is available
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git not found in PATH
    pause
    exit /b 1
)

REM Run auto-backup
python auto_backup_github.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Backup completed successfully
) else (
    echo.
    echo ❌ Backup failed or no changes
)

echo.
pause
