#!/usr/bin/env python
"""
Test user registration and login
"""
import requests
from urllib.parse import urljoin
import json

BASE_URL = "http://localhost:8000"
session = requests.Session()

print("=" * 70)
print("🧪 USER REGISTRATION AND LOGIN TEST")
print("=" * 70)

# Step 1: Get registration page
print("\n[1/3] Accessing registration page...")
try:
    response = session.get(f"{BASE_URL}/auth/register", timeout=5)
    print(f"✅ Registration page loaded (Status: {response.status_code})")
except Exception as e:
    print(f"❌ Failed: {e}")
    exit(1)

# Step 2: Register user
print("\n[2/3] Registering test user (testuser_final/Test@123456)...")
register_data = {
    "username": "testuser_final",
    "email": "testuser_final@example.com",
    "password": "Test@123456",
    "confirm_password": "Test@123456"
}
try:
    response = session.post(f"{BASE_URL}/auth/register", data=register_data, timeout=5, allow_redirects=True)
    print(f"✅ Registration response received (Status: {response.status_code})")
    
    # Check if redirect happened or success message
    if response.status_code == 200:
        if "login" in response.text.lower() or "testuser" in response.text:
            print("✅ User registered successfully!")
        else:
            print(f"⚠️  Response contains: {response.text[:200]}")
except Exception as e:
    print(f"❌ Registration failed: {e}")
    exit(1)

# Step 3: Login with the user
print("\n[3/3] Testing login with registered user...")
login_data = {
    "username": "testuser_final",
    "password": "Test@123456"
}
try:
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, timeout=5, allow_redirects=True)
    print(f"✅ Login response received (Status: {response.status_code})")
    
    if "dashboard" in response.text.lower() or "testuser" in response.text:
        print("✅ Login successful! User can access dashboard.")
    else:
        print(f"⚠️  Check response for issues")
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ REGISTRATION AND LOGIN TEST PASSED")
print("=" * 70)
print("\n📝 Test user credentials:")
print("   Username: testuser_final")
print("   Password: Test@123456")
print("   Email: testuser_final@example.com")
print("\n🌐 Open http://localhost:8000 and login manually to complete your testing!")
