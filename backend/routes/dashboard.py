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
        
        # Calculate profit/loss from positions instead of individual trades
        positions = Position.query.filter(Position.user_id == user.id).all()
        total_profit_loss = sum(float(pos.pnl) for pos in positions if pos.pnl is not None)
        avg_profit_loss = total_profit_loss / len(positions) if len(positions) > 0 else 0
        
        # Get recent closed positions (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_positions = [pos for pos in positions if pos.sell_date and pos.sell_date >= thirty_days_ago]
        recent_profit_loss = sum(float(pos.pnl) for pos in recent_positions if pos.pnl is not None)
        
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
        
        # Get stats for Swing positions
        swing_positions = Position.query.filter(Position.user_id == user.id).all()
        closed_swing_positions = [pos for pos in swing_positions if pos.status == 'CLOSED']
        swing_stats = {
            'total_trades': len(swing_positions),
            'win_count': len([pos for pos in closed_swing_positions if pos.pnl and pos.pnl > 0]),
            'loss_count': len([pos for pos in closed_swing_positions if pos.pnl and pos.pnl < 0]),
            'total_profit_loss': sum(float(pos.pnl) for pos in closed_swing_positions if pos.pnl is not None),
            'win_rate': 0
        }
        if len(closed_swing_positions) > 0:
            swing_stats['win_rate'] = round((swing_stats['win_count'] / len(closed_swing_positions)) * 100, 2)
        
        # Get stats for Day positions (same as swing for now since we don't separate by trading type in positions)
        day_positions = Position.query.filter(Position.user_id == user.id).all()
        closed_day_positions = [pos for pos in day_positions if pos.status == 'CLOSED']
        day_stats = {
            'total_trades': len(day_positions),
            'win_count': len([pos for pos in closed_day_positions if pos.pnl and pos.pnl > 0]),
            'loss_count': len([pos for pos in closed_day_positions if pos.pnl and pos.pnl < 0]),
            'total_profit_loss': sum(float(pos.pnl) for pos in closed_day_positions if pos.pnl is not None),
            'win_rate': 0
        }
        if len(closed_day_positions) > 0:
            day_stats['win_rate'] = round((day_stats['win_count'] / len(closed_day_positions)) * 100, 2)
        
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

    # Process each symbol for position tracking with consolidation
    print(f"Starting position tracking for {len(symbol_trades)} symbols...")
    
    # Get existing open positions for this user
    existing_positions = Position.query.filter_by(user_id=user.id, status='OPEN').all()
    open_positions = {pos.symbol: pos for pos in existing_positions}
    
    trades_added = 0
    
    for symbol, actions in symbol_trades.items():
        print(f"Processing symbol {symbol} with {len(actions)} actions")
        
        # Separate BUY and SELL actions
        buy_actions = []
        sell_actions = []
        
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
                
                # Store action with date
                action_data = {
                    'side': side,
                    'qty': qty,
                    'price': price,
                    'date': exec_date,
                    'trade_row': trade_row
                }
                
                if side == 'BUY':
                    buy_actions.append(action_data)
                elif side == 'SELL':
                    sell_actions.append(action_data)
                    
            except Exception as e:
                print(f"  Error processing trade {action}: {e}")
                continue
        
        # Consolidate ALL BUY actions for this symbol (across all dates)
        total_buy_shares = 0
        total_buy_cost = 0.0
        earliest_buy_date = None
        
        for buy_action in buy_actions:
            total_buy_shares += buy_action['qty']
            total_buy_cost += buy_action['qty'] * buy_action['price']
            if earliest_buy_date is None or buy_action['date'] < earliest_buy_date:
                earliest_buy_date = buy_action['date']
        
        # Consolidate ALL SELL actions for this symbol (across all dates)
        total_sell_shares = 0
        total_sell_cost = 0.0
        latest_sell_date = None
        
        for sell_action in sell_actions:
            total_sell_shares += sell_action['qty']
            total_sell_cost += sell_action['qty'] * sell_action['price']
            if latest_sell_date is None or sell_action['date'] > latest_sell_date:
                latest_sell_date = sell_action['date']
        
        # Calculate weighted averages
        buy_avg_price = total_buy_cost / total_buy_shares if total_buy_shares > 0 else 0
        sell_avg_price = total_sell_cost / total_sell_shares if total_sell_shares > 0 else 0
        
        print(f"  Symbol {symbol} Summary:")
        print(f"    Total BUY: {total_buy_shares} shares @ ${buy_avg_price:.2f} avg")
        print(f"    Total SELL: {total_sell_shares} shares @ ${sell_avg_price:.2f} avg")
        
        # Handle symbols with no BUY trades (SELL-only positions)
        if total_buy_shares == 0:
            print(f"    Processing {symbol} - SELL-only position")
            
            # For SELL-only positions, use sell date as buy date and sell price as buy price
            # This represents a "short sale" or "sold without owning" scenario
            buy_date = latest_sell_date  # Use the sell date as buy date
            buy_price = sell_avg_price   # Use sell price as buy price
            remaining_shares = total_sell_shares  # Show the actual shares that were sold
            status = 'CLOSED'           # Always closed for SELL-only
            
            # Calculate P&L for SELL-only positions (sell_price - buy_price = 0 since they're the same)
            pnl = 0.0  # For SELL-only positions, P&L is 0 since buy_price = sell_price
            
            print(f"    SELL-only position: {total_sell_shares} shares @ ${buy_price:.2f} (sold on {buy_date})")
            print(f"    P&L: ${pnl:.2f} (SELL-only position)")
            
            # Create or update position
            position = Position.query.filter_by(user_id=user.id, symbol=symbol).first()
            if position:
                position.total_shares = remaining_shares
                position.buy_price = buy_price
                position.buy_date = buy_date
                position.sell_price = sell_avg_price
                position.sell_date = latest_sell_date
                position.status = status
                position.pnl = pnl
                position.updated_at = datetime.utcnow()
                print(f"    Updated existing {symbol} position")
            else:
                position = Position(
                    user_id=user.id,
                    symbol=symbol,
                    total_shares=remaining_shares,
                    buy_price=buy_price,
                    buy_date=buy_date,
                    sell_price=sell_avg_price,
                    sell_date=latest_sell_date,
                    status=status,
                    pnl=pnl
                )
                db.session.add(position)
                print(f"    Created new {symbol} position")
            
            # Create individual SELL trade records
            for sell_action in sell_actions:
                trade = Trade(
                    date=sell_action['date'],
                    ticker_symbol=symbol,
                    number_of_shares=int(sell_action['qty']),
                    buy_price=0,  # No actual buy price for SELL-only trades
                    sell_price=sell_action['price'],
                    trading_type='Swing',
                    user_id=user.id,
                    status='CLOSED',
                    position_id=position.id,  # Link to the position
                    shares_remaining=0,
                    transaction_type='stock'
                )
                db.session.add(trade)
                trades_added += 1
                print(f"    Added SELL trade: {symbol} {sell_action['qty']} @ {sell_action['price']}")
            
            continue
        
        # Determine position status and remaining shares
        net_shares = total_buy_shares - total_sell_shares
        
        if net_shares > 0:
            # Position is still OPEN
            status = 'OPEN'
            remaining_shares = net_shares
            # For open positions, calculate realized P&L from shares that were sold
            pnl = (sell_avg_price - buy_avg_price) * total_sell_shares if total_sell_shares > 0 else 0.0
            print(f"    Result: {remaining_shares} shares OPEN @ ${buy_avg_price:.2f}")
            print(f"    Realized P&L: ${pnl:.2f} (from {total_sell_shares} shares sold)")
        else:
            # Position is CLOSED
            status = 'CLOSED'
            remaining_shares = 0
            # For closed positions, P&L = (sell_price - buy_price) * shares_sold
            pnl = (sell_avg_price - buy_avg_price) * total_sell_shares if total_sell_shares > 0 else 0.0
            print(f"    Result: Position CLOSED (sold {total_sell_shares} of {total_buy_shares} shares)")
            print(f"    P&L: ${pnl:.2f} (realized)")
        
        # Create or update position
        position = Position.query.filter_by(
            user_id=user.id,
            symbol=symbol,
            status='OPEN'
        ).first()
        
        if position:
            # Update existing position
            position.total_shares = remaining_shares
            position.buy_price = buy_avg_price
            position.buy_date = earliest_buy_date
            position.status = status
            position.pnl = pnl
            if status == 'CLOSED':
                position.sell_price = sell_avg_price
                position.sell_date = latest_sell_date
            position.updated_at = datetime.utcnow()
            print(f"  Updated {symbol} position: {remaining_shares} shares @ ${buy_avg_price:.2f} ({status})")
        else:
            # Create new position
            position = Position(
                user_id=user.id,
                symbol=symbol,
                total_shares=remaining_shares,
                buy_price=buy_avg_price,
                buy_date=earliest_buy_date,
                status=status,
                pnl=pnl
            )
            if status == 'CLOSED':
                position.sell_price = sell_avg_price
                position.sell_date = latest_sell_date
            db.session.add(position)
            print(f"  Created new {symbol} position: {remaining_shares} shares @ ${buy_avg_price:.2f} ({status})")
        
        # Create individual trade records for audit trail
        for buy_action in buy_actions:
            trade = Trade(
                date=buy_action['date'],
                ticker_symbol=symbol,
                number_of_shares=int(buy_action['qty']),
                buy_price=buy_action['price'],
                sell_price=None,
                trading_type='Swing',
                user_id=user.id,
                status='OPEN' if status == 'OPEN' else 'CLOSED',
                position_id=position.id,
                shares_remaining=int(buy_action['qty']) if status == 'OPEN' else 0,
                transaction_type='stock'
            )
            db.session.add(trade)
            trades_added += 1
            print(f"    Added BUY trade: {symbol} {buy_action['qty']} @ {buy_action['price']}")
        
        for sell_action in sell_actions:
            trade = Trade(
                date=sell_action['date'],
                ticker_symbol=symbol,
                number_of_shares=int(sell_action['qty']),
                buy_price=buy_avg_price,  # Use position's weighted average buy price
                sell_price=sell_action['price'],
                trading_type='Swing',
                user_id=user.id,
                status='CLOSED',
                position_id=position.id,
                shares_remaining=0,
                transaction_type='stock'
            )
            db.session.add(trade)
            trades_added += 1
            print(f"    Added SELL trade: {symbol} {sell_action['qty']} @ {sell_action['price']}")
    
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