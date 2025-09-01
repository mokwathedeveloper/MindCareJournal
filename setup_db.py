#!/usr/bin/env python3
"""
Simple Database Setup Script for MindCare
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from flask_auth import register_user

def setup_database():
    """Set up the database tables"""
    with app.app_context():
        try:
            # Drop all tables first
            db.drop_all()
            print("🗑️  Dropped existing tables")

            # Create all tables fresh
            db.create_all()
            print("✅ Database tables recreated!")

        except Exception as e:
            print(f"❌ Database setup failed: {str(e)}")
            return False

        return True

def create_test_user():
    """Create a simple test user"""
    with app.app_context():
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(username='testuser').first()
            if existing_user:
                print("Test user already exists!")
                return existing_user

            # Create test user
            user = register_user(
                username='testuser',
                email='test@mindcare.app',
                password='password123',
                first_name='Test',
                last_name='User'
            )

            if user:
                user.email_verified = True
                db.session.commit()
                print("✅ Created test user:")
                print("   Username: testuser")
                print("   Password: password123")
                print("   Email: test@mindcare.app")
                return user
            else:
                print("❌ Failed to create test user")
                return None

        except Exception as e:
            print(f"❌ User creation failed: {str(e)}")
            return None

if __name__ == '__main__':
    print("🚀 Setting up MindCare Database")
    print("=" * 40)

    # Setup database
    if setup_database():
        print()
        # Create test user
        test_user = create_test_user()

        print()
        print("🎉 Setup complete!")
        print("=" * 40)
        print("Database has been reset and test user created.")
        print("You can now:")
        print("1. Run the application: python main.py")
        print("2. Register new users through the web interface")
        print("3. Login with test user (testuser / password123)")
