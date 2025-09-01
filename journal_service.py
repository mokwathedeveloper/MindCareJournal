from app import db, app
from models import JournalEntry, User
from openai_service import analyze_journal_sentiment
import logging
from sqlalchemy.exc import SQLAlchemyError # Added for specific exception handling

def create_journal_entry(user_id, title, content):
    """
    Handles the creation of a new journal entry, including AI sentiment analysis and database persistence.
    Returns a tuple: (success_boolean, message, category, entry_id_if_success)
    """
    app.logger.info(f"Attempting to create entry for user_id: {user_id}, title: {title[:50]}...")

    # Verify user exists in database (moved from routes)
    user_check = User.query.get(user_id)
    if not user_check:
        app.logger.error(f"User {user_id} not found in mindcare_users table during entry creation.")
        return False, 'User authentication error. Please log in again.', 'error', None

    entry = JournalEntry()
    entry.user_id = user_id
    entry.title = title
    entry.content = content

    try:
        sentiment_result = analyze_journal_sentiment(content)
        entry.mood_score = sentiment_result.get('mood_score')
        entry.confidence = sentiment_result.get('confidence')
        entry.emotions = sentiment_result.get('emotions')

        api_error_message = None
        if 'api_error' in sentiment_result:
            api_error_message = sentiment_result['api_error']
            app.logger.warning(f"AI API error (using fallback) for user {user_id}: {api_error_message}")

        db.session.add(entry)
        db.session.commit()

        message = 'Journal entry saved successfully with AI mood analysis!'
        category = 'success'
        if api_error_message:
            message = 'Entry saved! AI analysis unavailable - using keyword analysis.'
            category = 'warning'

        app.logger.info(f"Journal entry {entry.id} saved for user {user_id}.")
        return True, message, category, entry.id

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Database error saving journal entry for user {user_id}: {e}")
        # More specific error messages for database issues
        if "foreign key constraint" in str(e).lower():
            return False, 'Authentication error. Please log out and log back in.', 'error', None
        else:
            return False, 'A database error occurred while saving your entry. Please try again.', 'error', None
    except Exception as e: # Catch other unexpected errors
        db.session.rollback() # Ensure rollback for any unhandled exception before this point
        app.logger.error(f"Unexpected error saving journal entry for user {user_id}: {e}")
        return False, 'An unexpected error occurred while saving your entry. Please try again.', 'error', None
