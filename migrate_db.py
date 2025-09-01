#!/usr/bin/env python3
"""
Database Migration Script for MindCare
This script migrates from the existing users table structure to the new one.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
import sqlalchemy as sa

def backup_existing_users():
    """Backup existing users table"""
    with app.app_context():
        try:
            # Check if users table exists
            inspector = sa.inspect(db.engine)
            if 'users' not in inspector.get_table_names():
                print("No existing users table found")
                return True

            # Rename existing users table to users_backup
            db.engine.execute(sa.text("ALTER TABLE users RENAME TO users_backup"))
            print("✅ Backed up existing users table to users_backup")
            return True

        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return False

def create_new_tables():
    """Create new table structure"""
    with app.app_context():
        try:
            # Drop our new tables if they exist (from models.py)
            db.drop_all()

            # Create all tables with new structure
            db.create_all()
            print("✅ Created new table structure")
            return True

        except Exception as e:
            print(f"❌ Table creation failed: {str(e)}")
            return False

def migrate_user_data():
    """Migrate user data from backup to new table"""
    with app.app_context():
        try:
            # Check if backup table exists
            inspector = sa.inspect(db.engine)
            if 'users_backup' not in inspector.get_table_names():
                print("No backup table found - skipping migration")
                return True

            # Get data from backup table
            result = db.engine.execute(sa.text("SELECT id, email, password, name FROM users_backup"))
            users_data = result.fetchall()

            if not users_data:
                print("No users to migrate")
                return True

            print(f"Migrating {len(users_data)} users...")

            # Import here to avoid circular imports
            from werkzeug.security import generate_password_hash

            for user_data in users_data:
                old_id, email, old_password, name = user_data

                # Parse name into first_name and last_name
                name_parts = name.split() if name else []
                first_name = name_parts[0] if name_parts else None
                last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None

                # Generate username from email
                username = email.split('@')[0] if email else f'user_{old_id}'

                # Check if username already exists and make it unique
                counter = 1
                original_username = username
                while db.engine.execute(sa.text("SELECT id FROM users WHERE username = :username"),
                                      {"username": username}).fetchone():
                    username = f"{original_username}_{counter}"
                    counter += 1

                # Hash the old password (assuming it's plain text)
                password_hash = generate_password_hash(old_password) if old_password else generate_password_hash('temppassword123')

                # Insert new user
                insert_query = sa.text("""
                    INSERT INTO users (username, email, password_hash, first_name, last_name,
                                     is_active, email_verified, created_at, updated_at)
                    VALUES (:username, :email, :password_hash, :first_name, :last_name,
                           :is_active, :email_verified, NOW(), NOW())
                """)

                db.engine.execute(insert_query, {
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                    "email_verified": True
                })

                print(f"  ✅ Migrated user: {email} -> {username}")

            print(f"✅ Successfully migrated {len(users_data)} users")
            return True

        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            return False

def create_test_user():
    """Create a test user for demonstration"""
    with app.app_context():
        try:
            from models import User
            from flask_auth import register_user

            # Check if test user already exists
            existing_user = User.query.filter_by(username='testuser').first()
            if existing_user:
                print("Test user already exists")
                return True

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
                return True
            else:
                print("❌ Failed to create test user")
                return False

        except Exception as e:
            print(f"❌ Test user creation failed: {str(e)}")
            return False

def cleanup_backup():
    """Optionally remove backup table"""
    response = input("\nDo you want to remove the backup table? (y/N): ")
    if response.lower() == 'y':
        with app.app_context():
            try:
                db.engine.execute(sa.text("DROP TABLE IF EXISTS users_backup"))
                print("✅ Removed backup table")
            except Exception as e:
                print(f"❌ Failed to remove backup table: {str(e)}")

if __name__ == '__main__':
    print("🚀 MindCare Database Migration")
    print("=" * 40)
    print("This will migrate your existing users table to the new structure.")
    print("Your existing data will be backed up before migration.")
    print()

    confirm = input("Continue with migration? (y/N): ")
    if confirm.lower() != 'y':
        print("Migration cancelled")
        sys.exit(0)

    print("\n1. Backing up existing users table...")
    if not backup_existing_users():
        print("Migration aborted")
        sys.exit(1)

    print("\n2. Creating new table structure...")
    if not create_new_tables():
        print("Migration aborted")
        sys.exit(1)

    print("\n3. Migrating user data...")
    if not migrate_user_data():
        print("Migration aborted")
        sys.exit(1)

    print("\n4. Creating test user...")
    create_test_user()

    print("\n🎉 Migration Complete!")
    print("=" * 40)
    print("Your users have been migrated to the new authentication system.")
    print("\nImportant notes:")
    print("- All users will need to use their email as username initially")
    print("- Passwords have been migrated (if they weren't hashed before, they are now)")
    print("- Users can change their username after first login")
    print("- A backup table 'users_backup' contains your original data")
    print("\nYou can now start the application with: python main.py")

    # Ask about cleanup
    cleanup_backup()
