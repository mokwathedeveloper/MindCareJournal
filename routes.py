from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from app import app, db
from models import JournalEntry, PremiumSubscription
from flask_auth import require_login, auth_bp
from flask_login import current_user
from journal_service import create_journal_entry # Added for service layer
from forms import JournalEntryForm # Added for journal entry forms
from openai_service import analyze_journal_sentiment, generate_mood_insights
from datetime import datetime, timedelta
from sqlalchemy import desc
import os
from sqlalchemy.exc import SQLAlchemyError # Added for specific exception handling

# Constants for magic numbers
RECENT_ENTRIES_LIMIT = 5
MOOD_DATA_30_DAYS = 30
MOOD_DATA_90_DAYS = 90
ENTRIES_PER_PAGE = 10


# Register authentication blueprint
app.register_blueprint(auth_bp)

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
        .limit(RECENT_ENTRIES_LIMIT).all()

    # Get mood data for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=MOOD_DATA_30_DAYS)
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
    form = JournalEntryForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        success, message, category, entry_id = create_journal_entry(current_user.id, title, content)

        flash(message, category)
        if success:
            return redirect(url_for('view_entry', entry_id=entry_id))
        else:
            # If creation failed, re-render the form with previous data
            return render_template('new_entry.html', form=form) # Pass form to template
    
    # For GET request or if form validation fails
    return render_template('new_entry.html', form=form) # Pass form to template


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
    form = JournalEntryForm(obj=entry) # Populate form with existing entry data

    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        entry.updated_at = datetime.now()

        try:
            # Re-analyze sentiment
            sentiment_result = analyze_journal_sentiment(entry.content) # Use updated content
            entry.mood_score = sentiment_result.get('mood_score')
            entry.confidence = sentiment_result.get('confidence')
            entry.emotions = sentiment_result.get('emotions')

            db.session.commit()
            flash('Entry updated successfully!', 'success')
            return redirect(url_for('view_entry', entry_id=entry.id))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash('A database error occurred while updating your entry. Please try again.', 'error')
            app.logger.error(f"Database error updating journal entry: {e}")
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred while updating your entry. Please try again.', 'error')
            app.logger.error(f"Unexpected error updating journal entry: {e}")

    return render_template('edit_entry.html', entry=entry, form=form) # Pass form to template


@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
@require_login
def delete_entry(entry_id):
    """Delete a journal entry"""
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('A database error occurred while deleting your entry. Please try again.', 'error')
        app.logger.error(f"Database error deleting journal entry: {e}")
    except Exception as e:
        db.session.rollback()
        flash('An unexpected error occurred while deleting your entry. Please try again.', 'error')
        app.logger.error(f"Unexpected error deleting journal entry: {e}")

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
    ninety_days_ago = datetime.now() - timedelta(days=MOOD_DATA_90_DAYS)
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
        .paginate(page=page, per_page=ENTRIES_PER_PAGE, error_out=False)

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


@app.route('/profile')
@require_login
def profile():
    """User profile page"""
    return render_template('profile.html')


@app.route('/profile/edit', methods=['GET', 'POST'])
@require_login
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        current_user.first_name = first_name or None
        current_user.last_name = last_name or None
        current_user.updated_at = datetime.now()

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('A database error occurred while updating your profile. Please try again.', 'error')
            app.logger.error(f"Database error updating profile: {e}")
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred while updating your profile. Please try again.', 'error')
            app.logger.error(f"Unexpected error updating profile: {e}")

    return render_template('edit_profile.html')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


@app.route('/favicon.ico')
def favicon():
    """Serve favicon or return 204 if not found"""
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico',
                                  mimetype='image/vnd.microsoft.icon')
    except FileNotFoundError: # More specific for file not found
        # Return empty response with 204 No Content if favicon doesn't exist
        from flask import Response  # noqa: E402
        app.logger.warning("Favicon not found, returning 204.")
        return Response(status=204)
    except Exception as e: # Catch other unexpected errors
        from flask import Response  # noqa: E402
        app.logger.error(f"Unexpected error serving favicon: {e}")
        return Response(status=500) # Return 500 for other errors
