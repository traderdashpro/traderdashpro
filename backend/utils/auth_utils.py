import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import re

def generate_jwt_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=1),  # 1 hour expiration
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_confirmation_token():
    """Generate a unique confirmation token"""
    return str(uuid.uuid4())

def send_confirmation_email(user_email, confirmation_token):
    """Send confirmation email to user"""
    from app import mail
    
    confirmation_url = f"https://traderdashpro.vercel.app/confirm-email?token={confirmation_token}"
    
    msg = Message(
        'Confirm Your Email - Trading Insights',
        recipients=[user_email],
        body=f'''
        Welcome to Trading Insights!
        
        Please confirm your email address by clicking the link below:
        {confirmation_url}
        
        If you didn't create an account, you can safely ignore this email.
        
        Best regards,
        Trading Insights Team
        ''',
        html=f'''
        <h2>Welcome to Trading Insights!</h2>
        <p>Please confirm your email address by clicking the link below:</p>
        <p><a href="{confirmation_url}">Confirm Email</a></p>
        <p>If you didn't create an account, you can safely ignore this email.</p>
        <br>
        <p>Best regards,<br>Trading Insights Team</p>
        '''
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def hash_password(password):
    """Hash password using werkzeug"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Verify password against hash"""
    return check_password_hash(password_hash, password) 