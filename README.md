# Bariatric Surgery Assistant Chatbot

An intelligent chatbot system designed to assist patients with information about bariatric surgery, appointment scheduling, and post-operative care.

## Features

- 🤖 AI-powered chatbot for instant responses
- 📅 Appointment scheduling and management
- 👥 User role-based access control
- 📊 Admin dashboard with analytics
- 📧 Automated email notifications
- 🔒 Secure authentication system
- 📱 Responsive web interface
- 📝 Comprehensive surgery and diet information

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Email**: Flask-Mail
- **Authentication**: Flask-Login
- **Task Queue**: Celery with Redis
- **Testing**: pytest
- **Documentation**: Flasgger/apispec

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bariatric-chatbot.git
cd bariatric-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask init
flask create-admin  # Follow prompts to create admin user
```

6. Import initial data:
```bash
flask import-surgery-types config/surgery_types.json
flask import-diet-plans config/diet_plans.json
```

## Configuration

Key configuration options in `.env`:

```ini
# Flask
FLASK_APP=server.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

## Running the Application

1. Start Redis server (required for Celery):
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A server.celery worker --loglevel=info
```

3. Run the Flask application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Project Structure

```
bariatric_chatbot/
├── config/                 # Configuration files
│   ├── surgery_types.json
│   └── diet_plans.json
├── decorators/            # Custom decorators
│   └── role_required.py
├── templates/             # HTML templates
│   ├── admin/            # Admin interface templates
│   ├── email/            # Email templates
│   └── errors/           # Error pages
├── utils/                # Utility modules
│   ├── helpers.py
│   └── chatbot_logic.py
├── static/               # Static files
├── models.py            # Database models
├── forms.py             # Form definitions
├── server.py            # Main application
├── config.py            # App configuration
├── database.py          # Database setup
├── cli.py              # CLI commands
└── requirements.txt     # Dependencies
```

## API Documentation

API documentation is available at `/api/docs` when running in development mode.

## Testing

Run the test suite:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=bariatric_chatbot
```

## Admin Interface

Access the admin interface at `/admin` with your admin credentials.

Features:
- User management
- Appointment tracking
- Chat history
- System configuration
- Analytics dashboard

## Deployment

1. Set up a production server (e.g., Ubuntu with nginx)
2. Install PostgreSQL and Redis
3. Configure nginx as reverse proxy
4. Set up SSL certificate
5. Configure environment variables
6. Run with gunicorn:
```bash
gunicorn -w 4 -b 127.0.0.1:8000 server:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Security

- All passwords are hashed using bcrypt
- CSRF protection enabled
- Session security measures
- Rate limiting on API endpoints
- Input validation and sanitization
- Regular security updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@bariatric-assistant.com or create an issue in the repository.

## Acknowledgments

- Flask team for the excellent framework
- Tailwind CSS for the UI components
- Contributors and testers
