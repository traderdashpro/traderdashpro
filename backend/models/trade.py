from database import db
from datetime import datetime
import uuid
#import user model
from models.user import User

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, nullable=False)
    ticker_symbol = db.Column(db.String(10), nullable=False)
    number_of_shares = db.Column(db.Integer, nullable=False)
    price_cost_basis = db.Column(db.Numeric(10, 2), nullable=False)
    proceeds = db.Column(db.Numeric(10, 2), nullable=False)
    trading_type = db.Column(db.String(10), nullable=False)  # 'Swing' or 'Day'
    win_loss = db.Column(db.String(10), nullable=False)  # 'Win' or 'Loss'
    buy_price = db.Column(db.Numeric(10, 2), nullable=True)
    sell_price = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='trades')
    
    # Position tracking fields
    status = db.Column(db.String(10), nullable=False, default='CLOSED')
    position_id = db.Column(db.String(20), db.ForeignKey('positions.id'), nullable=True)
    shares_remaining = db.Column(db.Integer, nullable=True)
    
    # Relationships
    position = db.relationship('Position', back_populates='trades')
    
    # Relationship with journal entries
    journal_entries = db.relationship('JournalEntry', backref='trade', lazy=True)
    
    def __init__(self, date, ticker_symbol, number_of_shares, buy_price, sell_price, trading_type, user_id=None, status='CLOSED', position_id=None, shares_remaining=None):
        self.date = date
        self.ticker_symbol = ticker_symbol.upper()
        self.number_of_shares = int(number_of_shares)
        self.buy_price = float(buy_price) if buy_price is not None else None
        self.sell_price = float(sell_price) if sell_price is not None else None
        self.price_cost_basis = self.number_of_shares * self.buy_price if self.buy_price is not None else None
        self.proceeds = self.number_of_shares * self.sell_price if self.sell_price is not None else None
        self.trading_type = trading_type
        self.user_id = user_id
        self.status = status
        self.position_id = position_id
        self.shares_remaining = shares_remaining
        
        # Auto-detect win/loss based on proceeds vs cost basis (only for closed trades)
        if self.sell_price is not None:
            total_cost = self.price_cost_basis
            self.win_loss = 'Win' if self.proceeds > total_cost else 'Loss'
        else:
            self.win_loss = 'Pending'  # For open positions
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'date': self.date.isoformat(),
            'ticker_symbol': self.ticker_symbol,
            'number_of_shares': self.number_of_shares,
            'price_cost_basis': float(self.price_cost_basis) if self.price_cost_basis is not None else None,
            'proceeds': float(self.proceeds) if self.proceeds is not None else None,
            'buy_price': float(self.buy_price) if self.buy_price is not None else None,
            'sell_price': float(self.sell_price) if self.sell_price is not None else None,
            'trading_type': self.trading_type,
            'win_loss': self.win_loss,
            'status': self.status,
            'position_id': self.position_id,
            'shares_remaining': self.shares_remaining,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def calculate_profit_loss(self):
        """Calculate profit/loss for this trade"""
        if self.proceeds is None or self.price_cost_basis is None:
            return None
        return float(self.proceeds) - float(self.price_cost_basis) 