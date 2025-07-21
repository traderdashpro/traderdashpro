from flask import Blueprint, request, jsonify
from database import db
from models.journal import JournalEntry
from models.trade import Trade
from datetime import datetime
import os
import openai

journal_bp = Blueprint('journal', __name__)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

@journal_bp.route('/', methods=['GET'])
def get_journal_entries():
    """Get all journal entries with optional filtering"""
    try:
        # Get query parameters for filtering
        trade_id = request.args.get('trade_id')
        entry_type = request.args.get('entry_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = JournalEntry.query
        
        if trade_id:
            query = query.filter(JournalEntry.trade_id == trade_id)
        if entry_type:
            query = query.filter(JournalEntry.entry_type == entry_type)
        if date_from:
            query = query.filter(JournalEntry.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(JournalEntry.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        # Order by date descending
        entries = query.order_by(JournalEntry.date.desc()).all()
        
        return jsonify({
            'success': True,
            'entries': [entry.to_dict() for entry in entries]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'notes']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse date
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Validate trade_id if provided
        trade_id = data.get('trade_id')
        if trade_id:
            trade = Trade.query.get(trade_id)
            if not trade:
                return jsonify({
                    'success': False,
                    'error': 'Referenced trade not found'
                }), 400
        
        # Determine entry type
        entry_type = 'trade_specific' if trade_id else 'general'
        
        # Create journal entry
        entry = JournalEntry(
            date=entry_date,
            notes=data['notes'],
            trade_id=trade_id,
            entry_type=entry_type
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'entry': entry.to_dict(),
            'message': 'Journal entry created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/<entry_id>', methods=['GET'])
def get_journal_entry(entry_id):
    """Get a specific journal entry by ID"""
    try:
        entry = JournalEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Journal entry not found'
            }), 404
        
        return jsonify({
            'success': True,
            'entry': entry.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/<entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    """Update a journal entry"""
    try:
        entry = JournalEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Journal entry not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'date' in data:
            entry.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'notes' in data:
            entry.notes = data['notes']
        if 'trade_id' in data:
            if data['trade_id']:
                trade = Trade.query.get(data['trade_id'])
                if not trade:
                    return jsonify({
                        'success': False,
                        'error': 'Referenced trade not found'
                    }), 400
            entry.trade_id = data['trade_id']
            entry.entry_type = 'trade_specific' if data['trade_id'] else 'general'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'entry': entry.to_dict(),
            'message': 'Journal entry updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/<entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    """Delete a journal entry"""
    try:
        entry = JournalEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'success': False,
                'error': 'Journal entry not found'
            }), 404
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Journal entry deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/insights', methods=['GET'])
def get_ai_insights():
    """Get AI insights from journal entries"""
    try:
        # Get all journal entries
        entries = JournalEntry.query.order_by(JournalEntry.date.desc()).all()
        
        if not entries:
            return jsonify({
                'success': True,
                'insights': 'No journal entries found to analyze.'
            }), 200
        
        # Prepare data for AI analysis
        journal_text = ""
        for entry in entries:
            trade_info = ""
            if entry.trade_id and entry.trade:
                trade = entry.trade
                trade_info = f" (Trade: {trade.ticker_symbol}, {trade.trading_type}, {trade.win_loss})"
            
            journal_text += f"Date: {entry.date}, Type: {entry.entry_type}{trade_info}\nNotes: {entry.notes}\n\n"
        
        # Generate AI insights
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a trading analyst. Analyze the provided trading journal entries and provide insights about trading patterns, common mistakes, successful strategies, and recommendations for improvement. Be concise but comprehensive."
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze these trading journal entries and provide insights:\n\n{journal_text}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content
            
        except Exception as ai_error:
            insights = f"Unable to generate AI insights at this time. Error: {str(ai_error)}"
        
        return jsonify({
            'success': True,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 