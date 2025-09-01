#!/usr/bin/env python3
"""
MindCare - AI-Powered Mental Health Journal
Main application entry point with production-ready security configurations.
"""

import os
from app import app
import routes  # noqa: F401
import flask_auth  # noqa: F401


def main():
    """
    Main function to start the application with environment-based configuration.

    Uses environment variables to determine if debug mode should be enabled.
    In production, debug should always be False for security.
    """
    # Get environment configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')  # Secure default
    port = int(os.environ.get('FLASK_PORT', '5001'))

    # Security warning for debug mode
    if debug_mode:
        print("⚠️  WARNING: Debug mode is enabled. Do not use in production!")
        print("   Set FLASK_DEBUG=False in production environment")

    # Start the application
    app.run(host=host, port=port, debug=debug_mode)


if __name__ == "__main__":
    main()
