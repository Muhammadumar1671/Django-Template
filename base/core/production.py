"""
Production Settings - Optimized for High Concurrency

This configuration is designed for high-performance production deployments
with proper security, connection pooling (PgBouncer), caching, and async support.
"""

from .base import *
import os
import dj_database_url
import psycopg2.extensions

# =============================================================================
# CORE SETTINGS
# =============================================================================

DEBUG = False

# Security: Restrict allowed hosts in production
allowed_hosts_env = os.getenv('ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = []

# Secret key validation
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")

# =============================================================================
# CORS SETTINGS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False  # Disabled for production security

cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
else:
    CORS_ALLOWED_ORIGINS = []

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-requested-with',
    'cache-control',
    'content-disposition',
]

# =============================================================================
# DATABASE SETTINGS - Optimized for High Concurrency with PgBouncer
# =============================================================================

# IMPORTANT: We use PgBouncer (external connection pooler) instead of Django's CONN_MAX_AGE
# This avoids conflicts and is the production-standard approach
#
# PgBouncer handles:
# - Connection pooling (transaction-level)
# - Connection reuse
# - Load balancing
# - Connection limits
#
# Django connects to PgBouncer (port 6432) instead of PostgreSQL (port 5432)

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Configure Django to connect to PgBouncer (not PostgreSQL directly)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,  # Disable persistent connections - PgBouncer manages this
            conn_health_checks=True,  # Enable connection health checks
            engine='django.db.backends.postgresql'
        )
    }
    
    # PostgreSQL-specific options for optimal performance
    # NOTE: We do NOT include statement_timeout here because PgBouncer in transaction
    # pooling mode cannot handle per-connection startup parameters.
    # Instead, set statement_timeout at the database level:
    # ALTER DATABASE your_db SET statement_timeout = '30s';
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 5,
        'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
    }
else:
    # Fallback to environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'django_db'),
            'USER': os.getenv('DB_USER', 'django_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '6432'),  # PgBouncer default port
            'CONN_MAX_AGE': 0,  # Disable - PgBouncer manages connections
            'OPTIONS': {
                'connect_timeout': 5,
                'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
            }
        }
    }

# =============================================================================
# PGBOUNCER CONFIGURATION REFERENCE
# =============================================================================
# 
# PgBouncer Configuration (pgbouncer.ini):
# 
# [databases]
# your_db = host=localhost port=5432 dbname=your_db user=postgres password=...
#
# [pgbouncer]
# pool_mode = transaction          # Transaction-level pooling (most efficient)
# max_client_conn = 10000          # Max connections from Django
# default_pool_size = 25           # Connections per database
# min_pool_size = 10               # Minimum connections to maintain
# reserve_pool_size = 5            # Reserve connections for emergencies
# reserve_pool_timeout = 3         # Timeout for reserve pool
# server_lifetime = 3600           # Recycle server connections every hour
# server_idle_timeout = 600        # Close idle connections after 10 min
# listen_port = 6432               # PgBouncer port
# listen_addr = localhost          # PgBouncer address
#
# Django connects to: localhost:6432 (PgBouncer)
# PgBouncer connects to: localhost:5432 (PostgreSQL)
# =============================================================================

# Disable atomic requests for better connection reuse with PgBouncer
ATOMIC_REQUESTS = False

# =============================================================================
# CACHE SETTINGS - Redis Configuration for High Performance
# =============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 100,  # Increased for high concurrency
                'retry_on_timeout': True,
                'socket_keepalive': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,  # Fail gracefully if Redis is down
        },
        'TIMEOUT': 3600,  # 1 hour default timeout
        'KEY_PREFIX': 'django_prod',
        'VERSION': 1,
    }
}

# Session storage using Redis for scalability
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False  # Reduce Redis writes

# =============================================================================
# CELERY SETTINGS - Async Task Processing
# =============================================================================

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Celery performance optimizations for high throughput
CELERY_BROKER_POOL_LIMIT = 50
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Prevent memory leaks
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes soft limit

# =============================================================================
# STATIC FILES - WhiteNoise for serving static files
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# SECURITY SETTINGS - Production Hardening
# =============================================================================

# SSL/HTTPS Settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'

# Security Headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Cookie Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'

# Optional: Set cookie domain for subdomain support
cookie_domain = os.getenv('COOKIE_DOMAIN')
if cookie_domain:
    SESSION_COOKIE_DOMAIN = cookie_domain
    CSRF_COOKIE_DOMAIN = cookie_domain

# CSRF Trusted Origins
csrf_trusted_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS')
if csrf_trusted_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_origins_env.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# =============================================================================
# LOGGING - Production Monitoring
# =============================================================================

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
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('LOG_FILE_PATH', os.path.join(BASE_DIR, 'logs', 'production.log')),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('ERROR_LOG_FILE_PATH', os.path.join(BASE_DIR, 'logs', 'error.log')),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# =============================================================================
# EMAIL SETTINGS - SMTP for Production
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'server@example.com')
EMAIL_TIMEOUT = 10  # Connection timeout

# Admin email notifications
admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
ADMINS = [('Admin', admin_email)]
MANAGERS = ADMINS

# =============================================================================
# FILE UPLOAD SETTINGS
# =============================================================================

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# PERFORMANCE OPTIMIZATIONS
# =============================================================================

# Template caching
if not DEBUG:
    TEMPLATES[0]['APP_DIRS'] = False  # Must be False when using custom loaders
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Disable template debug mode
TEMPLATES[0]['OPTIONS']['debug'] = False

# =============================================================================
# UNFOLD ADMIN - Production Configuration
# =============================================================================

UNFOLD["SITE_TITLE"] = os.getenv('UNFOLD_SITE_TITLE', 'Django Admin')
UNFOLD["SITE_HEADER"] = os.getenv('UNFOLD_SITE_HEADER', 'Django Administration')
UNFOLD["SITE_URL"] = os.getenv('UNFOLD_SITE_URL', '/')

# =============================================================================
# OPTIONAL: SENTRY ERROR TRACKING
# =============================================================================

# Uncomment and configure if using Sentry for error tracking
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# 
# sentry_dsn = os.getenv('SENTRY_DSN')
# if sentry_dsn:
#     sentry_sdk.init(
#         dsn=sentry_dsn,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=False,
#         environment='production',
#     )
