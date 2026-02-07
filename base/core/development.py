'''
Development Settings

This extends the base.py file and overrides settings specific to development.
Includes relaxed security, detailed logging, and development-friendly configurations.
'''
from .base import *

# =============================================================================
# CORE SETTINGS
# =============================================================================

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-&r((#t-_n#5_et_zbm4ycxmxqre=ph6%p8(49i0$!3iihxz!j0')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '*']

# =============================================================================
# CORS SETTINGS - Permissive for Development
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# DATABASE - SQLite or PostgreSQL for Development
# =============================================================================

# Use PostgreSQL if USE_POSTGRES=True in .env, otherwise use SQLite
if os.getenv('USE_POSTGRES', 'False').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'django_dev'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # Default: SQLite (no additional setup required)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# CACHE - Local Memory Cache for Development
# =============================================================================

# Override Redis with local memory cache for development (no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dev-cache',
    }
}

# Use database sessions for development (easier debugging)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# CHANNELS - In-Memory Layer for Development
# =============================================================================

# Override Redis channels with in-memory layer (no Redis required)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# =============================================================================
# EMAIL - Console Backend for Development
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# DJANGO DEBUG TOOLBAR (Optional)
# =============================================================================

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Uncomment if you have django-debug-toolbar installed
    # INSTALLED_APPS += ['debug_toolbar']
    # MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# =============================================================================
# LOGGING - Verbose for Development
# =============================================================================

# Disable SQL query logging to see print() statements clearly
LOGGING['loggers']['django.db.backends']['level'] = 'WARNING'  # Suppress SQL queries
LOGGING['handlers']['console']['level'] = 'INFO'  # Keep console at INFO level

# =============================================================================
# DEVELOPMENT-SPECIFIC APPS (Optional)
# =============================================================================

# Uncomment as needed
# INSTALLED_APPS += [
#     'django_extensions',  # Provides shell_plus, runserver_plus, etc.
# ]

# =============================================================================
# SECURITY - Disabled for Development
# =============================================================================

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# =============================================================================
# CSRF TRUSTED ORIGINS - Development URLs
# =============================================================================

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',  # Vite default
    'http://127.0.0.1:5173',
]

# =============================================================================
# FILE UPLOAD SETTINGS - More Permissive for Development
# =============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# =============================================================================
# STATIC FILES - Django's Built-in Server
# =============================================================================

# No WhiteNoise needed in development
# Django's built-in static file serving is sufficient

# =============================================================================
# UNFOLD ADMIN - Development Configuration
# =============================================================================

UNFOLD["SITE_TITLE"] = os.getenv('UNFOLD_SITE_TITLE', 'Django Admin (Dev)')
UNFOLD["SITE_HEADER"] = os.getenv('UNFOLD_SITE_HEADER', 'Django Administration (Development)')
UNFOLD["SITE_URL"] = os.getenv('UNFOLD_SITE_URL', 'http://localhost:8000')

# =============================================================================
# CELERY - Development Settings
# =============================================================================

# Use eager mode for development (tasks run synchronously, no Celery worker needed)
# Uncomment to enable:
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True
