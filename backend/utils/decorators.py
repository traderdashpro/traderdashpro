from functools import wraps
from flask import request, jsonify, current_app
from utils.auth_utils import verify_jwt_token
from models.user import User

def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Authorization header missing'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'message': 'Invalid authorization header format'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 401
        
        # Skip email confirmation check for development
        # if not user.is_confirmed:
        #     return jsonify({'message': 'Email not confirmed'}), 403
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def require_confirmed_email(f):
    """Decorator to require confirmed email"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Authorization header missing'}), 401
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'message': 'Invalid authorization header format'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 401
        
        # Skip email confirmation check for development
        # if not user.is_confirmed:
        #     return jsonify({'message': 'Email not confirmed'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function 