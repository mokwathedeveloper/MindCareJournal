from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string


class User(UserMixin, db.Model):
    __tablename__ = 'mindcare_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    profile_image_url = db.Column(db.String(255), nullable=True)

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)

    # Password reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_token_expires = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship to journal entries
    journal_entries = db.relationship('JournalEntry', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Generate a secure random token for password reset"""
        token_chars = string.ascii_letters + string.digits
        self.reset_token = ''.join(secrets.choice(token_chars) for _ in range(32))
        # Token expires in 1 hour
        self.reset_token_expires = datetime.now() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if the reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if datetime.now() > self.reset_token_expires:
            return False
        return self.reset_token == token

    def clear_reset_token(self):
        """Clear the reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None

    def generate_email_verification_token(self):
        """Generate a secure random token for email verification"""
        token_chars = string.ascii_letters + string.digits
        self.email_verification_token = ''.join(secrets.choice(token_chars) for _ in range(32))
        # Token expires in 24 hours
        self.email_verification_token_expires = datetime.now() + timedelta(hours=24)
        return self.email_verification_token

    def verify_email_verification_token(self, token):
        """Verify if the email verification token is valid and not expired"""
        if not self.email_verification_token or not self.email_verification_token_expires:
            return False
        if datetime.now() > self.email_verification_token_expires:
            return False
        return self.email_verification_token == token

    def clear_email_verification_token(self):
        """Clear the email verification token after use"""
        self.email_verification_token = None
        self.email_verification_token_expires = None

    @property
    def full_name(self):
        """Return the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username

    def __repr__(self):
        return f'<User {self.username}>'


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('mindcare_users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Sentiment analysis results
    mood_score = db.Column(db.Float)  # Overall mood score (1-5)
    confidence = db.Column(db.Float)  # Confidence level (0-1)
    emotions = db.Column(db.JSON)  # Detailed emotion analysis

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<JournalEntry {self.title}>'


class PremiumSubscription(db.Model):
    __tablename__ = 'premium_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('mindcare_users.id'), nullable=False)
    subscription_type = db.Column(db.String(50), nullable=False)  # 'premium', 'therapist_access'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='premium_subscription')

    def __repr__(self):
        return f'<PremiumSubscription {self.subscription_type} for user {self.user_id}>'
