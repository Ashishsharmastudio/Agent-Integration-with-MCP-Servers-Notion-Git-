#!/usr/bin/env python3
"""
Test script to verify Docker setup and environment configuration
"""

import os
import sys
import subprocess

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def check_docker():
    """Check if Docker is installed and running"""
    print("🐳 Checking Docker installation...")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker Desktop.")
        return False

def check_docker_running():
    """Check if Docker daemon is running"""
    print("\n🔄 Checking Docker daemon...")
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running. Please start Docker Desktop.")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker daemon: {e}")
        return False

def check_mcp_images():
    """Check if required MCP images are available"""
    print("\n🔍 Checking MCP images...")
    try:
        # Check GitHub MCP server image
        result = subprocess.run(['docker', 'images', 'ghcr.io/github/github-mcp-server', '--format', 'table'], 
                              capture_output=True, text=True)
        if 'ghcr.io/github/github-mcp-server' in result.stdout:
            print("✅ GitHub MCP server image found")
        else:
            print("⚠️  GitHub MCP server image not found. Pulling...")
            pull_result = subprocess.run(['docker', 'pull', 'ghcr.io/github/github-mcp-server'], 
                                       capture_output=True, text=True)
            if pull_result.returncode == 0:
                print("✅ GitHub MCP server image pulled successfully")
            else:
                print("❌ Failed to pull GitHub MCP server image")
        
        return True
    except Exception as e:
        print(f"❌ Error checking MCP images: {e}")
        return False

def check_env_vars():
    """Check if required environment variables are set"""
    print("\n🔐 Checking environment variables...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'GITHUB_PERSONAL_ACCESS_TOKEN',
        'GITHUB_REPO',
        'NOTION_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}{value[-4:] if len(value) > 4 else value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_python_deps():
    """Check if Python dependencies are installed"""
    print("\n🐍 Checking Python dependencies...")
    try:
        import flask
        import openai
        import mcp
        print("✅ Required Python packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main check function"""
    print("📋 MCP Agent Docker Setup Checker")
    print("=" * 50)
    
    checks = [
        check_docker,
        check_docker_running,
        check_mcp_images,
        check_env_vars,
        check_python_deps
    ]
    
    passed = 0
    for check in checks:
        if check():
            passed += 1
        print()  # Add spacing between checks
    
    print("=" * 50)
    print(f"🏁 Setup Check Results: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 All checks passed! You're ready to run the MCP Agent.")
        return 0
    else:
        print("⚠️  Some checks failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())