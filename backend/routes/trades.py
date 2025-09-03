from flask import Blueprint, request, jsonify
from database import db
from models.trade import Trade
from models.position import Position
from utils.decorators import require_auth
from datetime import datetime
import uuid

trades_bp = Blueprint('trades', __name__)

@trades_bp.route('/', methods=['GET'])
@require_auth
def get_trades():
    """Get all trades for the authenticated user with optional filtering"""
    try:
        user = request.current_user
        
        # Get query parameters for filtering
        trading_type = request.args.get('trading_type')
        win_loss = request.args.get('win_loss')
        status = request.args.get('status')  # 'OPEN' or 'CLOSED'
        transaction_type = request.args.get('transaction_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query - only get trades for the current user
        query = Trade.query.filter(Trade.user_id == user.id)
        
        if trading_type:
            query = query.filter(Trade.trading_type == trading_type)
        if win_loss:
            query = query.filter(Trade.win_loss == win_loss)
        if status:
            query = query.filter(Trade.status == status)
        if transaction_type:
            query = query.filter(Trade.transaction_type == transaction_type)
        if date_from:
            query = query.filter(Trade.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(Trade.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        # Order by status (OPEN first) then by date descending
        trades = query.order_by(Trade.status.desc(), Trade.date.desc()).all()
        
        # Get open positions for additional context
        open_positions = Position.query.filter_by(user_id=user.id, status='OPEN').all()
        
        return jsonify({
            'success': True,
            'trades': [trade.to_dict() for trade in trades],
            'open_positions': [pos.to_dict() for pos in open_positions]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trades_bp.route('/', methods=['POST'])
@require_auth
def create_trade():
    """Create a new trade for the authenticated user"""
    try:
        user = request.current_user
        data = request.get_json()

        # Validate required fields
        required_fields = ['date', 'ticker_symbol', 'number_of_shares', 'buy_price', 'trading_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # Validate trading type
        if data['trading_type'] not in ['Swing', 'Day']:
            return jsonify({
                'success': False,
                'error': 'Trading type must be either "Swing" or "Day"'
            }), 400

        # Parse date
        trade_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Determine if this is an open or closed position
        sell_price = data.get('sell_price')
        # Handle empty string case - convert to None for open positions
        if sell_price == '' or sell_price is None:
            sell_price = None
            status = 'OPEN'
        else:
            status = 'CLOSED'
        
        # Create trade with user association
        trade = Trade(
            date=trade_date,
            ticker_symbol=data['ticker_symbol'],
            number_of_shares=data['number_of_shares'],
            buy_price=data['buy_price'],
            sell_price=sell_price,
            trading_type=data['trading_type'],
            user_id=user.id,
            status=status,
            transaction_type=data.get('transaction_type', 'stock')
        )
        
        # If this is an open position, create a position record
        if status == 'OPEN':
            position = Position(
                user_id=user.id,
                symbol=data['ticker_symbol'],
                total_shares=data['number_of_shares'],
                buy_price=data['buy_price'],
                buy_date=trade_date
            )
            db.session.add(position)
            trade.position_id = position.id

        db.session.add(trade)
        db.session.commit()

        return jsonify({
            'success': True,
            'trade': trade.to_dict(),
            'message': 'Trade created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error creating trade: {str(e)}")  # Add logging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trades_bp.route('/<trade_id>', methods=['GET'])
@require_auth
def get_trade(trade_id):
    """Get a specific trade by ID for the authenticated user"""
    try:
        user = request.current_user
        trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
        
        if not trade:
            return jsonify({
                'success': False,
                'error': 'Trade not found'
            }), 404

        return jsonify({
            'success': True,
            'trade': trade.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trades_bp.route('/<trade_id>', methods=['PUT'])
@require_auth
def update_trade(trade_id):
    """Update a trade"""
    try:
        user = request.current_user
        trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
        if not trade:
            return jsonify({
                'success': False,
                'error': 'Trade not found'
            }), 404

        data = request.get_json()

        # Update fields if provided
        if 'date' in data:
            trade.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'ticker_symbol' in data:
            trade.ticker_symbol = data['ticker_symbol'].upper()
        if 'number_of_shares' in data:
            trade.number_of_shares = data['number_of_shares']
        if 'buy_price' in data:
            trade.buy_price = float(data['buy_price'])
        if 'sell_price' in data:
            trade.sell_price = float(data['sell_price'])
        if 'trading_type' in data:
            if data['trading_type'] not in ['Swing', 'Day']:
                return jsonify({
                    'success': False,
                    'error': 'Trading type must be either "Swing" or "Day"'
                }), 400
            trade.trading_type = data['trading_type']

        # Auto-calculate price_cost_basis and proceeds
        if trade.buy_price is not None and trade.number_of_shares is not None:
            trade.price_cost_basis = trade.number_of_shares * float(trade.buy_price)
        if trade.sell_price is not None and trade.number_of_shares is not None:
            trade.proceeds = trade.number_of_shares * float(trade.sell_price)

        # Recalculate win/loss
        total_cost = trade.price_cost_basis
        trade.win_loss = 'Win' if trade.proceeds > total_cost else 'Loss'

        db.session.commit()

        return jsonify({
            'success': True,
            'trade': trade.to_dict(),
            'message': 'Trade updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@trades_bp.route('/<trade_id>', methods=['DELETE'])
@require_auth
def delete_trade(trade_id):
    print("deteing trade")
    """Delete a trade"""
    try:
        user = request.current_user
        trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
        print(trade)
        if not trade:
            return jsonify({
                'success': False,
                'error': 'Trade not found'
            }), 404
        db.session.delete(trade)
        print("success delete")
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Trade deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Explicit OPTIONS handler for CORS preflight
@trades_bp.route('/<trade_id>', methods=['OPTIONS'])
def options_trade(trade_id):
    return ('', 204) 

# Catch-all OPTIONS handler for CORS preflight on any /api/trades/* route
@trades_bp.route('/<path:dummy>', methods=['OPTIONS'])
def catch_all_options(dummy):
    return ('', 204) 