from flask import Blueprint, request, jsonify
from database import db
from models.trade import Trade
from models.position import Position
from utils.decorators import require_auth
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
from io import StringIO
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Get dashboard statistics for the authenticated user"""
    try:
        user = request.current_user
        
        # Get query parameters
        trading_type = request.args.get('trading_type')  # 'Swing', 'Day', or None for all
        
        # Build base query - only get trades for the current user
        query = Trade.query.filter(Trade.user_id == user.id)
        
        if trading_type:
            query = query.filter(Trade.trading_type == trading_type)
        
        # Get all trades for calculations
        trades = query.all()
        
        if not trades:
            return jsonify({
                'success': True,
                'stats': {
                    'total_trades': 0,
                    'win_count': 0,
                    'loss_count': 0,
                    'win_rate': 0,
                    'total_profit_loss': 0,
                    'avg_profit_loss': 0
                }
            }), 200
        
        # Calculate statistics - only count closed trades for P&L calculations
        total_trades = len(trades)
        closed_trades = [t for t in trades if t.status == 'CLOSED']
        open_trades = [t for t in trades if t.status == 'OPEN']
        
        win_count = len([t for t in closed_trades if t.win_loss == 'Win'])
        loss_count = len([t for t in closed_trades if t.win_loss == 'Loss'])
        win_rate = (win_count / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
        
        # Calculate profit/loss only for closed trades
        total_profit_loss = sum(t.calculate_profit_loss() for t in closed_trades if t.calculate_profit_loss() is not None)
        avg_profit_loss = total_profit_loss / len(closed_trades) if len(closed_trades) > 0 else 0
        
        # Get recent closed trades (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_closed_trades = [t for t in closed_trades if t.date >= thirty_days_ago]
        recent_profit_loss = sum(t.calculate_profit_loss() for t in recent_closed_trades if t.calculate_profit_loss() is not None)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_trades': total_trades,
                'win_count': win_count,
                'loss_count': loss_count,
                'win_rate': round(win_rate, 2),
                'total_profit_loss': round(total_profit_loss, 2),
                'avg_profit_loss': round(avg_profit_loss, 2),
                'recent_profit_loss': round(recent_profit_loss, 2),
                'recent_trades_count': len(recent_closed_trades)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in dashboard stats: {str(e)}")  # Add logging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/chart', methods=['GET'])
@require_auth
def get_chart_data():
    """Get chart data for dashboard for the authenticated user"""
    try:
        user = request.current_user
        
        # Get query parameters
        trading_type = request.args.get('trading_type')  # 'Swing', 'Day', or None for all
        
        # Build base query - only get trades for the current user
        query = Trade.query.filter(Trade.user_id == user.id)
        
        if trading_type:
            query = query.filter(Trade.trading_type == trading_type)
        
        # Get all trades
        trades = query.all()
        
        if not trades:
            return jsonify({
                'success': True,
                'donut_chart': {
                    'labels': [],
                    'data': [],
                    'backgroundColor': []
                },
                'line_chart': {
                    'labels': [],
                    'data': []
                }
            }), 200
        
        # Get win/loss distribution for donut chart - only closed trades
        closed_trades = [t for t in trades if t.status == 'CLOSED']
        win_count = len([t for t in closed_trades if t.win_loss == 'Win'])
        loss_count = len([t for t in closed_trades if t.win_loss == 'Loss'])
        
        # Format data for donut chart
        chart_data = {
            'labels': [],
            'data': [],
            'backgroundColor': []
        }
        
        # Add Win data if there are wins
        if win_count > 0:
            chart_data['labels'].append('Win')
            chart_data['data'].append(win_count)
            chart_data['backgroundColor'].append('#10B981')  # Green
        
        # Add Loss data if there are losses
        if loss_count > 0:
            chart_data['labels'].append('Loss')
            chart_data['data'].append(loss_count)
            chart_data['backgroundColor'].append('#EF4444')  # Red
        
        # If no wins or losses, add a placeholder
        if not chart_data['labels']:
            chart_data['labels'].append('No Data')
            chart_data['data'].append(1)
            chart_data['backgroundColor'].append('#6B7280')  # Gray
        
        # Get daily profit/loss data for line chart - only closed trades
        daily_data = {}
        for trade in closed_trades:
            profit_loss = trade.calculate_profit_loss()
            if profit_loss is not None:  # Only include trades with valid P&L
                day = trade.date.strftime('%Y-%m-%d')
                if day not in daily_data:
                    daily_data[day] = 0
                daily_data[day] += profit_loss
        
        # Sort by day and format for chart
        sorted_days = sorted(daily_data.keys())
        daily_chart_data = {
            'labels': [],
            'data': []
        }
        for day in sorted_days:
            daily_chart_data['labels'].append(day)
            daily_chart_data['data'].append(round(daily_data[day], 2))
        return jsonify({
            'success': True,
            'donut_chart': chart_data,
            'line_chart': daily_chart_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/trading-type-stats', methods=['GET'])
@require_auth
def get_trading_type_stats():
    """Get statistics by trading type for the authenticated user"""
    try:
        user = request.current_user
        
        # Get stats for Swing trades - only closed trades for P&L calculations
        swing_trades = Trade.query.filter(Trade.user_id == user.id, Trade.trading_type == 'Swing').all()
        closed_swing_trades = [t for t in swing_trades if t.status == 'CLOSED']
        swing_stats = {
            'total_trades': len(swing_trades),
            'win_count': len([t for t in closed_swing_trades if t.win_loss == 'Win']),
            'loss_count': len([t for t in closed_swing_trades if t.win_loss == 'Loss']),
            'total_profit_loss': sum(t.calculate_profit_loss() for t in closed_swing_trades if t.calculate_profit_loss() is not None),
            'win_rate': 0
        }
        if len(closed_swing_trades) > 0:
            swing_stats['win_rate'] = round((swing_stats['win_count'] / len(closed_swing_trades)) * 100, 2)
        
        # Get stats for Day trades - only closed trades for P&L calculations
        day_trades = Trade.query.filter(Trade.user_id == user.id, Trade.trading_type == 'Day').all()
        closed_day_trades = [t for t in day_trades if t.status == 'CLOSED']
        day_stats = {
            'total_trades': len(day_trades),
            'win_count': len([t for t in closed_day_trades if t.win_loss == 'Win']),
            'loss_count': len([t for t in closed_day_trades if t.win_loss == 'Loss']),
            'total_profit_loss': sum(t.calculate_profit_loss() for t in closed_day_trades if t.calculate_profit_loss() is not None),
            'win_rate': 0
        }
        if len(closed_day_trades) > 0:
            day_stats['win_rate'] = round((day_stats['win_count'] / len(closed_day_trades)) * 100, 2)
        
        return jsonify({
            'success': True,
            'swing_stats': swing_stats,
            'day_stats': day_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@dashboard_bp.route('/upload-statement', methods=['POST'])
@require_auth
def upload_statement():
    user = request.current_user
    platform = request.form.get('platform')
    file = request.files.get('file')
    if not platform or not file:
        return jsonify({'error': 'Platform and file are required.'}), 400
    if platform.lower() != "thinkorswim":
        return jsonify({'error': 'Only Thinkorswim supported for now.'}), 400

    content = file.read()
    text = content.decode("utf-8")
    f = StringIO(text)
    reader = csv.reader(f)
    lines = list(reader)

    # Find the start of the Account Trade History section
    trade_section = False
    trades = []
    for i, row in enumerate(lines):
        if any("Account Trade History" in cell for cell in row):
            trade_section = True
            header_row = i + 1
            break
    if not trade_section:
        return jsonify({'error': "No 'Account Trade History' section found."}), 400

    # Parse trades
    trade_headers = lines[header_row]
    for row in lines[header_row+1:]:
        if not any(row):
            break  # End of section
        # Skip empty or malformed rows
        if len(row) < 12 or not row[2].strip():
            continue
        trade = dict(zip(trade_headers, row))
        trades.append(trade)

    # Calculate P&L and track positions
    pnl_by_symbol: dict[str, float] = {}
    symbol_trades = defaultdict(list)
    new_trades = []
    new_positions = []
    closed_positions = []
    
    # Get existing open positions for this user
    existing_positions = Position.query.filter_by(user_id=user.id, status='OPEN').all()
    open_positions = {pos.symbol: pos for pos in existing_positions}
    
    for trade in trades:
        symbol = trade.get("Symbol", "").strip()
        side = trade.get("Side", "").strip().upper()
        try:
            qty_str = trade.get("Qty", "0").replace(",", "") if trade.get("Qty") else "0"
            qty = abs(float(qty_str))
            price = float(trade.get("Price", "0").replace(",", "")) if trade.get("Price") else 0.0
        except Exception:
            qty = 0.0
            price = 0.0
            
        if symbol:
            if symbol not in pnl_by_symbol:
                pnl_by_symbol[symbol] = 0.0
            if side == "BUY":
                pnl_by_symbol[symbol] -= qty * price
            elif side == "SELL":
                pnl_by_symbol[symbol] += qty * price
            symbol_trades[symbol].append({"side": side, "qty": qty, "price": price})

    # Process each symbol for position tracking
    closed_trades_count = 0
    day_trades = 0
    swing_trades = 0
    
    for symbol, actions in symbol_trades.items():
        position = 0
        open_dates = []
        close_dates = []
        buy_legs = []
        sell_legs = []
        
        for idx, action in enumerate(actions):
            # Parse date from trade row
            trade_row = trades[[i for i, t in enumerate(trades) if t.get('Symbol', '').strip() == symbol][idx]]
            exec_time_str = trade_row.get('Exec Time') or trade_row.get('ExecTime') or trade_row.get('Date')
            exec_date = None
            if exec_time_str:
                try:
                    exec_date = datetime.strptime(exec_time_str.split()[0], '%m/%d/%y').date()
                except Exception:
                    try:
                        exec_date = datetime.strptime(exec_time_str, '%m/%d/%y').date()
                    except Exception:
                        exec_date = None
                        
            if action["side"] == "BUY":
                position += action["qty"]
                if exec_date:
                    open_dates.append(exec_date)
                buy_legs.append({"qty": action["qty"], "price": action["price"], "date": exec_date})
                
                # Check if we have an existing open position to close (LIFO)
                if symbol in open_positions:
                    existing_pos = open_positions[symbol]
                    # Close the existing position
                    existing_pos.close_position(action["price"], exec_date)
                    closed_positions.append(existing_pos)
                    del open_positions[symbol]
                    
                    # Create closed trade record
                    trade_obj = Trade(
                        date=existing_pos.buy_date,
                        ticker_symbol=symbol,
                        number_of_shares=existing_pos.total_shares,
                        buy_price=existing_pos.buy_price,
                        sell_price=action["price"],
                        trading_type="Swing" if existing_pos.buy_date != exec_date else "Day",
                        user_id=user.id,
                        status='CLOSED',
                        position_id=existing_pos.id
                    )
                    db.session.add(trade_obj)
                    new_trades.append(trade_obj)
                    closed_trades_count += 1
                    if existing_pos.buy_date == exec_date:
                        day_trades += 1
                    else:
                        swing_trades += 1
                
                # Create new open position for remaining shares
                if position > 0:
                    new_position = Position(
                        user_id=user.id,
                        symbol=symbol,
                        total_shares=int(position),
                        buy_price=action["price"],
                        buy_date=exec_date or datetime.now().date()
                    )
                    db.session.add(new_position)
                    new_positions.append(new_position)
                    open_positions[symbol] = new_position
                    
            elif action["side"] == "SELL":
                position -= action["qty"]
                if exec_date:
                    close_dates.append(exec_date)
                sell_legs.append({"qty": action["qty"], "price": action["price"], "date": exec_date})
                
                # Check if we have an existing open position to close
                if symbol in open_positions:
                    existing_pos = open_positions[symbol]
                    # Close the existing position
                    existing_pos.close_position(action["price"], exec_date)
                    closed_positions.append(existing_pos)
                    del open_positions[symbol]
                    
                    # Create closed trade record
                    trade_obj = Trade(
                        date=existing_pos.buy_date,
                        ticker_symbol=symbol,
                        number_of_shares=existing_pos.total_shares,
                        buy_price=existing_pos.buy_price,
                        sell_price=action["price"],
                        trading_type="Swing" if existing_pos.buy_date != exec_date else "Day",
                        user_id=user.id,
                        status='CLOSED',
                        position_id=existing_pos.id
                    )
                    db.session.add(trade_obj)
                    new_trades.append(trade_obj)
                    closed_trades_count += 1
                    if existing_pos.buy_date == exec_date:
                        day_trades += 1
                    else:
                        swing_trades += 1
                        
        # After processing all actions for this symbol, check if we have remaining open positions
        # that should be created as open trades
        if symbol in open_positions:
            open_pos = open_positions[symbol]
            # Create open trade record
            trade_obj = Trade(
                date=open_pos.buy_date,
                ticker_symbol=symbol,
                number_of_shares=open_pos.total_shares,
                buy_price=open_pos.buy_price,
                sell_price=None,  # No sell price for open position
                trading_type="Swing",  # Default to Swing for open positions
                user_id=user.id,
                status='OPEN',
                position_id=open_pos.id
            )
            db.session.add(trade_obj)
            new_trades.append(trade_obj)
    
    # Commit all changes
    if new_trades or new_positions or closed_positions:
        db.session.commit()

    total_pnl = float(sum(pnl_by_symbol.values()))

    return jsonify({
        "num_trades": len(trades),
        "closed_trades_count": closed_trades_count,
        "day_trades": day_trades,
        "swing_trades": swing_trades,
        "symbols": list(pnl_by_symbol.keys()),
        "pnl_by_symbol": pnl_by_symbol,
        "total_pnl": total_pnl,
        "sample_trades": trades[:5],
        "new_positions": len(new_positions),
        "closed_positions": len(closed_positions),
        "open_positions_count": len(open_positions)
    }) 