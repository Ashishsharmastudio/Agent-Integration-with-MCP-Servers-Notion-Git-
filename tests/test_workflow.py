#!/usr/bin/env python3
"""
Test workflow demonstrating the full MCP Agent functionality
"""

import os
import sys
import time
import requests

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

def test_health_endpoint():
    """Test the health endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get('http://localhost:5000/healthz')
        if response.status_code == 200 and response.json().get('ok'):
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_simple_query():
    """Test a simple query"""
    print("\n🔍 Testing simple query...")
    try:
        response = requests.get('http://localhost:5000/agent?query=medical%20chatbot')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simple query successful")
            print(f"   Answer: {data.get('answer', '')[:100]}...")
            print(f"   Confidence: {data.get('confidence', 0)}")
            return True
        else:
            print(f"❌ Simple query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple query error: {e}")
        return False

def test_feature_comparison():
    """Test feature comparison query"""
    print("\n🔄 Testing feature comparison...")
    try:
        response = requests.get('http://localhost:5000/agent?query=compare%20features%20between%20docs%20and%20code')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Feature comparison successful")
            print(f"   Answer: {data.get('answer', '')[:100]}...")
            diff = data.get('diff', {})
            print(f"   Overlap: {len(diff.get('overlap', []))} items")
            print(f"   Only in Notion: {len(diff.get('only_in_notion', []))} items")
            print(f"   Only in Code: {len(diff.get('only_in_code', []))} items")
            return True
        else:
            print(f"❌ Feature comparison failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Feature comparison error: {e}")
        return False

def main():
    """Main test workflow"""
    print("🚀 MCP Agent Test Workflow")
    print("=" * 50)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Run all tests
    tests = [
        test_health_endpoint,
        test_simple_query,
        test_feature_comparison
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The MCP Agent is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the application logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())