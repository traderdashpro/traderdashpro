from flask import Blueprint, request, jsonify
from database import db
from models.journal import JournalEntry
from models.trade import Trade
from models.ai_insights import AIInsights
from utils.decorators import require_auth
from datetime import datetime
import os
from openai import OpenAI
import json



journal_bp = Blueprint('journal', __name__)


@journal_bp.route('/', methods=['GET'])
@require_auth
def get_journal_entries():
    """Get all journal entries for the authenticated user with optional filtering and pagination"""
    try:
        user = request.current_user
        
        # Get query parameters for filtering and pagination
        trade_id = request.args.get('trade_id')
        entry_type = request.args.get('entry_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Build query - only get entries belonging to the current user
        query = JournalEntry.query.filter(JournalEntry.user_id == user.id)
        
        if trade_id:
            # Ensure the trade belongs to the current user
            trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
            if not trade:
                return jsonify({
                    'success': False,
                    'error': 'Trade not found'
                }), 404
            query = query.filter(JournalEntry.trade_id == trade_id)
        if entry_type:
            query = query.filter(JournalEntry.entry_type == entry_type)
        if date_from:
            query = query.filter(JournalEntry.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            query = query.filter(JournalEntry.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        if search:
            # Search in notes field
            query = query.filter(JournalEntry.notes.ilike(f'%{search}%'))
        
        # Get total count for pagination
        total_count = query.count()
        
        # Calculate pagination
        offset = (page - 1) * per_page
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get paginated entries ordered by date descending
        entries = query.order_by(JournalEntry.date.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()
        
        return jsonify({
            'success': True,
            'entries': [entry.to_dict() for entry in entries],
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@journal_bp.route('/', methods=['POST'])
@require_auth
def create_journal_entry():
    """Create a new journal entry for the authenticated user"""
    try:
        user = request.current_user
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
            # Ensure the trade belongs to the current user
            trade = Trade.query.filter_by(id=trade_id, user_id=user.id).first()
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
            user_id=str(user.id),
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
@require_auth
def get_journal_entry(entry_id):
    """Get a specific journal entry by ID"""
    try:
        user = request.current_user
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
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
@require_auth
def update_journal_entry(entry_id):
    """Update a journal entry"""
    try:
        user = request.current_user
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
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
@require_auth
def delete_journal_entry(entry_id):
    """Delete a journal entry"""
    try:
        user = request.current_user
        entry = JournalEntry.query.filter_by(id=entry_id, user_id=user.id).first()
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
@require_auth
def get_ai_insights():
    """Get AI insights from journal entries"""
    try:
        user = request.current_user
        
        # Check if user can get AI insights based on their plan
        if not user.can_get_ai_insights():
            next_available = user.get_next_ai_insights_date()
            return jsonify({
                'success': False,
                'error': 'AI insights limit reached for free plan',
                'plan': user.plan,
                'last_insights_date': user.last_ai_insights_date.isoformat() if user.last_ai_insights_date else None,
                'next_available_date': next_available.isoformat() if next_available else None,
                'can_get_insights': False
            }), 429
        
        # Get all journal entries for the current user
        entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.date.desc()).all()
        
        if not entries:
            return jsonify({
                'success': True,
                'insights': 'No journal entries found to analyze.',
                'plan': user.plan,
                'can_get_insights': True
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
        openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        try:
            prompt = f"""
            Analyze the following trading journal entries and provide insights in JSON format.
            
            Journal Entries:
            {journal_text}
            
            Please provide analysis in the following JSON structure:
            {{
                "key_patterns": ["pattern1", "pattern2", "pattern3"],
                "strengths": ["strength1", "strength2"],
                "areas_for_improvement": ["area1", "area2"],
                "emotional_state_analysis": "brief analysis of emotional patterns",
                "trading_performance_insights": "insights about trading performance",
                "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
                "learning_resources": {{
                    "videos": [
                        {{
                            "title": "Specific video title based on analysis",
                            "description": "Why this video is recommended",
                            "search_query": "specific search terms to find this video",
                            "category": "patterns|strengths|improvements|emotions|performance"
                        }}
                    ],
                    "books": [
                        {{
                            "title": "Specific book title based on analysis",
                            "description": "Why this book is recommended",
                            "search_query": "specific search terms to find this book",
                            "category": "patterns|strengths|improvements|emotions|performance"
                        }}
                    ]
                }}
            }}
            
            Focus on:
            - Recurring patterns in trading behavior
            - Emotional states and their impact on trading
            - Performance trends
            - Risk management practices
            - Areas for improvement
            - Actionable recommendations
            
            For learning resources:
            - Recommend 2-3 specific YouTube videos that would help with identified issues
            - Recommend 2-3 specific books that address the user's needs
            - Make recommendations highly specific to the user's trading patterns
            - Focus on practical, actionable learning content
            - Ensure video titles and book titles are real and searchable
            """
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trading coach and analyst. Analyze trading journal entries to provide actionable insights and recommendations. Additionally, provide specific, relevant learning resources including YouTube videos and books that directly address the user's identified needs and trading patterns. Focus on practical, searchable content that users can actually find and benefit from."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            
            # Store the insights in the database
            insights_record = AIInsights(
                user_id=user.id,
                insights_data=json.dumps(insights)
            )
            db.session.add(insights_record)
            
            # Update user's last AI insights date
            user.last_ai_insights_date = datetime.utcnow()
            db.session.commit()
            
        except Exception as ai_error:
            insights = f"Unable to generate AI insights at this time. Error: {str(ai_error)}"
        
        return jsonify({
            'success': True,
            'insights': insights,
            'plan': user.plan,
            'can_get_insights': user.can_get_ai_insights(),
            'last_insights_date': user.last_ai_insights_date.isoformat() if user.last_ai_insights_date else None,
            'next_available_date': user.get_next_ai_insights_date().isoformat() if user.get_next_ai_insights_date() else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@journal_bp.route('/stored-insights', methods=['GET'])
@require_auth
def get_stored_insights():
    """Get the most recent stored AI insights for the user"""
    try:
        user = request.current_user
        
        # Get the most recent AI insights for this user
        latest_insights = AIInsights.query.filter_by(user_id=user.id).order_by(AIInsights.created_at.desc()).first()
        
        if not latest_insights:
            # For first-time users, return plan info without insights
            return jsonify({
                'success': False,
                'error': 'No stored insights found',
                'plan': user.plan,
                'can_get_insights': user.can_get_ai_insights(),
                'last_insights_date': user.last_ai_insights_date.isoformat() if user.last_ai_insights_date else None,
                'next_available_date': user.get_next_ai_insights_date().isoformat() if user.get_next_ai_insights_date() else None
            }), 404
        
        # Parse the stored insights
        insights_data = json.loads(latest_insights.insights_data)
        
        return jsonify({
            'success': True,
            'insights': insights_data,
            'plan': user.plan,
            'can_get_insights': user.can_get_ai_insights(),
            'last_insights_date': user.last_ai_insights_date.isoformat() if user.last_ai_insights_date else None,
            'next_available_date': user.get_next_ai_insights_date().isoformat() if user.get_next_ai_insights_date() else None,
            'insights_created_at': latest_insights.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 