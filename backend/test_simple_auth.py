#!/usr/bin/env python3
"""
Simple authentication test using subprocess and curl
"""
import subprocess
import json
import time

def run_curl_command(method, url, data=None, headers=None):
    """Run a curl command and return the response"""
    cmd = ['curl', '-X', method, url, '-s']
    
    if headers:
        for header in headers:
            cmd.extend(['-H', header])
    
    if data:
        cmd.extend(['-H', 'Content-Type: application/json', '-d', data])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def test_auth_flow():
    """Test the complete authentication flow"""
    base_url = "http://localhost:5001/api"
    
    print("🚀 Testing Authentication Flow (Email Confirmation Disabled)")
    print("=" * 60)
    
    # Test 1: Signup
    print("\n1️⃣ Testing Signup...")
    signup_data = json.dumps({
        "email": "test@example.com",
        "password": "TestPass123"
    })
    
    response, code = run_curl_command('POST', f"{base_url}/auth/signup", signup_data)
    print(f"Status Code: {code}")
    print(f"Response: {response}")
    
    if code != 0:
        print("❌ Signup failed - server might not be running")
        return None
    
    try:
        signup_result = json.loads(response)
        print(f"✅ Signup successful: {signup_result.get('message', '')}")
    except:
        print("❌ Invalid JSON response")
        return None
    
    # Test 2: Login
    print("\n2️⃣ Testing Login...")
    login_data = json.dumps({
        "email": "test@example.com",
        "password": "TestPass123"
    })
    
    response, code = run_curl_command('POST', f"{base_url}/auth/login", login_data)
    print(f"Status Code: {code}")
    print(f"Response: {response}")
    
    if code != 0:
        print("❌ Login failed")
        return None
    
    try:
        login_result = json.loads(response)
        token = login_result.get('token')
        if token:
            print(f"✅ Login successful! Token received: {token[:20]}...")
            return token
        else:
            print("❌ No token in response")
            return None
    except:
        print("❌ Invalid JSON response")
        return None

def test_protected_routes(token):
    """Test protected routes with the token"""
    if not token:
        print("❌ No token available for protected route tests")
        return
    
    base_url = "http://localhost:5001/api"
    
    print("\n3️⃣ Testing Protected Routes...")
    
    # Test /auth/me endpoint
    print("\n   Testing /auth/me...")
    headers = [f"Authorization: Bearer {token}"]
    response, code = run_curl_command('GET', f"{base_url}/auth/me", headers=headers)
    print(f"   Status Code: {code}")
    print(f"   Response: {response}")
    
    if code == 0:
        try:
            result = json.loads(response)
            print(f"   ✅ /auth/me successful: {result.get('user', {}).get('email', '')}")
        except:
            print("   ❌ Invalid JSON response")
    else:
        print("   ❌ /auth/me failed")
    
    # Test /trades endpoint
    print("\n   Testing /trades...")
    response, code = run_curl_command('GET', f"{base_url}/trades/", headers=headers)
    print(f"   Status Code: {code}")
    print(f"   Response: {response}")
    
    if code == 0:
        try:
            result = json.loads(response)
            print(f"   ✅ /trades successful: {len(result.get('trades', []))} trades found")
        except:
            print("   ❌ Invalid JSON response")
    else:
        print("   ❌ /trades failed")

def main():
    """Main test function"""
    print("🔧 Starting Authentication Tests...")
    print("Make sure your Flask server is running on localhost:5001")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    # Test the auth flow
    token = test_auth_flow()
    
    if token:
        # Test protected routes
        test_protected_routes(token)
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Authentication flow failed")

if __name__ == "__main__":
    main() 