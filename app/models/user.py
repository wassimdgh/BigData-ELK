"""
User Model for Authentication
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from app.services.database import get_mongodb
from datetime import datetime


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_id, username, email, role='viewer', is_active=True, is_admin=False):
        self.id = str(user_id)
        self.username = username
        self.email = email
        self.role = role
        self._is_active = is_active
        self.is_admin = is_admin
    
    @property
    def is_active(self):
        """Check if user is active"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Set user active status"""
        self._is_active = value
    
    @property
    def is_authenticated(self):
        """Check if user is authenticated"""
        return True
    
    @property
    def is_anonymous(self):
        """Check if user is anonymous"""
        return False
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        mongo = get_mongodb()
        user_doc = mongo.users.find_one({'username': username})
        
        if not user_doc:
            return None
        
        return User(
            user_id=user_doc['_id'],
            username=user_doc['username'],
            email=user_doc['email'],
            role=user_doc.get('role', 'viewer'),
            is_active=user_doc.get('is_active', True),
            is_admin=user_doc.get('is_admin', False)
        )
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        import logging
        logger = logging.getLogger(__name__)
        mongo = get_mongodb()
        try:
            logger.debug(f'Finding user by ID: {user_id}')
            obj_id = ObjectId(user_id)
            user_doc = mongo.users.find_one({'_id': obj_id})
            
            if not user_doc:
                logger.warning(f'User document not found for ID: {user_id}')
                return None
            
            return User(
                user_id=user_doc['_id'],
                username=user_doc['username'],
                email=user_doc['email'],
                role=user_doc.get('role', 'viewer'),
                is_active=user_doc.get('is_active', True),
                is_admin=user_doc.get('is_admin', False)
            )
        except Exception as e:
            logger.error(f'Error finding user by ID {user_id}: {str(e)}')
            return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        mongo = get_mongodb()
        user_doc = mongo.users.find_one({'email': email})
        
        if not user_doc:
            return None
        
        return User(
            user_id=user_doc['_id'],
            username=user_doc['username'],
            email=user_doc['email'],
            role=user_doc.get('role', 'viewer'),
            is_active=user_doc.get('is_active', True),
            is_admin=user_doc.get('is_admin', False)
        )
    
    @staticmethod
    def create_user(username, email, password, role='viewer', is_admin=False):
        """Create a new user"""
        mongo = get_mongodb()
        
        # Check if user already exists
        if mongo.users.find_one({'username': username}):
            return None, "Username already exists"
        
        if mongo.users.find_one({'email': email}):
            return None, "Email already exists"
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create user document
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'is_admin': is_admin,
            'created_at': datetime.now(),
            'last_login': None
        }
        
        result = mongo.users.insert_one(user_doc)
        
        return User(
            user_id=result.inserted_id,
            username=username,
            email=email,
            role=role,
            is_admin=is_admin
        ), "User created successfully"
    
    @staticmethod
    def verify_password(username, password):
        """Verify password for a user"""
        mongo = get_mongodb()
        user_doc = mongo.users.find_one({'username': username})
        
        if not user_doc:
            return False
        
        if not check_password_hash(user_doc['password_hash'], password):
            return False
        
        # Update last login
        mongo.users.update_one(
            {'_id': user_doc['_id']},
            {'$set': {'last_login': datetime.now()}}
        )
        
        return True
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        mongo = get_mongodb()
        users = []
        for user_doc in mongo.users.find():
            users.append({
                '_id': str(user_doc['_id']),
                'username': user_doc['username'],
                'email': user_doc['email'],
                'role': user_doc.get('role', 'viewer'),
                'is_active': user_doc.get('is_active', True),
                'is_admin': user_doc.get('is_admin', False),
                'created_at': user_doc.get('created_at', '').isoformat() if isinstance(user_doc.get('created_at'), datetime) else user_doc.get('created_at', ''),
                'last_login': user_doc.get('last_login', '').isoformat() if isinstance(user_doc.get('last_login'), datetime) else user_doc.get('last_login', '')
            })
        return users
    
    def update_role(self, new_role):
        """Update user role"""
        mongo = get_mongodb()
        mongo.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'role': new_role}}
        )
        self.role = new_role
    
    def deactivate(self):
        """Deactivate user"""
        mongo = get_mongodb()
        mongo.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_active': False}}
        )
        self.is_active = False
    
    def activate(self):
        """Activate user"""
        mongo = get_mongodb()
        mongo.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'is_active': True}}
        )
        self.is_active = True
