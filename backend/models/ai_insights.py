from database import db
from datetime import datetime
import uuid

class AIInsights(db.Model):
    __tablename__ = 'ai_insights'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    insights_data = db.Column(db.Text, nullable=False)  # JSON string of insights
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, insights_data):
        self.user_id = user_id
        self.insights_data = insights_data
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'insights_data': self.insights_data,
            'created_at': self.created_at.isoformat()
        } 