# Kalin AI - Professional Test Suite
# Execute all tests before deployment

import subprocess
import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_test(test_name, command):
    """Run a test and report results"""
    print_header(f"Running: {test_name}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ {test_name} PASSED")
            return True
        else:
            print(f"❌ {test_name} FAILED")
            print("STDOUT:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_name} TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {test_name} ERROR: {str(e)}")
        return False

def main():
    print_header("KALIN AI - PROFESSIONAL TEST SUITE")
    
    tests = [
        ("Syntax Check", "python -m py_compile web.py"),
        ("Import Check", "python -c \"import flask; import agent.core.orchestrator\""),
        ("Unit Tests", "python -m pytest tests/ -v --tb=short"),
        ("Integration Tests", "python -m pytest tests/integration/ -v --tb=short"),
        ("API Endpoint Tests", "python test_endpoints.py"),
        ("LLM Provider Tests", "python test_llm_providers.py"),
    ]
    
    results = []
    for test_name, command in tests:
        passed = run_test(test_name, command)
        results.append((test_name, passed))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Ready for specialist review.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
