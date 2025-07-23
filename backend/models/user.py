from database import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email, password, confirmation_token=None, is_confirmed=False):
        self.email = email.lower().strip()
        self.set_password(password)
        self.confirmation_token = confirmation_token
        self.is_confirmed = is_confirmed

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'is_confirmed': self.is_confirmed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }