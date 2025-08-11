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
    plan = db.Column(db.String(20), default='free')  # 'free', 'premium', 'pro'
    last_ai_insights_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email, password, confirmation_token=None, is_confirmed=False, plan='free'):
        self.email = email.lower().strip()
        self.set_password(password)
        self.confirmation_token = confirmation_token
        self.is_confirmed = is_confirmed
        self.plan = plan

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_get_ai_insights(self):
        """Check if user can get AI insights based on their plan"""
        if self.plan == 'free':
            if not self.last_ai_insights_date:
                return True
            # Free users can get insights once per week
            from datetime import timedelta
            next_available = self.last_ai_insights_date + timedelta(days=7)
            return datetime.utcnow() >= next_available
        # Premium and pro users have unlimited access
        return True
    
    def get_next_ai_insights_date(self):
        """Get the next available date for AI insights"""
        if self.plan != 'free' or not self.last_ai_insights_date:
            return None
        from datetime import timedelta
        return self.last_ai_insights_date + timedelta(days=7)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'is_confirmed': self.is_confirmed,
            'plan': self.plan,
            'last_ai_insights_date': self.last_ai_insights_date.isoformat() if self.last_ai_insights_date else None,
            'next_ai_insights_date': self.get_next_ai_insights_date().isoformat() if self.get_next_ai_insights_date() else None,
            'can_get_ai_insights': self.can_get_ai_insights(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }