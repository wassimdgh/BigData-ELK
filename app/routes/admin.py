"""
Admin Routes for User Management
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.services.auth_decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    users = User.get_all_users()
    return render_template('admin/dashboard.html', users=users)


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users"""
    users = User.get_all_users()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<user_id>/role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['admin', 'analyst', 'viewer']:
            return jsonify({'error': 'Invalid role'}), 400
        
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.update_role(new_role)
        return jsonify({'message': 'Role updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user"""
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Cannot deactivate self
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate yourself'}), 400
        
        user.deactivate()
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate user"""
    try:
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.activate()
        return jsonify({'message': 'User activated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    """Get all users (API endpoint)"""
    users = User.get_all_users()
    return jsonify({'users': users}), 200


@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def api_admin_stats():
    """Get admin statistics"""
    from app.services.database import get_mongodb, get_elasticsearch
    
    mongo = get_mongodb()
    es = get_elasticsearch()
    
    stats = {
        'total_users': mongo.users.count_documents({}),
        'total_files': mongo.uploaded_files.count_documents({}),
        'total_logs': 0
    }
    
    try:
        result = es.count(index='iot-logs-*')
        stats['total_logs'] = result['count']
    except:
        stats['total_logs'] = 0
    
    return jsonify(stats), 200
