from functools import wraps
from flask import request, redirect, url_for, session, flash, render_template
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app import app, db
from models import User
import re
from mail_service import send_password_reset_email, send_verification_email # Added for email sending
from app import limiter # Added for rate limiting
from sqlalchemy.exc import SQLAlchemyError # Added for specific exception handling

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Authentication Forms
class LoginForm(FlaskForm):
    username_or_email = StringField(
        'Username or Email',
        validators=[DataRequired(), Length(min=3, max=120)],
        render_kw={"placeholder": "Enter your username or email"})
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your password"})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Choose a username"})
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your email"})
    first_name = StringField(
        'First Name',
        validators=[Length(max=100)],
        render_kw={"placeholder": "Your first name (optional)"})
    last_name = StringField(
        'Last Name',
        validators=[Length(max=100)],
        render_kw={"placeholder": "Your last name (optional)"})
    password = PasswordField(
        'Password',
        validators=[DataRequired(), validate_strong_password],
        render_kw={"placeholder": "Create a password (min 8 characters, with uppercase, lowercase, digit, and special character)"})
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={"placeholder": "Confirm your password"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # Check if username contains only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email address already registered. Please use a different one.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter your current password"})
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), validate_strong_password],
        render_kw={"placeholder": "Enter new password (min 8 characters, with uppercase, lowercase, digit, and special character)"})
    new_password2 = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password')],
        render_kw={"placeholder": "Confirm new password"})
    submit = SubmitField('Change Password')


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Enter your registered email"})
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[DataRequired(), validate_strong_password],
        render_kw={"placeholder": "Enter new password (min 8 characters, with uppercase, lowercase, digit, and special character)"})
    password2 = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={"placeholder": "Confirm new password"})
    submit = SubmitField('Reset Password')

# Authentication Functions

def authenticate_user(username_or_email, password):
    """
    Authenticate a user with username/email and password
    Returns the user object if authentication successful, None otherwise
    """
    # Try to find user by username first
    user = User.query.filter_by(username=username_or_email).first()

    # If not found by username, try email
    if not user:
        user = User.query.filter_by(email=username_or_email.lower()).first()

    # Check if user exists and password is correct
    if user and user.check_password(password):
        if user.is_active:
            return user
        else:
            # Do not flash message here, handle in calling route
            return None

    return None


def register_user(username, email, password, first_name=None, last_name=None):
    """
    Register a new user
    Returns the user object if successful, None otherwise
    """
    try:
        # Create new user
        user = User()
        user.username = username
        user.email = email.lower()
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.is_active = True
        user.email_verified = False  # You can implement email verification later

        # Save to database
        db.session.add(user)
        db.session.commit()

        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Database error registering user: {e}")
        return None
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Unexpected error registering user: {e}")
        return None


def require_login(f):
    """
    Decorator to require login for a route
    Replaces the old Replit Auth decorator
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Store the intended destination
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_redirect_url():
    """
    Get the URL to redirect to after successful login
    """
    next_url = session.pop('next_url', None)
    if next_url and next_url != request.url:
        return next_url
    return url_for('dashboard')

def validate_strong_password(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>-]', password):
        raise ValidationError('Password must contain at least one special character.')


# Blueprint for authentication routes
from flask import Blueprint  # noqa: E402

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Added for rate limiting
def login():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(form.username_or_email.data, form.password.data)

        if user:
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.first_name or user.username}!', 'success')
            return redirect(get_redirect_url())
        else:
            flash('Invalid username/email or password.', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("2 per minute") # Added for rate limiting
def register():
    """Registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = register_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data or None,
            last_name=form.last_name.data or None
        )

        if user:
            # Generate and send email verification token
            token = user.generate_email_verification_token()
            db.session.commit() # Commit token to database

            if send_verification_email(user, token):
                flash(f'Welcome to MindCare, {user.first_name or user.username}! Your account has been created successfully. Please check your email to verify your account.', 'success')
            else:
                flash(f'Welcome to MindCare, {user.first_name or user.username}! Your account has been created, but we could not send a verification email. Please try again later.', 'warning')
            
            login_user(user) # Log in the user even if email sending fails
            return redirect(url_for('dashboard'))
        else:
            flash('There was an error creating your account. Please try again.', 'error')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out successfully. See you soon!', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route"""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Current password is incorrect.', 'error')

    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute") # Added for rate limiting
def forgot_password():
    """Forgot password route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            db.session.commit()

            # Send password reset email
            if send_password_reset_email(user, token):
                flash('Password reset instructions have been sent to your email address.', 'info')
            else:
                flash('Failed to send password reset email. Please try again later.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('If that email address is registered, you will receive reset instructions shortly.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # Find user with this token
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()

        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user's email address with a token"""
    user = User.query.filter_by(email_verification_token=token).first()

    if not user or not user.verify_email_verification_token(token):
        flash('Invalid or expired email verification link.', 'error')
        return redirect(url_for('auth.login')) # Redirect to login or a specific error page

    user.email_verified = True
    user.clear_email_verification_token()
    db.session.commit()

    flash('Your email address has been successfully verified! You can now log in.', 'success')
    return redirect(url_for('auth.login')) # Redirect to login page after successful verification

# Helper function to check if user has premium subscription

def has_premium_subscription(user=None):
    """Check if user has an active premium subscription"""
    if not user:
        user = current_user

    if not user.is_authenticated:
        return False

    from models import PremiumSubscription
    subscription = PremiumSubscription.query.filter_by(
        user_id=user.id,
        is_active=True
    ).first()

    if subscription and subscription.expires_at:
        from datetime import datetime
        return subscription.expires_at > datetime.now()

    return subscription is not None


def require_premium(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    @require_login
    def decorated_function(*args, **kwargs):
        if not has_premium_subscription():
            flash('This feature requires a premium subscription.', 'warning')
            return redirect(url_for('premium'))
        return f(*args, **kwargs)
    return decorated_function
