#!/usr/bin/env python3
"""
Simple test runner for the MCP Agent tests
"""

import os
import sys
import subprocess

def run_test_file(test_file):
    """Run a single test file"""
    print(f"Running {test_file}...")
    try:
        # Add the current directory to the Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        result = subprocess.run([
            sys.executable, '-c', 
            f'import sys; sys.path.insert(0, "."); exec(open("{test_file}").read())'
        ], cwd='.', env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {test_file} error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running MCP Agent Tests")
    print("=" * 50)
    
    # List of test files to run
    test_files = [
        'tests/test_feature_diff.py',
        'tests/test_mcp_manager.py',
        'tests/test_reasoning.py'
    ]
    
    passed = 0
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{len(test_files)} tests passed")
    
    if passed == len(test_files):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())