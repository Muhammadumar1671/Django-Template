# Django Plugin Template

A clean, production-ready Django starter template with modern UI and pre-configured settings for rapid development.

## ✨ Features

### 🎨 Modern Admin Interface
- **Unfold Admin** - Beautiful, modern Django admin interface
- Clean and intuitive UI out of the box
- Responsive design for all devices

### ⚙️ Pre-configured Settings
- **Environment-based configuration** - Separate settings for development and production
- **Django REST Framework** - Ready for API development
- **JWT Authentication** - Secure token-based authentication with SimpleJWT
- **CORS Support** - Pre-configured for cross-origin requests
- **Celery Integration** - Async task processing ready
- **Redis Caching** - High-performance caching layer
- **Django Channels** - WebSocket support for real-time features

### 🛠️ Developer-Friendly
- **SQLite for development** - No database setup required to get started
- **PostgreSQL support** - Easy switch for production
- **Environment variables** - Secure configuration management with `.env`
- **Logging configured** - File and console logging out of the box
- **Static file handling** - WhiteNoise for production-ready static files

## 📋 Requirements

- Python 3.10+
- pip
- virtualenv (recommended)

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd django-plugin
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env  # Create your .env file
# Edit .env with your configuration
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Collect static files

```bash
python manage.py collectstatic
```

### 8. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the admin interface.

## 📁 Project Structure

```
django-plugin/
├── base/                   # Main project directory
│   ├── core/              # Settings modules
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Development settings
│   │   └── production.py  # Production settings
│   ├── settings.py        # Settings router
│   ├── urls.py            # URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── logs/                  # Application logs
├── staticfiles/           # Collected static files
├── media/                 # User-uploaded media
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Environment
DJANGO_ENV=development  # or 'production'

# Security
DJANGO_SECRET_KEY=your-secret-key-here

# Database (optional - defaults to SQLite)
USE_POSTGRES=False
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis (optional)
REDIS_URL=redis://localhost:6379/1
REDIS_CHANNELS_URL=redis://localhost:6379/2

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Switching Between Environments

The project automatically loads the appropriate settings based on `DJANGO_ENV`:

- `development` → Uses `base/core/development.py`
- `production` → Uses `base/core/production.py`

## 🎯 What's Included

### Installed Apps
- Django Admin (with Unfold theme)
- Django REST Framework
- SimpleJWT (JWT authentication)
- CORS Headers
- Django Channels
- Token Blacklist

### Middleware
- CORS
- Security
- WhiteNoise (static files)
- Session management
- CSRF protection
- Authentication

### Development Features
- SQLite database (no setup required)
- In-memory cache (no Redis required)
- Console email backend
- Detailed logging
- Debug mode enabled
- Permissive CORS settings

### Production Features
- PostgreSQL database support
- Redis caching
- File-based logging
- Security hardening
- Static file compression
- HTTPS enforcement

## 📝 Usage

### Creating Your First App

```bash
python manage.py startapp myapp
```

Add your app to `LOCAL_APPS` in `base/core/base.py`:

```python
LOCAL_APPS = [
    'myapp',
]
```

### API Development

The project includes Django REST Framework. Create your API views in your app:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MyAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Hello, World!'})
```

### Using Celery (Optional)

Start Celery worker:

```bash
celery -A base worker -l info
```

Start Celery beat (for scheduled tasks):

```bash
celery -A base beat -l info
```

## 🧪 Testing

Run tests:

```bash
python manage.py test
```

## 📦 Deployment

For production deployment:

1. Set `DJANGO_ENV=production` in your environment
2. Configure PostgreSQL database
3. Set up Redis for caching and Celery
4. Configure your web server (Nginx, Apache)
5. Use a WSGI server (Gunicorn, uWSGI)
6. Set secure `SECRET_KEY`
7. Configure `ALLOWED_HOSTS`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Unfold Admin](https://unfoldadmin.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 💡 Tips

- Use `print()` statements for debugging in development (SQL logging is disabled by default)
- Check `logs/django.log` for application logs
- The admin interface is available at `/admin/`
- API endpoints can be added to your app's `urls.py`

## 🐛 Troubleshooting

### Static files not loading?
```bash
python manage.py collectstatic
```

### Database issues?
```bash
python manage.py migrate
```

### Port already in use?
```bash
python manage.py runserver 8090  # Use a different port
```

---

**Happy Coding! 🚀**
# Django-Template
