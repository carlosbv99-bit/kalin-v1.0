# Quick Start for Specialists

## 3-Step Preparation

### Option 1: Automated (Recommended)
```bash
# Windows - Double click this file
prepare_for_testing.bat

# Or run from command line
python prepare_for_review.py
python check_code_quality.py
python run_all_tests.py
```

### Option 2: Manual
```bash
# 1. Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Check code quality
python check_code_quality.py

# 3. Run tests
python run_all_tests.py

# 4. Start server
python run.py
```

## What to Review

### 📄 Documentation Files
1. **REVIEW_SUMMARY.md** - Project overview and architecture
2. **TESTING_GUIDE.md** - Detailed testing instructions
3. **DEPLOYMENT_CHECKLIST.md** - Pre-deployment checklist
4. **system_report.json** - Code metrics and statistics

### 💻 Key Code Files
1. **web.py** - Flask server (lines 1-400)
2. **agent/core/orchestrator.py** - Request handling
3. **agent/actions/executor.py** - Code generation logic
4. **templates/index.html** - Web interface

### 🧪 Test Files
1. **run_all_tests.py** - Test runner
2. **check_code_quality.py** - Quality checker
3. **test_endpoints.py** - API tests
4. **test_llm_providers.py** - LLM integration tests

## Quick Verification

```bash
# Verify syntax
python -m py_compile web.py

# Check imports
python -c "import flask; import agent.core.orchestrator; print('OK')"

# Start server
python run.py

# Test in browser
# Open: http://localhost:5000
```

## Common Commands

| Task | Command |
|------|---------|
| Prepare for review | `python prepare_for_review.py` |
| Check quality | `python check_code_quality.py` |
| Run all tests | `python run_all_tests.py` |
| Start server | `python run.py` |
| Check Ollama | `ollama list` |
| View logs | `type logs\kalin.log` |

## Expected Results

✅ **All checks pass** - No syntax errors, all imports work  
✅ **Tests complete** - All test suites run successfully  
✅ **Server starts** - Flask runs on port 5000  
✅ **Web UI loads** - Chat interface accessible  
✅ **Code generation works** - Can generate simple programs  

## Need Help?

- Check `logs/` directory for detailed logs
- Review error messages in console output
- Consult TESTING_GUIDE.md for troubleshooting
- Examine system_report.json for metrics

---
*Ready for specialist review! 🚀*
