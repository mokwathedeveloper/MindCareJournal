#!/usr/bin/env python3
"""
Debug Startup Script for MindCare
This script helps debug common issues when starting the application
"""

import sys
import os
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")

    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'wtforms',
        'bcrypt',
        'openai',
        'psycopg2'
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            missing.append((module, str(e)))
            print(f"  ❌ {module} - {e}")

    if missing:
        print("\n❌ Missing dependencies found!")
        print("Install them with: pip install <module_name>")
        return False

    print("✅ All dependencies available!")
    return True

def check_database():
    """Check database connection"""
    print("\n🔍 Checking database connection...")

    try:
        from app import app, db
        from models import User

        with app.app_context():
            # Test basic connection
            user_count = User.query.count()
            print(f"  ✅ Database connected! Found {user_count} users.")

            # Test table structure
            print("  ✅ User table accessible")

            return True

    except Exception as e:
        print(f"  ❌ Database error: {e}")
        print("  💡 Check your DATABASE_URL configuration")
        traceback.print_exc()
        return False

def check_config():
    """Check application configuration"""
    print("\n🔍 Checking configuration...")

    try:
        from app import app

        # Check secret key
        if app.config.get('SECRET_KEY'):
            print("  ✅ Secret key configured")
        else:
            print("  ⚠️  Secret key not set - using default")

        # Check database URL
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_url:
            print(f"  ✅ Database URL: {db_url[:50]}...")
        else:
            print("  ❌ No database URL configured")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def check_templates():
    """Check if required templates exist"""
    print("\n🔍 Checking templates...")

    required_templates = [
        'templates/base.html',
        'templates/landing.html',
        'templates/dashboard.html',
        'templates/auth/login.html',
        'templates/auth/register.html'
    ]

    missing = []
    for template in required_templates:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            missing.append(template)
            print(f"  ❌ {template}")

    if missing:
        print("❌ Missing templates found!")
        return False

    print("✅ All required templates found!")
    return True

def check_static_files():
    """Check if static files exist"""
    print("\n🔍 Checking static files...")

    static_files = [
        'static/css/style.css',
        'static/js/main.js'
    ]

    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️  {file_path} - missing but not critical")

    return True

def test_imports():
    """Test importing all main modules"""
    print("\n🔍 Testing module imports...")

    modules_to_test = [
        ('app', 'from app import app, db'),
        ('models', 'from models import User, JournalEntry'),
        ('routes', 'import routes'),
        ('flask_auth', 'import flask_auth'),
    ]

    for name, import_stmt in modules_to_test:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name} - {e}")
            traceback.print_exc()
            return False

    print("✅ All modules imported successfully!")
    return True

def start_debug_server():
    """Start the Flask application with debug information"""
    print("\n🚀 Starting Flask application...")

    try:
        from app import app
        import routes  # noqa: F401
        import flask_auth  # noqa: F401

        print("✅ Application modules loaded")
        print("✅ Routes registered")
        print("✅ Authentication system loaded")

        # Find an available port
        import socket

        def find_free_port():
            for port in range(5001, 5010):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind(('localhost', port))
                    sock.close()
                    return port
                except OSError:
                    continue
            return 5001

        port = find_free_port()

        print(f"\n🎉 Starting server on http://localhost:{port}")
        print("📝 Test credentials:")
        print("   Username: testuser")
        print("   Password: password123")
        print("\n🔗 Available endpoints:")
        print(f"   http://localhost:{port}/          - Home page")
        print(f"   http://localhost:{port}/test      - Test endpoint")
        print(f"   http://localhost:{port}/auth/login - Login page")
        print(f"   http://localhost:{port}/dashboard - Dashboard (requires login)")

        print("\n⚠️  If you see errors, check the console output above.")
        print("   Press Ctrl+C to stop the server")
        print("-" * 60)

        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🚀 MindCare Debug Startup")
    print("=" * 60)

    # Run all checks
    checks = [
        check_dependencies,
        check_config,
        check_database,
        check_templates,
        check_static_files,
        test_imports
    ]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 All checks passed! Starting application...")
        start_debug_server()
    else:
        print("❌ Some checks failed. Please fix the issues above before starting.")
        print("\n💡 Common solutions:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Check database connection and credentials")
        print("   3. Verify all template files exist")
        print("   4. Check file permissions")

        sys.exit(1)

if __name__ == '__main__':
    main()
