from flask import Blueprint, request, jsonify
from database import db
from models.trade import Trade
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
from io import StringIO
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get query parameters
        trading_type = request.args.get('trading_type')  # 'Swing', 'Day', or None for all
        
        # Build base query
        query = Trade.query
        
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
        
        # Calculate statistics
        total_trades = len(trades)
        win_count = len([t for t in trades if t.win_loss == 'Win'])
        loss_count = len([t for t in trades if t.win_loss == 'Loss'])
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate profit/loss
        total_profit_loss = sum(t.calculate_profit_loss() for t in trades)
        avg_profit_loss = total_profit_loss / total_trades if total_trades > 0 else 0
        
        # Get recent trades (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_trades = [t for t in trades if t.date >= thirty_days_ago]
        recent_profit_loss = sum(t.calculate_profit_loss() for t in recent_trades)
        
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
                'recent_trades_count': len(recent_trades)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/chart', methods=['GET'])
def get_chart_data():
    """Get chart data for dashboard"""
    try:
        # Get query parameters
        trading_type = request.args.get('trading_type')  # 'Swing', 'Day', or None for all
        
        # Build base query
        query = Trade.query
        
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
        
        # Get win/loss distribution for donut chart
        win_count = len([t for t in trades if t.win_loss == 'Win'])
        loss_count = len([t for t in trades if t.win_loss == 'Loss'])
        
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
        
        # Get daily profit/loss data for line chart
        daily_data = {}
        for trade in trades:
            day = trade.date.strftime('%Y-%m-%d')
            if day not in daily_data:
                daily_data[day] = 0
            daily_data[day] += trade.calculate_profit_loss()
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
def get_trading_type_stats():
    """Get statistics by trading type"""
    try:
        # Get stats for Swing trades
        swing_trades = Trade.query.filter(Trade.trading_type == 'Swing').all()
        swing_stats = {
            'total_trades': len(swing_trades),
            'win_count': len([t for t in swing_trades if t.win_loss == 'Win']),
            'loss_count': len([t for t in swing_trades if t.win_loss == 'Loss']),
            'total_profit_loss': sum(t.calculate_profit_loss() for t in swing_trades),
            'win_rate': 0
        }
        if swing_stats['total_trades'] > 0:
            swing_stats['win_rate'] = round((swing_stats['win_count'] / swing_stats['total_trades']) * 100, 2)
        
        # Get stats for Day trades
        day_trades = Trade.query.filter(Trade.trading_type == 'Day').all()
        day_stats = {
            'total_trades': len(day_trades),
            'win_count': len([t for t in day_trades if t.win_loss == 'Win']),
            'loss_count': len([t for t in day_trades if t.win_loss == 'Loss']),
            'total_profit_loss': sum(t.calculate_profit_loss() for t in day_trades),
            'win_rate': 0
        }
        if day_stats['total_trades'] > 0:
            day_stats['win_rate'] = round((day_stats['win_count'] / day_stats['total_trades']) * 100, 2)
        
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
def upload_statement():
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

    # Calculate P&L (simple: sum sell - sum buy for each symbol)
    pnl_by_symbol: dict[str, float] = {}
    # For closed trade counting
    symbol_trades = defaultdict(list)
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
            # For closed trade counting
            symbol_trades[symbol].append({"side": side, "qty": qty})

    # Count closed trades and classify as day or swing
    closed_trades_count = 0
    day_trades = 0
    swing_trades = 0
    new_trades = []
    for symbol, actions in symbol_trades.items():
        position = 0
        open_dates = []
        close_dates = []
        buy_legs = []
        sell_legs = []
        for idx, action in enumerate(actions):
            # Parse date from trade row (Exec Time column)
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
                buy_legs.append({"qty": action["qty"], "price": float(trade_row.get("Price", "0").replace(",", "")), "date": exec_date})
            elif action["side"] == "SELL":
                position -= action["qty"]
                if exec_date:
                    close_dates.append(exec_date)
                sell_legs.append({"qty": action["qty"], "price": float(trade_row.get("Price", "0").replace(",", "")), "date": exec_date})
            # If position returns to zero, count as a closed trade
            if position == 0 and (open_dates or close_dates):
                closed_trades_count += 1
                open_date = open_dates[0] if open_dates else None
                close_date = close_dates[-1] if close_dates else None
                trading_type = "Day" if open_date and close_date and open_date == close_date else "Swing"
                if trading_type == "Day":
                    day_trades += 1
                else:
                    swing_trades += 1
                # Aggregate buy/sell legs for this closed trade
                total_buy_qty = sum(leg["qty"] for leg in buy_legs)
                total_sell_qty = sum(leg["qty"] for leg in sell_legs)
                # Use the smaller of total buy/sell qty for number_of_shares
                num_shares = int(min(total_buy_qty, total_sell_qty))
                # Weighted average buy price
                buy_price = sum(leg["qty"] * leg["price"] for leg in buy_legs) / total_buy_qty if total_buy_qty else 0
                # Weighted average sell price
                sell_price = sum(leg["qty"] * leg["price"] for leg in sell_legs) / total_sell_qty if total_sell_qty else 0
                # Use earliest buy date as trade date
                trade_date = min([leg["date"] for leg in buy_legs if leg["date"]] or [open_date])
                # Create and save Trade
                trade_obj = Trade(
                    date=trade_date,
                    ticker_symbol=symbol,
                    number_of_shares=num_shares,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    trading_type=trading_type
                )
                db.session.add(trade_obj)
                new_trades.append(trade_obj)
                # Reset for next closed trade
                open_dates = []
                close_dates = []
                buy_legs = []
                sell_legs = []
    if new_trades:
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
    }) 