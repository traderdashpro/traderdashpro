from sqlalchemy import Column, String, Integer, Numeric, Date, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
import uuid


class Position(db.Model):
    __tablename__ = 'positions'
    
    id = Column(String(20), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    symbol = Column(String(10), nullable=False)
    status = Column(String(10), nullable=False, default='OPEN')
    total_shares = Column(Integer, nullable=False)
    buy_price = Column(Numeric(precision=10, scale=2), nullable=False)
    buy_date = Column(Date, nullable=False)
    sell_price = Column(Numeric(precision=10, scale=2), nullable=True)
    sell_date = Column(Date, nullable=True)
    pnl = Column(Numeric(precision=10, scale=2), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text('now()'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="positions")
    trades = relationship("Trade", back_populates="position")
    
    def __init__(self, user_id, symbol, total_shares, buy_price, buy_date, **kwargs):
        self.id = f"POS_{str(uuid.uuid4())[:8].upper()}"
        self.user_id = user_id
        self.symbol = symbol
        self.total_shares = total_shares
        self.buy_price = buy_price
        self.buy_date = buy_date
        self.status = 'OPEN'
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'status': self.status,
            'total_shares': self.total_shares,
            'buy_price': float(self.buy_price) if self.buy_price else None,
            'buy_date': self.buy_date.isoformat() if self.buy_date else None,
            'sell_price': float(self.sell_price) if self.sell_price else None,
            'sell_date': self.sell_date.isoformat() if self.sell_date else None,
            'pnl': float(self.pnl) if self.pnl else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def close_position(self, sell_price, sell_date):
        """Close the position and calculate P&L"""
        self.sell_price = sell_price
        self.sell_date = sell_date
        self.status = 'CLOSED'
        self.pnl = (sell_price - self.buy_price) * self.total_shares
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def generate_position_id():
        """Generate a unique position ID"""
        return f"POS_{str(uuid.uuid4())[:8].upper()}"
