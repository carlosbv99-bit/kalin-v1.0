"""
Code Quality Checker for Kalin AI
Checks code quality before specialist review
"""
import subprocess
import sys
import os

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check_syntax():
    """Check Python syntax"""
    print_section("1. SYNTAX CHECK")
    
    files_to_check = [
        'web.py',
        'agent/core/orchestrator.py',
        'agent/actions/executor.py',
        'agent/actions/tools/fix_tool.py',
        'agent/core/experience_memory.py',
    ]
    
    errors = []
    for filepath in files_to_check:
        if os.path.exists(filepath):
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', filepath],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {filepath}")
            else:
                print(f"❌ {filepath}")
                errors.append((filepath, result.stderr))
        else:
            print(f"⚠️  {filepath} not found")
    
    return len(errors) == 0, errors

def check_imports():
    """Check if all imports work"""
    print_section("2. IMPORT CHECK")
    
    imports_to_test = [
        'flask',
        'flask_cors',
        'dotenv',
        'requests',
        'agent.core.orchestrator',
        'agent.llm.client',
        'agent.core.experience_memory',
    ]
    
    errors = []
    for import_name in imports_to_test:
        try:
            __import__(import_name)
            print(f"✅ {import_name}")
        except ImportError as e:
            print(f"❌ {import_name}: {str(e)}")
            errors.append((import_name, str(e)))
    
    return len(errors) == 0, errors

def check_code_quality():
    """Run basic code quality checks"""
    print_section("3. CODE QUALITY METRICS")
    
    # Count lines of code
    total_lines = 0
    total_files = 0
    
    key_files = [
        'web.py',
        'agent/core/orchestrator.py',
        'agent/actions/executor.py',
        'agent/actions/tools/fix_tool.py',
    ]
    
    for filepath in key_files:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                total_files += 1
                print(f"📄 {filepath}: {lines} lines")
    
    print(f"\n📊 Total: {total_lines} lines across {total_files} key files")
    
    return True, []

def check_documentation():
    """Check if key files have documentation"""
    print_section("4. DOCUMENTATION CHECK")
    
    files_needing_docs = [
        'web.py',
        'agent/core/orchestrator.py',
        'agent/actions/executor.py',
    ]
    
    missing_docs = []
    for filepath in files_needing_docs:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                has_docstring = '"""' in content or "'''" in content
                has_comments = '#' in content
                
                if has_docstring or has_comments:
                    print(f"✅ {filepath} - Documented")
                else:
                    print(f"❌ {filepath} - Missing documentation")
                    missing_docs.append(filepath)
        else:
            print(f"⚠️  {filepath} not found")
    
    return len(missing_docs) == 0, missing_docs

def main():
    print("="*60)
    print("  KALIN AI - CODE QUALITY CHECKER")
    print("  Preparing for Specialist Review")
    print("="*60)
    
    checks = [
        ("Syntax", check_syntax),
        ("Imports", check_imports),
        ("Code Quality", check_code_quality),
        ("Documentation", check_documentation),
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, errors = check_func()
            results.append((check_name, passed, errors))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n❌ Error running {check_name}: {str(e)}")
            results.append((check_name, False, [str(e)]))
            all_passed = False
    
    # Summary
    print_section("SUMMARY")
    
    for check_name, passed, errors in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {check_name}")
        
        if errors and not passed:
            for error in errors[:3]:  # Show first 3 errors
                if isinstance(error, tuple):
                    print(f"             • {error[0]}")
                else:
                    print(f"             • {error}")
    
    print()
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Code is ready for specialist review")
        return 0
    else:
        print("⚠️  Some checks failed")
        print("Please fix issues before specialist review")
        return 1

if __name__ == "__main__":
    sys.exit(main())
