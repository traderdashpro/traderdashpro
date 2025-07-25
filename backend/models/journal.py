from database import db
from datetime import datetime
import uuid

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=False)
    trade_id = db.Column(db.String(36), db.ForeignKey('trades.id'), nullable=True)
    entry_type = db.Column(db.String(20), nullable=False, default='general')  # 'trade_specific' or 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, date, notes, trade_id=None, entry_type='general'):
        self.date = date
        self.notes = notes
        self.trade_id = trade_id
        self.entry_type = entry_type
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.isoformat(),
            'notes': self.notes,
            'trade_id': str(self.trade_id) if self.trade_id else None,
            'entry_type': self.entry_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 