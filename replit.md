# Overview

MindCare is an AI-powered mental health journal application that helps users track their emotions, understand mood patterns, and support their wellness journey. The application allows users to write daily journal entries, automatically analyzes sentiment using OpenAI's GPT-5 model, and provides visual mood tracking over time. It includes premium features for advanced analytics and professional support access.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **JavaScript Libraries**: Chart.js for mood visualization, Feather Icons for consistent iconography
- **Styling**: Custom CSS with CSS variables for theming, Bootstrap for layout and components
- **Client-side Features**: Form validation, auto-save functionality, keyboard shortcuts, smooth scrolling

## Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database Design**: Relational model with Users, JournalEntry, OAuth, and PremiumSubscription tables
- **Authentication**: Replit Auth integration using OAuth2 with Flask-Login for session management
- **AI Integration**: OpenAI GPT-5 API for sentiment analysis returning mood scores (1-5), confidence levels, and detailed emotion percentages
- **Route Structure**: Separation of concerns with dedicated route handlers for dashboard, journal CRUD operations, mood analytics, and premium features

## Data Storage
- **Primary Database**: PostgreSQL (configurable via DATABASE_URL environment variable)
- **Connection Management**: SQLAlchemy with connection pooling (300-second recycle, pre-ping enabled)
- **Schema Design**: 
  - Users table with Replit Auth compatibility
  - JournalEntry table with sentiment analysis results stored as JSON
  - OAuth table for authentication token management
  - PremiumSubscription table for monetization features

## Authentication & Authorization
- **Provider**: Replit Auth with OAuth2 flow
- **Session Management**: Flask-Login with permanent sessions
- **Access Control**: Login required decorators for protected routes
- **User Data**: Profile information integration with journal ownership

# External Dependencies

## AI Services
- **OpenAI API**: GPT-5 model for sentiment analysis and emotion detection
- **Configuration**: API key via OPENAI_API_KEY environment variable
- **Response Format**: Structured JSON with mood scores, confidence levels, and emotion percentages

## Authentication Services
- **Replit Auth**: OAuth2 provider for user authentication
- **Flask-Dance**: OAuth integration library for token management
- **Session Storage**: Custom UserSessionStorage class for database-backed token persistence

## Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and components
- **Chart.js**: JavaScript library for mood trend visualization
- **Feather Icons**: Icon library for consistent UI elements

## Database
- **PostgreSQL**: Primary database (configurable)
- **SQLAlchemy**: ORM with declarative base model
- **Connection Pooling**: Automated connection management with health checks

## Security & Infrastructure
- **ProxyFix**: Werkzeug middleware for proper HTTPS URL generation
- **Environment Variables**: Configuration management for sensitive data (API keys, database URLs, session secrets)
- **CSRF Protection**: Form validation and security measures