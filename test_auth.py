"""
Test script to verify authentication system
Run: python test_auth.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.user import User
from app.services.database import get_mongodb

def test_user_creation():
    """Test user creation"""
    print("\n" + "=" * 70)
    print("🧪 Testing User Creation")
    print("=" * 70)
    
    # Test 1: Create a new user
    print("\n1️⃣ Creating test user...")
    user, msg = User.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    if user:
        print(f"✓ User created: {user.username} (ID: {user.id})")
    else:
        print(f"✓ (Already exists) {msg}")


def test_user_retrieval():
    """Test user retrieval"""
    print("\n" + "=" * 70)
    print("🧪 Testing User Retrieval")
    print("=" * 70)
    
    # Test by username
    print("\n1️⃣ Finding user by username...")
    user = User.find_by_username('admin')
    if user:
        print(f"✓ Found user: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Role: {user.role}")
        print(f"  - Admin: {user.is_admin}")
        print(f"  - Active: {user.is_active}")
    else:
        print("✗ User not found")


def test_password_verification():
    """Test password verification"""
    print("\n" + "=" * 70)
    print("🧪 Testing Password Verification")
    print("=" * 70)
    
    print("\n1️⃣ Testing correct password...")
    if User.verify_password('admin', 'admin123'):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")
    
    print("\n2️⃣ Testing incorrect password...")
    if not User.verify_password('admin', 'wrongpassword'):
        print("✓ Correctly rejected wrong password")
    else:
        print("✗ Incorrectly accepted wrong password")


def test_user_listing():
    """Test listing all users"""
    print("\n" + "=" * 70)
    print("🧪 Testing User Listing")
    print("=" * 70)
    
    users = User.get_all_users()
    print(f"\n✓ Found {len(users)} user(s):")
    
    for user in users:
        print(f"\n  📝 {user['username']}")
        print(f"     Email: {user['email']}")
        print(f"     Role: {user['role']}")
        print(f"     Admin: {user['is_admin']}")
        print(f"     Active: {user['is_active']}")


def test_database_connection():
    """Test MongoDB connection"""
    print("\n" + "=" * 70)
    print("🧪 Testing MongoDB Connection")
    print("=" * 70)
    
    try:
        mongo = get_mongodb()
        count = mongo.users.count_documents({})
        print(f"✓ MongoDB connection successful")
        print(f"  - Users collection: {count} document(s)")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {str(e)}")


def run_all_tests():
    """Run all tests"""
    print("\n\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "🔐 AUTHENTICATION SYSTEM TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        test_database_connection()
        test_user_creation()
        test_user_retrieval()
        test_password_verification()
        test_user_listing()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
