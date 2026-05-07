@echo off
REM Kalin AI - Quick Test Script for Windows
REM Run this to prepare code for specialist review

echo ============================================================
echo   KALIN AI - PREPARING FOR SPECIALIST REVIEW
echo ============================================================
echo.

echo Step 1: Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo.

echo Step 2: Preparing project for review...
python prepare_for_review.py
if errorlevel 1 (
    echo.
    echo WARNING: Preparation had some issues. Review output above.
    echo.
)
echo.

echo Step 3: Checking code quality...
python check_code_quality.py
if errorlevel 1 (
    echo.
    echo WARNING: Code quality checks failed. Fix issues before review.
    echo.
)
echo.

echo ============================================================
echo   PREPARATION COMPLETE
echo ============================================================
echo.
echo Generated files for review:
echo   - system_report.json
echo   - DEPLOYMENT_CHECKLIST.md
echo   - TESTING_GUIDE.md
echo   - REVIEW_SUMMARY.md
echo.
echo Next steps:
echo   1. Review generated documentation
echo   2. Run full test suite: python run_all_tests.py
echo   3. Start server: python run.py
echo   4. Open browser: http://localhost:5000
echo.
pause
