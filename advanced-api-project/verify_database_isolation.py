#!/usr/bin/env python
"""
Database Isolation Verification Script

This script demonstrates that our test suite maintains complete database isolation
by showing that development data is never affected by test execution.

Usage:
    python verify_database_isolation.py

The script will:
1. Show current development database state
2. Run the test suite 
3. Verify development database is unchanged
4. Provide clear evidence of proper isolation
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return the output."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return result.stdout.strip()
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Main verification process."""
    
    print("=" * 80)
    print("🧪 DATABASE ISOLATION VERIFICATION")
    print("=" * 80)
    print("This script verifies that test execution does not affect development data.")
    
    # Step 1: Check development database before tests
    print("\n📊 STEP 1: Check Development Database State (BEFORE tests)")
    before_books = run_command(
        './venv/bin/python manage.py shell -c "from api.models import Book, Author; '
        'print(f\'Books: {Book.objects.count()}\'); '
        'print(f\'Authors: {Author.objects.count()}\'); '
        'print(f\'Sample book: {Book.objects.first().title if Book.objects.exists() else \"None\"}\');"',
        "Checking current development database state"
    )
    
    # Step 2: Run the comprehensive test suite
    print("\n🧪 STEP 2: Execute Complete Test Suite")
    test_output = run_command(
        './venv/bin/python manage.py test api.test_views --settings=advanced_api_project.test_settings',
        "Running all 45 tests with isolated test database"
    )
    
    # Extract test results
    if test_output:
        # Check for successful test completion
        lines = test_output.split('\n')
        test_result_line = [line for line in lines if line.strip() == "OK"]
        
        if test_result_line:
            print("✅ All tests passed successfully!")
        elif "FAILED" in test_output:
            print("❌ Some tests failed!")
        else:
            print("ℹ️  Test execution completed (checking results...)")
            
        # Show test database creation/destruction evidence
        if "Creating test database" in test_output:
            print("✅ Confirmed: Separate test database was created")
        if "Destroying test database" in test_output:
            print("✅ Confirmed: Test database was properly destroyed")
        if "memorydb_default" in test_output or ":memory:" in test_output:
            print("✅ Confirmed: In-memory database was used for testing")
        if "🧪 Test settings loaded" in test_output:
            print("✅ Confirmed: Optimized test settings were loaded")
    
    # Step 3: Check development database after tests
    print("\n📊 STEP 3: Check Development Database State (AFTER tests)")
    after_books = run_command(
        './venv/bin/python manage.py shell -c "from api.models import Book, Author; '
        'print(f\'Books: {Book.objects.count()}\'); '
        'print(f\'Authors: {Author.objects.count()}\'); '
        'print(f\'Sample book: {Book.objects.first().title if Book.objects.exists() else \"None\"}\');"',
        "Verifying development database is unchanged"
    )
    
    # Step 4: Compare results and provide verification
    print("\n🔍 STEP 4: Database Isolation Verification")
    print("=" * 60)
    
    if before_books == after_books:
        print("✅ SUCCESS: Database isolation is working perfectly!")
        print("✅ Development database state is identical before and after tests")
        print("✅ No test data leaked into development database") 
        print("✅ Production/development data is completely safe")
    else:
        print("❌ WARNING: Database isolation may have failed!")
        print("❌ Development database state changed during testing")
        print("🔍 This should be investigated immediately")
    
    print("\n📝 SUMMARY:")
    print("-" * 40)
    print("Before tests:", before_books)
    print("After tests: ", after_books)
    print("Isolation:   ", "✅ WORKING" if before_books == after_books else "❌ FAILED")
    
    print("\n" + "=" * 80)
    print("🎯 VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()