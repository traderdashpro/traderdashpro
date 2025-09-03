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

def parse_thinkorswim_statement(file):
    """Parse Thinkorswim statement CSV file"""
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
        return []

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
    
    return trades

def parse_robinhood_statement(file):
    """Parse Robinhood statement CSV file"""
    try:
        print("Starting Robinhood CSV parsing...")
        content = file.read()
        print(f"Read {len(content)} bytes from file")
        text = content.decode("utf-8")
        print(f"Decoded text length: {len(text)}")
        f = StringIO(text)
        reader = csv.reader(f)
        lines = list(reader)
        print(f"CSV has {len(lines)} total lines")
    except Exception as e:
        print(f"Error reading Robinhood CSV file: {e}")
        return []
    
    trades = []
    if len(lines) < 2:
        print(f"Robinhood CSV has only {len(lines)} lines, need at least 2")
        return trades
    
    # Robinhood CSV has headers in first row
    headers = lines[0]
    print(f"Robinhood CSV headers: {headers}")
    
    # Print first few rows for debugging
    for i, row in enumerate(lines[1:4]):
        print(f"Row {i+1}: {row}")
    
    for row in lines[1:]:
        if len(row) < len(headers):
            print(f"Skipping short row: {row}")
            continue
        
        trade = dict(zip(headers, row))
        
        # Extract basic trade info using actual Robinhood column names
        symbol = trade.get('Instrument', '').strip()
        trans_code = trade.get('Trans Code', '').strip()
        qty = trade.get('Quantity', '').strip()
        price = trade.get('Price', '').strip()
        amount = trade.get('Amount', '').strip()
        
        print(f"Row data: {row}")
        print(f"Extracted: symbol='{symbol}', trans_code='{trans_code}', qty='{qty}', price='{price}', amount='{amount}'")
        
        # Skip non-trade rows (dividends, fees, deposits, etc.)
        if not symbol or not trans_code or not qty or not price:
            print(f"Skipping non-trade row: symbol='{symbol}', trans_code='{trans_code}', qty='{qty}', price='{price}'")
            continue
            
        # Skip options trades for now (BTO, STO, STC)
        if trans_code in ['BTO', 'STO', 'STC']:
            print(f"Skipping options trade: {trans_code}")
            continue
            
        # Only process Buy/Sell stock trades
        print(f"Checking if '{trans_code}' is in ['Buy', 'Sell']: {trans_code in ['Buy', 'Sell']}")
        if trans_code in ['Buy', 'Sell']:
            try:
                # Convert to proper types
                qty_float = abs(float(qty.replace(',', '')))
                price_float = float(price.replace('$', '').replace(',', ''))
                
                # Map Robinhood format to our internal format (matching what main logic expects)
                trade['Symbol'] = symbol
                trade['Side'] = trans_code.upper()
                trade['Qty'] = qty_float  # Changed from 'Quantity' to 'Qty'
                trade['Price'] = price_float
                trade['Transaction Type'] = 'stock'
                
                # Parse date
                activity_date = trade.get('Activity Date', '')
                if activity_date:
                    try:
                        # Parse MM/DD/YYYY format
                        parsed_date = datetime.strptime(activity_date, '%m/%d/%Y')
                        trade['Date'] = parsed_date.strftime('%m/%d/%y')
                    except ValueError:
                        trade['Date'] = activity_date
                
                trades.append(trade)
                print(f"Added stock trade: {symbol} {trans_code} {qty_float} @ ${price_float}")
            except (ValueError, AttributeError) as e:
                print(f"Error processing row: {e}")
                continue
    
    print(f"Total stock trades parsed: {len(trades)}")
    return trades

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
    
    # Parse based on platform
    if platform.lower() == "thinkorswim":
        print("Parsing Thinkorswim statement...")
        trades = parse_thinkorswim_statement(file)
    elif platform.lower() == "robinhood":
        print("Parsing Robinhood statement...")
        trades = parse_robinhood_statement(file)
    else:
        return jsonify({'error': 'Unsupported platform. Please select Thinkorswim or Robinhood.'}), 400
    
    print(f"Parsed {len(trades)} trades from {platform} statement")
    
    if not trades:
        return jsonify({'error': 'No trades found in the statement.'}), 400

    # Calculate P&L and track positions
    pnl_by_symbol: dict[str, float] = {}
    symbol_trades = defaultdict(list)
    new_trades = []
    new_positions = []
    closed_positions = []
    
    # Get existing open positions for this user
    existing_positions = Position.query.filter_by(user_id=user.id, status='OPEN').all()
    open_positions = {pos.symbol: pos for pos in existing_positions}
    
    print(f"Processing {len(trades)} trades in main upload logic...")
    for i, trade in enumerate(trades):
        print(f"Trade {i}: {trade}")
        symbol = trade.get("Symbol", "").strip()
        side = trade.get("Side", "").strip().upper()
        qty = trade.get("Qty", "0")
        price = trade.get("Price", "0")
        
        print(f"  Extracted: symbol='{symbol}', side='{side}', qty='{qty}', price='{price}'")
        
        try:
            # Handle both string and float values
            if isinstance(qty, (int, float)):
                qty_float = abs(float(qty))
            else:
                qty_str = str(qty).replace(",", "") if qty else "0"
                qty_float = abs(float(qty_str))
                
            if isinstance(price, (int, float)):
                price_float = float(price)
            else:
                price_str = str(price).replace(",", "") if price else "0"
                price_float = float(price_str)
                
            print(f"  Converted: qty={qty_float}, price={price_float}")
        except Exception as e:
            print(f"  Error converting values: {e}")
            qty_float = 0.0
            price_float = 0.0
            
        if symbol:
            if symbol not in pnl_by_symbol:
                pnl_by_symbol[symbol] = 0.0
            if side == "BUY":
                pnl_by_symbol[symbol] -= qty_float * price_float
            elif side == "SELL":
                pnl_by_symbol[symbol] += qty_float * price_float
            symbol_trades[symbol].append({"side": side, "qty": qty_float, "price": price_float})
            print(f"  Added to symbol_trades: {symbol} {side} {qty_float} @ {price_float}")
        else:
            print(f"  Skipping trade with no symbol")
    
    print(f"Final symbol_trades: {dict(symbol_trades)}")
    print(f"Final pnl_by_symbol: {pnl_by_symbol}")

    # Process each symbol for position tracking
    print(f"Starting position tracking for {len(symbol_trades)} symbols...")
    
    # Get existing open positions for this user
    existing_positions = Position.query.filter_by(user_id=user.id, status='OPEN').all()
    open_positions = {pos.symbol: pos for pos in existing_positions}
    
    trades_added = 0
    
    for symbol, actions in symbol_trades.items():
        print(f"Processing symbol {symbol} with {len(actions)} actions")
        
        for idx, action in enumerate(actions):
            try:
                # Get the original trade row for additional data
                trade_row = trades[[i for i, t in enumerate(trades) if t.get('Symbol', '').strip() == symbol][idx]]
                
                # Extract trade details
                side = action['side']
                qty = action['qty']
                price = action['price']
                exec_date = None
                
                # Parse date
                exec_time_str = trade_row.get('Exec Time') or trade_row.get('ExecTime') or trade_row.get('Date')
                if exec_time_str:
                    try:
                        exec_date = datetime.strptime(exec_time_str.split()[0], '%m/%d/%y').date()
                    except Exception:
                        try:
                            exec_date = datetime.strptime(exec_time_str, '%m/%d/%y').date()
                        except Exception:
                            exec_date = None
                
                if exec_date is None:
                    print(f"  Skipping trade due to date parsing failure: {action}")
                    continue
                
                # Determine if this is a buy or sell
                if side == 'BUY':
                    # Create a new position or add to existing
                    position = Position.query.filter_by(
                        user_id=user.id,
                        symbol=symbol,
                        status='OPEN'
                    ).first()
                    
                    if position:
                        # Add to existing position
                        position.total_shares += qty
                        position.updated_at = datetime.utcnow()
                        print(f"  Added {qty} shares to existing {symbol} position")
                    else:
                        # Create new position
                        position = Position(
                            user_id=user.id,
                            symbol=symbol,
                            total_shares=qty,
                            buy_price=price,
                            buy_date=exec_date,
                            status='OPEN'
                        )
                        db.session.add(position)
                        print(f"  Created new {symbol} position with {qty} shares")
                    
                    # Create trade record
                    trade = Trade(
                        date=exec_date,
                        ticker_symbol=symbol,
                        number_of_shares=int(qty),
                        buy_price=price,
                        sell_price=None,  # No sell price for BUY
                        trading_type='Swing',  # Default to Swing for now
                        user_id=user.id,
                        status='OPEN',
                        position_id=position.id if position else None,
                        shares_remaining=int(qty),
                        transaction_type='stock'
                    )
                    db.session.add(trade)
                    trades_added += 1
                    print(f"  Added BUY trade: {symbol} {qty} @ {price}")
                    
                elif side == 'SELL':
                    # Find existing OPEN position to close
                    position = Position.query.filter_by(
                        user_id=user.id,
                        symbol=symbol,
                        status='OPEN'
                    ).first()
                    
                    if position and position.total_shares >= qty:
                        # Close position (LIFO - Last In, First Out)
                        position.close_position(price, exec_date)
                        print(f"  Closed {symbol} position: {qty} shares @ {price}")
                        
                        # Create trade record
                        trade = Trade(
                            date=exec_date,
                            ticker_symbol=symbol,
                            number_of_shares=int(qty),
                            buy_price=position.buy_price,  # Use position's buy price
                            sell_price=price,  # Current sell price
                            trading_type='Swing',  # Default to Swing for now
                            user_id=user.id,
                            status='CLOSED',
                            position_id=position.id,
                            shares_remaining=0,
                            transaction_type='stock'
                        )
                        db.session.add(trade)
                        trades_added += 1
                        print(f"  Added SELL trade: {symbol} {qty} @ {price}")
                    else:
                        print(f"  Skipping SELL trade - no matching OPEN position: {symbol} {qty}")
                
            except Exception as e:
                print(f"  Error processing trade {action}: {e}")
                continue
    
    # Commit all changes
    try:
        db.session.commit()
        print(f"Successfully added {trades_added} trades to database")
    except Exception as e:
        db.session.rollback()
        print(f"Error committing trades: {e}")
        return jsonify({'error': 'Failed to save trades to database'}), 500
    


    total_pnl = float(sum(pnl_by_symbol.values()))

    return jsonify({
        "num_trades": len(trades),
        "trades_added": trades_added,
        "symbols": list(pnl_by_symbol.keys()),
        "pnl_by_symbol": pnl_by_symbol,
        "total_pnl": total_pnl,
        "sample_trades": trades[:5]
    }) 