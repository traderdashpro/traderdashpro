from flask import Blueprint, request, jsonify, current_app
from database import db
from models.user import User
from utils.auth_utils import (
    generate_jwt_token, 
    generate_confirmation_token, 
    send_confirmation_email,
    validate_email,
    validate_password,
    hash_password,
    verify_password
)
from utils.decorators import require_auth
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({'message': password_message}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 409
        
        # Generate confirmation token (but we'll auto-confirm for now)
        confirmation_token = generate_confirmation_token()
        
        # Create user with auto-confirmation for development
        user = User(
            email=email,
            password=password,
            confirmation_token=confirmation_token,
            is_confirmed=True  # Auto-confirm for development
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Skip email sending for now
        # email_sent = send_confirmation_email(email, confirmation_token)
        
        response_data = {
            'message': 'Registration successful! (Email confirmation disabled for development)',
            'user_id': str(user.id),
            'email': user.email,
            'is_confirmed': True
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(user.password_hash, password):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Skip email confirmation check for development
        # if not user.is_confirmed:
        #     return jsonify({
        #         'message': 'Email not confirmed. Please check your email and click the confirmation link.',
        #         'email_not_confirmed': True
        #     }), 403
        
        # Generate JWT token
        token = generate_jwt_token(str(user.id), user.email)
        
        # Update last login
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'is_confirmed': user.is_confirmed
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/confirm-email', methods=['POST'])
def confirm_email():
    """Email confirmation endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'message': 'Confirmation token is required'}), 400
        
        # Find user by confirmation token
        user = User.query.filter_by(confirmation_token=token).first()
        
        if not user:
            return jsonify({'message': 'Invalid or expired confirmation token'}), 400
        
        if user.is_confirmed:
            return jsonify({'message': 'Email already confirmed'}), 400
        
        # Confirm email
        user.is_confirmed = True
        user.confirmation_token = None
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Email confirmed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email confirmation error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    """Resend confirmation email endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.is_confirmed:
            return jsonify({'message': 'Email already confirmed'}), 400
        
        # Generate new confirmation token
        confirmation_token = generate_confirmation_token()
        user.confirmation_token = confirmation_token
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send confirmation email
        email_sent = send_confirmation_email(email, confirmation_token)
        
        if email_sent:
            return jsonify({'message': 'Confirmation email sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send confirmation email'}), 500
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Resend confirmation error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        user = request.current_user
        
        return jsonify({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'is_confirmed': user.is_confirmed,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        user = request.current_user
        
        # Verify current password
        if not verify_password(user.password_hash, current_password):
            return jsonify({'message': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({'message': password_message}), 400
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout endpoint (client should discard token)"""
    # Since JWT tokens are stateless, we just return success
    # The client should discard the token
    return jsonify({'message': 'Logged out successfully'}), 200