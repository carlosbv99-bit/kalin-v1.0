"""
Prepare Kalin AI for specialist review and deployment
Cleans up code, runs checks, and generates reports
"""
import os
import sys
import json
from datetime import datetime

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_project_structure():
    """Verify project structure is complete"""
    print_header("1. CHECKING PROJECT STRUCTURE")
    
    required_files = [
        'web.py',
        'run.py',
        'requirements.txt',
        'agent/core/orchestrator.py',
        'agent/actions/executor.py',
        'agent/core/experience_memory.py',
        'templates/index.html',
    ]
    
    missing = []
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} MISSING")
            missing.append(filepath)
    
    return len(missing) == 0, missing

def check_environment():
    """Check if environment is properly configured"""
    print_header("2. CHECKING ENVIRONMENT")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False, ["Python version too old"]
    
    print("✅ Python version OK")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (create from .env.example)")
    
    # Check virtual environment
    if os.path.exists('.venv') or os.path.exists('venv'):
        print("✅ Virtual environment found")
    else:
        print("⚠️  No virtual environment detected")
    
    return True, []

def generate_system_report():
    """Generate a comprehensive system report"""
    print_header("3. GENERATING SYSTEM REPORT")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': sys.platform,
        'files': {},
        'dependencies': {}
    }
    
    # Analyze key files
    key_files = [
        'web.py',
        'agent/core/orchestrator.py',
        'agent/actions/executor.py',
        'agent/core/experience_memory.py',
    ]
    
    for filepath in key_files:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
                
                # Count functions and classes
                functions = content.count('def ')
                classes = content.count('class ')
                
                report['files'][filepath] = {
                    'lines': lines,
                    'functions': functions,
                    'classes': classes,
                    'size_kb': round(len(content.encode('utf-8')) / 1024, 2)
                }
                
                print(f"📄 {filepath}: {lines} lines, {functions} functions, {classes} classes")
    
    # Save report
    report_path = 'system_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Report saved to {report_path}")
    return True, []

def create_deployment_checklist():
    """Create a deployment checklist file"""
    print_header("4. CREATING DEPLOYMENT CHECKLIST")
    
    checklist = """# Deployment Checklist for Kalin AI

## Pre-Deployment Checks
- [ ] All tests pass (`python run_all_tests.py`)
- [ ] Code quality verified (`python check_code_quality.py`)
- [ ] System report generated (`system_report.json`)
- [ ] No sensitive data in code (API keys, passwords)
- [ ] `.env` file configured correctly
- [ ] Virtual environment created and activated

## Security Review
- [ ] CORS configuration appropriate for deployment
- [ ] Debug mode disabled in production
- [ ] Rate limiting implemented (if needed)
- [ ] Input validation on all endpoints
- [ ] File access restricted to safe paths
- [ ] Error messages don't leak sensitive info

## Performance Testing
- [ ] Server startup time < 5 seconds
- [ ] Simple requests respond < 2 seconds
- [ ] Code generation completes < 60 seconds
- [ ] Memory usage stable over time
- [ ] No memory leaks detected

## Documentation
- [ ] README.md updated
- [ ] API endpoints documented
- [ ] Installation instructions clear
- [ ] Troubleshooting guide available
- [ ] Architecture diagrams current

## Backup & Recovery
- [ ] Experience memory backup strategy defined
- [ ] Session data can be exported
- [ ] Configuration can be restored from backup
- [ ] Rollback plan documented

## Monitoring
- [ ] Logging configured appropriately
- [ ] Error tracking setup (if needed)
- [ ] Performance metrics collected
- [ ] Alert thresholds defined

## Final Steps
- [ ] Review all checklist items
- [ ] Get sign-off from team lead
- [ ] Schedule deployment window
- [ ] Notify stakeholders
- [ ] Execute deployment
- [ ] Verify functionality post-deployment
- [ ] Monitor for issues

---
Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Deployment checklist created: DEPLOYMENT_CHECKLIST.md")
    return True, []

def main():
    print("="*70)
    print("  KALIN AI - PREPARATION FOR SPECIALIST REVIEW")
    print("="*70)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Environment", check_environment),
        ("System Report", generate_system_report),
        ("Deployment Checklist", create_deployment_checklist),
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, issues = check_func()
            results.append((check_name, passed, issues))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n❌ Error in {check_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((check_name, False, [str(e)]))
            all_passed = False
    
    # Summary
    print_header("PREPARATION SUMMARY")
    
    for check_name, passed, issues in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {check_name}")
        
        if issues:
            for issue in issues[:3]:
                print(f"             • {issue}")
    
    print()
    if all_passed:
        print("🎉 PREPARATION COMPLETE!")
        print("\nNext steps:")
        print("1. Review generated files:")
        print("   - system_report.json")
        print("   - DEPLOYMENT_CHECKLIST.md")
        print("   - TESTING_GUIDE.md")
        print("\n2. Run full test suite:")
        print("   python run_all_tests.py")
        print("\n3. Review code quality:")
        print("   python check_code_quality.py")
        print("\n✅ Ready for specialist review!")
        return 0
    else:
        print("⚠️  Some checks failed")
        print("Please address issues before specialist review")
        return 1

if __name__ == "__main__":
    sys.exit(main())
