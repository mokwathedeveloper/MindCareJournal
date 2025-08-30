from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import JournalEntry, PremiumSubscription
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
from openai_service import analyze_journal_sentiment, generate_mood_insights
from datetime import datetime, timedelta
from sqlalchemy import desc

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page for logged out users, dashboard for logged in users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard showing recent entries and mood overview"""
    # Get recent entries
    recent_entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .order_by(desc(JournalEntry.created_at))\
        .limit(5).all()
    
    # Get mood data for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    mood_entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .filter(JournalEntry.created_at >= thirty_days_ago)\
        .filter(JournalEntry.mood_score.isnot(None))\
        .order_by(JournalEntry.created_at).all()
    
    # Calculate average mood
    avg_mood = None
    if mood_entries:
        avg_mood = sum(entry.mood_score for entry in mood_entries) / len(mood_entries)
    
    return render_template('dashboard.html', 
                         recent_entries=recent_entries, 
                         mood_entries=mood_entries,
                         avg_mood=avg_mood)

@app.route('/new-entry', methods=['GET', 'POST'])
@require_login
def new_entry():
    """Create a new journal entry"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Please fill in both title and content.', 'error')
            return render_template('new_entry.html', title=title, content=content)
        
        # Create new entry
        entry = JournalEntry()
        entry.user_id = current_user.id
        entry.title = title
        entry.content = content
        
        try:
            # Analyze sentiment using OpenAI
            sentiment_result = analyze_journal_sentiment(content)
            entry.mood_score = sentiment_result['mood_score']
            entry.confidence = sentiment_result['confidence']
            entry.emotions = sentiment_result['emotions']
            
            db.session.add(entry)
            db.session.commit()
            
            flash('Journal entry saved successfully!', 'success')
            return redirect(url_for('view_entry', entry_id=entry.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error saving entry. Please try again.', 'error')
            app.logger.error(f"Error saving journal entry: {e}")
            
        return render_template('new_entry.html', title=title, content=content)
    
    return render_template('new_entry.html')

@app.route('/entry/<int:entry_id>')
@require_login
def view_entry(entry_id):
    """View a specific journal entry"""
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    return render_template('view_entry.html', entry=entry)

@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_entry(entry_id):
    """Edit an existing journal entry"""
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            flash('Please fill in both title and content.', 'error')
            return render_template('edit_entry.html', entry=entry)
        
        entry.title = title
        entry.content = content
        entry.updated_at = datetime.now()
        
        try:
            # Re-analyze sentiment
            sentiment_result = analyze_journal_sentiment(content)
            entry.mood_score = sentiment_result['mood_score']
            entry.confidence = sentiment_result['confidence']
            entry.emotions = sentiment_result['emotions']
            
            db.session.commit()
            flash('Entry updated successfully!', 'success')
            return redirect(url_for('view_entry', entry_id=entry.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating entry. Please try again.', 'error')
            app.logger.error(f"Error updating journal entry: {e}")
    
    return render_template('edit_entry.html', entry=entry)

@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
@require_login
def delete_entry(entry_id):
    """Delete a journal entry"""
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting entry. Please try again.', 'error')
        app.logger.error(f"Error deleting journal entry: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/mood-trends')
@require_login
def mood_trends():
    """Show detailed mood trends and analytics"""
    # Get all entries with mood data
    entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .filter(JournalEntry.mood_score.isnot(None))\
        .order_by(JournalEntry.created_at).all()
    
    # Prepare data for insights
    entries_data = [
        {
            'date': entry.created_at.strftime('%Y-%m-%d'),
            'mood_score': entry.mood_score,
            'emotions': entry.emotions
        } for entry in entries
    ]
    
    # Generate AI insights
    insights = generate_mood_insights(entries_data)
    
    return render_template('mood_trends.html', entries=entries, insights=insights)

@app.route('/api/mood-data')
@require_login
def mood_data_api():
    """API endpoint for mood chart data"""
    # Get mood data for the last 90 days
    ninety_days_ago = datetime.now() - timedelta(days=90)
    entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .filter(JournalEntry.created_at >= ninety_days_ago)\
        .filter(JournalEntry.mood_score.isnot(None))\
        .order_by(JournalEntry.created_at).all()
    
    data = {
        'dates': [entry.created_at.strftime('%Y-%m-%d') for entry in entries],
        'mood_scores': [entry.mood_score for entry in entries],
        'confidence': [entry.confidence for entry in entries]
    }
    
    return jsonify(data)

@app.route('/entries')
@require_login
def all_entries():
    """Show all journal entries with pagination"""
    page = request.args.get('page', 1, type=int)
    entries = JournalEntry.query.filter_by(user_id=current_user.id)\
        .order_by(desc(JournalEntry.created_at))\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('all_entries.html', entries=entries)

@app.route('/premium')
@require_login
def premium():
    """Premium features page"""
    # Check if user has premium subscription
    subscription = PremiumSubscription.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    return render_template('premium.html', subscription=subscription)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
