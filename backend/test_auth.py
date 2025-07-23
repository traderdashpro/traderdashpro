#!/usr/bin/env python3
"""
Simple test script for the authentication system
"""
import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_signup():
    """Test user signup"""
    print("Testing signup...")
    
    signup_data = {
        "email": "test@example.com",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Signup response: {response.status_code}")
    print(f"Response body: {response.json()}")
    return response

def test_login():
    """Test user login"""
    print("\nTesting login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_protected_route(token):
    """Test accessing a protected route"""
    if not token:
        print("No token available, skipping protected route test")
        return
    
    print("\nTesting protected route...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Protected route response: {response.status_code}")
    print(f"Response body: {response.json()}")

def test_trades_with_auth(token):
    """Test trades endpoint with authentication"""
    if not token:
        print("No token available, skipping trades test")
        return
    
    print("\nTesting trades endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/trades/", headers=headers)
    print(f"Trades response: {response.status_code}")
    print(f"Response body: {response.json()}")

if __name__ == "__main__":
    print("Starting authentication tests...")
    
    # Test signup
    signup_response = test_signup()
    
    # Test login
    token = test_login()
    
    # Test protected routes
    test_protected_route(token)
    test_trades_with_auth(token)
    
    print("\nTests completed!") 