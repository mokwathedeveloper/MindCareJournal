from flask import render_template, url_for
from flask_mail import Message
from app import mail, app

def send_password_reset_email(user, token):
    """
    Sends a password reset email to the user.
    """
    reset_link = url_for('auth.reset_password', token=token, _external=True)
    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = render_template('email/password_reset.txt', user=user, reset_link=reset_link)
    msg.html = render_template('email/password_reset.html', user=user, reset_link=reset_link)
    try:
        mail.send(msg)
        app.logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        app.logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False

def send_verification_email(user, token):
    """
    Sends an email verification email to the user.
    """
    verify_link = url_for('auth.verify_email', token=token, _external=True)
    msg = Message('Verify Your Email Address',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = render_template('email/email_verification.txt', user=user, verify_link=verify_link)
    msg.html = render_template('email/email_verification.html', user=user, verify_link=verify_link)
    try:
        mail.send(msg)
        app.logger.info(f"Email verification email sent to {user.email}")
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email verification email to {user.email}: {e}")
        return False
