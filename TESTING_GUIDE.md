# Kalin AI - Testing Guide for Specialists

## Overview
This document provides instructions for specialists reviewing and testing the Kalin AI codebase.

## Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Code Quality Check
```bash
# Run comprehensive code quality checks
python check_code_quality.py
```

This will verify:
- ✅ Python syntax correctness
- ✅ All imports resolve correctly
- ✅ Code metrics and structure
- ✅ Documentation presence

### 3. Run Test Suite
```bash
# Execute all tests
python run_all_tests.py
```

Tests include:
- **Syntax validation** - No compilation errors
- **Import verification** - All dependencies available
- **Unit tests** - Core functionality
- **Integration tests** - Component interaction
- **API endpoint tests** - Web interface
- **LLM provider tests** - AI integration

### 4. Manual Testing Checklist

#### Backend Tests
- [ ] Server starts without errors: `python run.py`
- [ ] Health endpoint responds: `http://localhost:5000/health`
- [ ] LLM status check: `http://localhost:5000/llm-status`
- [ ] Experience memory loads correctly
- [ ] All API endpoints return proper responses

#### Frontend Tests
- [ ] Web interface loads: `http://localhost:5000`
- [ ] Sidebar menu opens/closes smoothly
- [ ] Model selection modal displays correctly
- [ ] Dependency check works
- [ ] Virtual environment creation succeeds
- [ ] Package installation completes
- [ ] Model download workflow functions

#### Feature Tests
- [ ] Code generation works (try: "create a simple calculator in Python")
- [ ] Experience export creates valid JSON file
- [ ] Experience import merges correctly
- [ ] Memory persistence across restarts
- [ ] Error handling displays user-friendly messages

## Architecture Overview

### Key Components

1. **web.py** - Flask web server with REST API
   - Routes for chat, system management, experience sharing
   - CORS configuration for frontend communication
   - Security headers and error handling

2. **agent/core/orchestrator.py** - Main request handler
   - Intent detection and routing
   - Context management
   - Response generation

3. **agent/actions/executor.py** - Command execution engine
   - Code generation workflows
   - Experience recording
   - File operations

4. **agent/core/experience_memory.py** - Learning system
   - Experience storage and retrieval
   - Pattern detection
   - Recommendation engine

5. **templates/index.html** - Web interface
   - Responsive chat UI
   - Sidebar navigation
   - Modal dialogs for complex interactions

## Testing Best Practices

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies (LLM providers, file system)
- Verify edge cases and error conditions
- Keep tests fast (< 1 second each)

### Integration Tests
- Test component interactions
- Use real dependencies where practical
- Verify data flow between modules
- Check state management

### End-to-End Tests
- Simulate complete user workflows
- Test from UI to backend and back
- Verify persistence and state
- Check error recovery

## Common Issues & Solutions

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Ollama connection refused
**Solution**: Start Ollama service
```bash
ollama serve
```

### Issue: Port already in use
**Solution**: Kill existing process or change port in `run.py`
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

### Issue: Models not found
**Solution**: Download required models
```bash
ollama pull deepseek-coder:6.7b
ollama pull llama3.2:3b
```

## Performance Benchmarks

Expected performance on standard hardware (8GB RAM, SSD):
- Server startup: < 3 seconds
- Simple code generation: 10-20 seconds
- Complex HTML generation: 30-60 seconds
- Experience export: < 1 second
- Dependency check: < 2 seconds

## Security Considerations

1. **Input Validation**: All user inputs are sanitized
2. **Path Traversal Prevention**: File operations restricted to project directory
3. **CORS Configuration**: Configured for development, tighten for production
4. **API Keys**: Stored in `.env`, never committed to version control
5. **Code Execution**: Generated code is NOT executed automatically

## Deployment Checklist

Before deploying to production:

- [ ] All tests pass (`python run_all_tests.py`)
- [ ] Code quality checks pass (`python check_code_quality.py`)
- [ ] `.env` file configured with production values
- [ ] CORS origins restricted to specific domains
- [ ] Debug mode disabled in Flask
- [ ] Logging configured appropriately
- [ ] Rate limiting implemented (if needed)
- [ ] HTTPS configured (if exposed to internet)
- [ ] Backup strategy for experience memory
- [ ] Monitoring and alerting setup

## Support

For issues or questions during review:
1. Check logs in `logs/` directory
2. Review error messages in console output
3. Consult architecture diagrams in documentation
4. Test individual components in isolation

## Version Information

- **Current Version**: 1.0
- **Python Required**: 3.8+
- **Key Dependencies**: Flask, Ollama, requests
- **Last Updated**: 2026-05-07

---

*This guide is maintained as part of the Kalin AI project. For updates or corrections, please submit a pull request.*
