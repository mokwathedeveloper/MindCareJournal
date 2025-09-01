#!/usr/bin/env python3
"""
Demo User Initialization Script for MindCare

This script creates a demo user for testing the Flask authentication system.
Run this script after setting up the database to create test data.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, JournalEntry, PremiumSubscription
from flask_auth import register_user

def create_demo_user():
    """Create a demo user with sample data"""
    # Check if demo user already exists
    existing_user = User.query.filter_by(username='demo').first()
    if existing_user:
        print("Demo user already exists!")
        print(f"Username: {existing_user.username}")
        print(f"Email: {existing_user.email}")
        return existing_user

    # Create demo user
    print("Creating demo user...")
    demo_user = register_user(
        username='demo',
        email='demo@mindcare.app',
        password='password123',
        first_name='Demo',
        last_name='User'
    )

    if not demo_user:
        print("Failed to create demo user!")
        return None

    # Mark email as verified
    demo_user.email_verified = True
    db.session.commit()

    print(f"✅ Demo user created successfully!")
    print(f"Username: demo")
    print(f"Password: password123")
    print(f"Email: demo@mindcare.app")

    return demo_user

def create_sample_journal_entries(user):
    """Create sample journal entries for the demo user"""

    sample_entries = [
        {
            'title': 'A Great Day at Work',
            'content': 'Today was absolutely wonderful! I completed my project ahead of schedule and received positive feedback from my manager. I feel so accomplished and proud of myself. The team collaboration was excellent, and I learned some new skills. Looking forward to tomorrow!',
            'days_ago': 1
        },
        {
            'title': 'Feeling a bit overwhelmed',
            'content': 'Had a tough day today. Work was stressful with multiple deadlines approaching. I felt anxious and worried about meeting all the requirements. Need to practice some relaxation techniques and prioritize my tasks better. Tomorrow will be better.',
            'days_ago': 3
        },
        {
            'title': 'Weekend Reflection',
            'content': 'Spent a peaceful weekend with family. We went for a walk in the park and had a lovely picnic. It was so refreshing to disconnect from work and enjoy nature. I feel grateful for these moments and recharged for the week ahead.',
            'days_ago': 5
        },
        {
            'title': 'Learning Something New',
            'content': 'Started learning a new programming language today. It\'s challenging but exciting! I love the feeling of growth and expanding my skills. The online course is well-structured and I made good progress. Feeling motivated and curious.',
            'days_ago': 7
        },
        {
            'title': 'Dealing with Uncertainty',
            'content': 'Facing some uncertainty about future career moves. It\'s making me feel nervous and indecisive. I know change is part of life, but it still feels uncomfortable. Need to trust the process and focus on what I can control.',
            'days_ago': 10
        },
        {
            'title': 'Celebrating Small Wins',
            'content': 'Today I want to celebrate the small victories. I maintained my morning exercise routine, ate healthy meals, and completed all my planned tasks. These might seem minor, but they contribute to my overall well-being and happiness.',
            'days_ago': 12
        },
        {
            'title': 'Friendship and Connection',
            'content': 'Had a wonderful dinner with old friends tonight. We shared stories, laughed until our stomachs hurt, and supported each other through life\'s challenges. I feel so blessed to have such meaningful relationships in my life.',
            'days_ago': 15
        },
        {
            'title': 'Rainy Day Blues',
            'content': 'It\'s been raining for days and I\'m starting to feel a bit down. The gloomy weather affects my mood more than I\'d like to admit. I tried some indoor activities and listened to uplifting music. Hoping for sunshine soon.',
            'days_ago': 18
        },
        {
            'title': 'Personal Growth Journey',
            'content': 'Reflecting on how much I\'ve grown over the past year. I\'ve become more confident, learned to set better boundaries, and developed healthier habits. The journey isn\'t always easy, but I\'m proud of the progress I\'ve made.',
            'days_ago': 21
        },
        {
            'title': 'Finding Balance',
            'content': 'Trying to find the right balance between work, personal life, and self-care. Some days I feel like I\'ve got it figured out, other days it feels overwhelming. Today was a good balance day - productive at work, quality time with loved ones, and time for myself.',
            'days_ago': 25
        }
    ]

    print("Creating sample journal entries...")

    # Import here to avoid circular imports
    try:
        from openai_service import analyze_journal_sentiment
        openai_available = True
    except Exception as e:
        print(f"  ⚠️  OpenAI service not available: {str(e)}")
        openai_available = False

    created_entries = []

    for entry_data in sample_entries:
        entry = JournalEntry()
        entry.user_id = user.id
        entry.title = entry_data['title']
        entry.content = entry_data['content']
        entry.created_at = datetime.now() - timedelta(days=entry_data['days_ago'])
        entry.updated_at = entry.created_at

        # Try to analyze sentiment, but don't fail if OpenAI is not available
        if openai_available:
            try:
                sentiment_result = analyze_journal_sentiment(entry_data['content'])
                entry.mood_score = sentiment_result['mood_score']
                entry.confidence = sentiment_result['confidence']
                entry.emotions = sentiment_result['emotions']
                print(f"  ✅ Analyzed sentiment for: {entry.title}")
            except Exception as e:
                print(f"  ⚠️  Could not analyze sentiment for: {entry.title} ({str(e)})")
                openai_available = False

        if not openai_available:
            # Set varied default values to simulate different moods
            import random
            mood_variations = [
                {"mood": 4.2, "emotions": {"happiness": 35, "sadness": 5, "anxiety": 8, "anger": 2, "fear": 5, "excitement": 20, "calm": 20, "hope": 25}},
                {"mood": 2.5, "emotions": {"happiness": 10, "sadness": 25, "anxiety": 20, "anger": 8, "fear": 15, "excitement": 5, "calm": 12, "hope": 15}},
                {"mood": 3.8, "emotions": {"happiness": 25, "sadness": 8, "anxiety": 12, "anger": 5, "fear": 8, "excitement": 15, "calm": 22, "hope": 20}},
                {"mood": 2.8, "emotions": {"happiness": 12, "sadness": 22, "anxiety": 18, "anger": 10, "fear": 12, "excitement": 8, "calm": 15, "hope": 13}},
                {"mood": 4.5, "emotions": {"happiness": 40, "sadness": 3, "anxiety": 5, "anger": 2, "fear": 3, "excitement": 25, "calm": 17, "hope": 30}},
            ]
            variation = random.choice(mood_variations)
            entry.mood_score = variation["mood"]
            entry.confidence = 0.7
            entry.emotions = variation["emotions"]
            print(f"  📊 Set sample mood data for: {entry.title} (mood: {entry.mood_score})")

        db.session.add(entry)
        created_entries.append(entry)

    try:
        db.session.commit()
        print(f"✅ Created {len(created_entries)} sample journal entries!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create journal entries: {str(e)}")
        return []

    return created_entries

def create_premium_subscription(user):
    """Create a premium subscription for the demo user"""

    print("Creating premium subscription...")

    subscription = PremiumSubscription()
    subscription.user_id = user.id
    subscription.subscription_type = 'premium'
    subscription.is_active = True
    subscription.created_at = datetime.now()
    subscription.expires_at = datetime.now() + timedelta(days=30)  # 30-day trial

    db.session.add(subscription)

    try:
        db.session.commit()
        print("✅ Created premium subscription (30-day trial)!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create premium subscription: {str(e)}")

def main():
    """Main function to set up demo data"""

    with app.app_context():
        print("🚀 Initializing MindCare Demo Data")
        print("=" * 40)

        # Create demo user
        demo_user = create_demo_user()
        if not demo_user:
            print("❌ Failed to create demo user. Exiting.")
            return

        print()

        # Create sample journal entries
        entries = create_sample_journal_entries(demo_user)
        if entries:
            print(f"📖 Created {len(entries)} journal entries with mood analysis")

        print()

        # Create premium subscription
        create_premium_subscription(demo_user)

        print()
        print("🎉 Demo setup complete!")
        print("=" * 40)
        print("Login credentials:")
        print("  Username: demo")
        print("  Password: password123")
        print("  Email: demo@mindcare.app")
        print()
        print("Features available:")
        print("  ✅ User authentication")
        print("  ✅ Journal entries with AI mood analysis")
        print("  ✅ Mood tracking and visualization")
        print("  ✅ Premium subscription features")
        print()
        print("You can now start the application and test all features!")

if __name__ == '__main__':
    main()
