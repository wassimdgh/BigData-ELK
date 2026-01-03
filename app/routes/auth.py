"""
Authentication Routes
Handles login, register, logout, and user management
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verify password
        if not User.verify_password(username, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user
        user = User.find_by_username(username)
        if not user or not user.is_active:
            flash('User not found or inactive', 'danger')
            return redirect(url_for('auth.login'))
        
        # Login user with permanent session
        import logging
        logger = logging.getLogger(__name__)
        session.permanent = True
        login_result = login_user(user, remember=remember)
        logger.info(f'🔐 User login: {username}, remember={remember}, success={login_result}, session_id={session.get("_id", "none")}')
        
        flash(f'Welcome back, {username}!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register page and handler"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(username) < 3:
            flash('Username must be at least 3 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        user, message = User.create_user(username, email, password)
        
        if not user:
            flash(message, 'danger')
            return redirect(url_for('auth.register'))
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout handler"""
    username = current_user.username
    logout_user()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API login endpoint (for AJAX)"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    
    # Verify password
    if not User.verify_password(username, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Get user
    user = User.find_by_username(username)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    # Login user with permanent session
    session.permanent = True
    login_user(user, remember=remember)
    
    return jsonify({
        'message': 'Logged in successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_admin': user.is_admin
        }
    }), 200


@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API register endpoint (for AJAX)"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    
    # Validation
    if not all([username, email, password, password_confirm]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if password != password_confirm:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Create user
    user, message = User.create_user(username, email, password)
    
    if not user:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message}), 201


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API logout endpoint"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/api/current-user', methods=['GET'])
def api_current_user():
    """Get current authenticated user"""
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'role': current_user.role,
            'is_admin': current_user.is_admin
        }), 200
    return jsonify({'authenticated': False}), 401
