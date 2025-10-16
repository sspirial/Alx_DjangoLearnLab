"""
Test script for Social Media API
This script tests the basic functionality of the user authentication system.
"""

import requests
import json

# Base URL - adjust port if needed
BASE_URL = "http://127.0.0.1:8001"
ACCOUNTS_URL = f"{BASE_URL}/api/accounts"

# Test data
test_user = {
    "username": "testuser_api",
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "bio": "This is a test user created by the test script"
}

login_data = {
    "username": "testuser_api",
    "password": "SecurePass123!"
}

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f"  {title}")
        print("="*60)

def test_user_registration():
    """Test user registration endpoint"""
    print_separator("TEST 1: User Registration")
    
    try:
        response = requests.post(
            f"{ACCOUNTS_URL}/register/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return response.json().get('token')
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_user_login():
    """Test user login endpoint"""
    print_separator("TEST 2: User Login")
    
    try:
        response = requests.post(
            f"{ACCOUNTS_URL}/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json().get('token')
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_get_profile(token):
    """Test getting user profile"""
    print_separator("TEST 3: Get User Profile")
    
    if not token:
        print("❌ No token available. Skipping test.")
        return False
    
    try:
        response = requests.get(
            f"{ACCOUNTS_URL}/profile/",
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Profile retrieval successful!")
            return True
        else:
            print("❌ Profile retrieval failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_update_profile(token):
    """Test updating user profile"""
    print_separator("TEST 4: Update User Profile")
    
    if not token:
        print("❌ No token available. Skipping test.")
        return False
    
    update_data = {
        "bio": "Updated bio text - Testing the API update functionality",
        "email": "updated_email@example.com"
    }
    
    try:
        response = requests.patch(
            f"{ACCOUNTS_URL}/profile/",
            json=update_data,
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Profile update successful!")
            return True
        else:
            print("❌ Profile update failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_logout(token):
    """Test user logout"""
    print_separator("TEST 5: User Logout")
    
    if not token:
        print("❌ No token available. Skipping test.")
        return False
    
    try:
        response = requests.post(
            f"{ACCOUNTS_URL}/logout/",
            headers={
                "Authorization": f"Token {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Logout successful!")
            return True
        else:
            print("❌ Logout failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print_separator("TEST 6: Unauthorized Access")
    
    try:
        response = requests.get(
            f"{ACCOUNTS_URL}/profile/",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ Unauthorized access properly blocked!")
            return True
        else:
            print("❌ Security issue: Unauthorized access not blocked!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print_separator("SOCIAL MEDIA API - TEST SUITE")
    print(f"Testing API at: {BASE_URL}")
    print(f"Make sure the server is running!")
    
    results = []
    
    # Test 1: Registration
    token = test_user_registration()
    results.append(("Registration", token is not None))
    
    # Test 2: Login (only if registration failed to get token)
    if not token:
        token = test_user_login()
        results.append(("Login", token is not None))
    
    # Test 3: Get Profile
    profile_result = test_get_profile(token)
    results.append(("Get Profile", profile_result))
    
    # Test 4: Update Profile
    update_result = test_update_profile(token)
    results.append(("Update Profile", update_result))
    
    # Test 5: Logout
    logout_result = test_logout(token)
    results.append(("Logout", logout_result))
    
    # Test 6: Unauthorized Access
    unauth_result = test_unauthorized_access()
    results.append(("Unauthorized Access Block", unauth_result))
    
    # Print Summary
    print_separator("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
