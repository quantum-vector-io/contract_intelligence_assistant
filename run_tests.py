"""
Test runner script for the Contract Intelligence Assistant.
Runs all tests in a structured way with proper reporting.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False

def main():
    """Run all tests in order."""
    print("🚀 Contract Intelligence Assistant - Test Suite")
    print("="*60)
    
    # Activate virtual environment
    venv_activate = "& G:/Software_Engineering/contract_intelligence_assistant/venv/Scripts/Activate.ps1"
    cd_project = "cd G:/Software_Engineering/contract_intelligence_assistant"
    
    # Test commands
    tests = [
        {
            "cmd": f"{venv_activate}; {cd_project}; python -m pytest tests/unit/ --tb=short -v",
            "desc": "Unit Tests - Individual Components"
        },
        {
            "cmd": f"{venv_activate}; {cd_project}; python -m pytest tests/integration/test_system_integration.py -v",
            "desc": "Integration Tests - System Components"
        },
        {
            "cmd": f"{venv_activate}; {cd_project}; python -m pytest tests/integration/test_financial_analysis_api.py -v",
            "desc": "Integration Tests - Financial Analysis API"
        },
        {
            "cmd": f"{venv_activate}; {cd_project}; python -m pytest tests/integration/test_rag_discrepancy.py -v",
            "desc": "Integration Tests - RAG Discrepancy Analysis"
        },
        {
            "cmd": f"{venv_activate}; {cd_project}; python -m pytest tests/integration/test_ui_workflow.py -v",
            "desc": "Integration Tests - UI Workflow"
        }
    ]
    
    results = []
    
    for test in tests:
        success = run_command(test["cmd"], test["desc"])
        results.append((test["desc"], success))
    
    # Performance tests (optional, marked as slow)
    print(f"\n{'='*60}")
    print("🐌 Performance Tests (Optional - may take longer)")
    print(f"{'='*60}")
    
    perf_cmd = f"{venv_activate}; {cd_project}; python -m pytest tests/integration/test_performance.py -m slow -v"
    perf_success = run_command(perf_cmd, "Performance Tests - Load and Stress Testing")
    results.append(("Performance Tests", perf_success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {desc}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
