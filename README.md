# MindCare Journal - AI-Powered Mental Health Journal

## Project Description
MindCare Journal is an AI-powered mental health journaling application designed to help users track their mood, gain insights into their emotional well-being, and manage their mental health. It leverages AI for sentiment analysis of journal entries and provides mood trends and analytics.

## Features
*   User Authentication (Registration, Login, Logout, Password Reset)
*   Journal Entry Creation, Viewing, Editing, and Deletion
*   AI-Powered Sentiment Analysis of Journal Entries
*   Mood Trend Visualization and Insights
*   User Profile Management
*   Premium Subscription (Placeholder)

## Setup and Installation

### Prerequisites
*   Python 3.12+
*   PostgreSQL database (or other compatible database)
*   OpenAI API Key (for sentiment analysis)

### 1. Clone the Repository
```bash
git clone https://github.com/mokwathedeveloper/MindCareJournal.git
cd MindCareJournal
```

### 2. Set up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt # Assuming requirements.txt exists or generate one from uv.lock
```
*(Note: If `requirements.txt` is not present, you might need to generate it from `uv.lock` or install dependencies manually based on `uv.lock`.)*

### 4. Configure Environment Variables
Create a `.env` file in the root directory of the project and add the following:

```
SESSION_SECRET="YOUR_VERY_LONG_RANDOM_SECRET_KEY"
DATABASE_URL="postgresql://user:password@host:port/database_name"
# Example: DATABASE_URL="postgresql://mindj:simple1234@localhost:5432/mjdatabase"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# Optional: Email Configuration for Password Reset
MAIL_SERVER="smtp.your-email-provider.com"
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME="your_email@example.com"
MAIL_PASSWORD="your_email_password"
MAIL_DEFAULT_SENDER="noreply@your-domain.com"
```
*Replace placeholder values with your actual credentials and settings.*

### 5. Initialize the Database
```bash
# Ensure your virtual environment is active
python app.py # This will create tables on first run based on init_db()
# For production, consider using Flask-Migrate for proper migrations
```

### 6. Run the Application
```bash
# Ensure your virtual environment is active
flask run
# Or using Gunicorn for production
# gunicorn app:app
```

## API Endpoints (Overview)
*   `/auth/login` (POST): User login
*   `/auth/register` (POST): User registration
*   `/auth/forgot-password` (POST): Request password reset
*   `/auth/reset-password/<token>` (GET, POST): Reset password
*   `/new-entry` (GET, POST): Create a new journal entry
*   `/entry/<int:entry_id>` (GET): View a specific journal entry
*   `/entry/<int:entry_id>/edit` (GET, POST): Edit a journal entry
*   `/entry/<int:entry_id>/delete` (POST): Delete a journal entry
*   `/dashboard` (GET): User dashboard
*   `/mood-trends` (GET): View mood trends and insights
*   `/api/mood-data` (GET): API for mood chart data
*   `/profile` (GET): User profile
*   `/profile/edit` (GET, POST): Edit user profile

## Contributing
(Add contributing guidelines here)

## License
(Add license information here)