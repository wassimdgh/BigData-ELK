"""
Initialize application with demo data and default admin user
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.user import User
from app.services.database import get_mongodb
from datetime import datetime

def init_db():
    """Initialize database with demo users"""
    
    print("=" * 70)
    print("🔧 Initializing Application Database")
    print("=" * 70)
    
    # Check if admin exists
    existing_admin = User.find_by_username('admin')
    if existing_admin:
        print("✓ Admin user already exists")
    else:
        print("Creating admin user...")
        admin, msg = User.create_user(
            username='admin',
            email='admin@smartbuilding.local',
            password='admin123',
            role='admin',
            is_admin=True
        )
        if admin:
            print(f"✓ Admin user created: {msg}")
        else:
            print(f"✗ Failed to create admin: {msg}")
    
    # Create demo users
    demo_users = [
        {
            'username': 'viewer1',
            'email': 'viewer1@smartbuilding.local',
            'password': 'viewer123',
            'role': 'viewer'
        },
        {
            'username': 'analyst1',
            'email': 'analyst1@smartbuilding.local',
            'password': 'analyst123',
            'role': 'analyst'
        }
    ]
    
    for user_data in demo_users:
        existing = User.find_by_username(user_data['username'])
        if existing:
            print(f"✓ User {user_data['username']} already exists")
        else:
            user, msg = User.create_user(**user_data)
            if user:
                print(f"✓ User {user_data['username']} created")
            else:
                print(f"✗ Failed to create {user_data['username']}: {msg}")
    
    # List all users
    print("\n" + "=" * 70)
    print("📋 All Users in Database:")
    print("=" * 70)
    users = User.get_all_users()
    for user in users:
        print(f"\nUsername: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"  Role: {user['role']}")
        print(f"  Admin: {user['is_admin']}")
        print(f"  Active: {user['is_active']}")
    
    print("\n" + "=" * 70)
    print("✓ Database initialization complete!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)
