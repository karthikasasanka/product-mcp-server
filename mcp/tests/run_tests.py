#!/usr/bin/env python3
"""
Test runner script for the MCP API project.
Runs all tests with coverage reporting.
"""

import subprocess
import sys
import os


def run_tests_with_coverage():
    """Run all tests with coverage reporting."""
    # Get the directory where this script is located
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    
    # Change to the project root directory
    os.chdir(project_root)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "ai/tests/",
        "--cov=mcp_api",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=100",
        "-v",
        "--tb=short"
    ]
    
    print("Running tests with coverage...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed with 100% coverage!")
        print("📊 Coverage report generated in htmlcov/")
        print("📄 Coverage XML report generated in coverage.xml")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


def run_tests_only():
    """Run tests without coverage reporting."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    os.chdir(project_root)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "ai/tests/",
        "-v",
        "--tb=short"
    ]
    
    print("Running tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for MCP API project")
    parser.add_argument(
        "--no-coverage", 
        action="store_true", 
        help="Run tests without coverage reporting"
    )
    
    args = parser.parse_args()
    
    if args.no_coverage:
        success = run_tests_only()
    else:
        success = run_tests_with_coverage()
    
    sys.exit(0 if success else 1)
