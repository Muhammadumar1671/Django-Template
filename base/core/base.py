"""
Django settings for base project.

This is the base settings file that contains all common settings.
Environment-specific settings are in development.py and production.py
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import sys
from datetime import timedelta

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# This points to the project root (django-plugin/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to Python path
sys.path.insert(0, str(BASE_DIR / 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

# Unfold Admin (must come before django.contrib.admin)
UNFOLD_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
]

# Django Core Apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

# Third Party Apps
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    'django_filters',
]

# Local Apps (add your apps here)
LOCAL_APPS = [
    'base',  # Required for management commands
    'apps.authentication',  # Authentication system
    'apps.email_service',  # Email service
]

INSTALLED_APPS = UNFOLD_APPS + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'base.urls'

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'base.wsgi.application'
ASGI_APPLICATION = 'base.asgi.application'

# =============================================================================
# DJANGO CHANNELS CONFIGURATION
# =============================================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.getenv('REDIS_CHANNELS_URL', 'redis://localhost:6379/2')],
        },
    },
}

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# =============================================================================
# SIMPLE JWT CONFIGURATION
# =============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# =============================================================================
# CACHE CONFIGURATION (Redis)
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 3600,  # 1 hour default timeout
        'KEY_PREFIX': 'django',
        'VERSION': 1,
    }
}

# =============================================================================
# SESSION CONFIGURATION
# =============================================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = False

# =============================================================================
# CELERY CONFIGURATION
# =============================================================================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_ENABLE_LOGGING = True

# Celery performance optimizations
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = 'server@example.com'

# Email Service Configuration
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'True').lower() in ['true', '1', 'yes']  # Global email enable/disable
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'smtp')  # 'sendgrid', 'resend', or 'smtp'
EMAIL_PROVIDER_API_KEY = os.getenv('EMAIL_PROVIDER_API_KEY', '')
DEFAULT_FROM_NAME = os.getenv('DEFAULT_FROM_NAME', 'Django App')

# Email Template Source Configuration
# Set to 'db' to use database templates first (fallback to static)
# Set to 'static' to only use static template files
# Set to 'db_only' to only use database templates (no fallback)
USE_DB_EMAIL_TEMPLATES = os.getenv('USE_DB_EMAIL_TEMPLATES', 'db')  # 'db', 'static', or 'db_only'

# Frontend Configuration (for email links)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
SITE_NAME = os.getenv('SITE_NAME', 'Django App')

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# CSRF CONFIGURATION
# =============================================================================

CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to read it
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False

# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = 'authentication.User'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# =============================================================================
# FILE UPLOAD SETTINGS
# =============================================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# UNFOLD ADMIN CONFIGURATION
# =============================================================================

UNFOLD = {
    "SITE_TITLE": os.getenv('UNFOLD_SITE_TITLE', 'Django Admin'),
    "SITE_HEADER": os.getenv('UNFOLD_SITE_HEADER', 'Django Administration'),
    "SITE_URL": os.getenv('UNFOLD_SITE_URL', '/'),
    "SITE_ICON": None,
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84"
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": []
    },
    "TABS": [],
}

# =============================================================================
# PAGINATION
# =============================================================================

PAGINATION_PAGE_SIZE = 20

# =============================================================================
# DATE AND TIME FORMATS
# =============================================================================

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
SHORT_DATE_FORMAT = 'm/d/Y'
SHORT_DATETIME_FORMAT = 'm/d/Y P'

