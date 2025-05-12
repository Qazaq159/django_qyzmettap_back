import os
import sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


def rel_to(to, *x):
    return os.path.join(to, *x)


def rel(*x):
    return os.path.join(PROJECT_PATH, *x)


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the %s environment variable' % var_name
        raise ImproperlyConfigured(error_msg)


def get_env_or_default(var_name, default):
    return os.environ.get(var_name, default)


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-rd7&p1fl)9po0_wjdhy!82otw79gyea!=(qkf8ogs$ueeyiqv@'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'web']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'market',
    'corsheaders',
    'orders',
    'subscriptions',
    'payments',
    'chats',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qyzmettap_back.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qyzmettap_back.wsgi.application'
ASGI_APPLICATION = 'qyzmettap_back.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../../media')

DEFAULT_LOGGER_NAME = "qyzmettap_back"
DB_LEVEL = 'ERROR'
DEFAULT_LOGGER_HANDLERS = ['default_file', 'sentry']
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__) + '/..')

WORK_ROOT = rel_to('..', '..',)
LOGS_FOLDER = get_env_or_default('LOGS_FOLDER', rel_to(WORK_ROOT, 'logs'))
LOG_DIR = rel_to(LOGS_FOLDER, 'qyzmettap_back')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },

    'formatters': {
        'general': {
            'format': '%(asctime)s %(levelname)s\t%(message)s',
            # 'datefmt': '%m/%d %H:%M:%S'
        },
        'json': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(process)d %(thread)d\t%(message)s',
            'datefmt': '%m/%d %H:%M:%S'
        }
    },

    'handlers': {
        'gunicorn': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': rel_to(LOG_DIR, 'gunicorn.log'),
            'maxBytes': 1024 * 1024 * 100,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'general'
        },
        'default_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': rel_to(LOG_DIR, 'default.log'),
            'formatter': 'json',
        },
        'db_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': rel_to(LOG_DIR, 'db.log'),
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler'
        }
    },

    'loggers': {
        'django': {
            'handlers': DEFAULT_LOGGER_HANDLERS,
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['sentry'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gunicorn.errors': {
            'handlers': ['gunicorn', 'sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_file', 'sentry'],
            'level': DB_LEVEL,
            'propagate': True,
        },
        'market.views': {
            'handlers': ['console', 'default_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'payments.views': {
            'handlers': ['console', 'default_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'orders.views': {
            'handlers': ['console', 'default_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        DEFAULT_LOGGER_NAME: {
            'handlers': DEFAULT_LOGGER_HANDLERS,
            'level': 'INFO',
            'propagate': True,
        }
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('MASTER_DB_NAME'),
        'USER': os.getenv('MASTER_DB_USER'),
        'PASSWORD': os.getenv('MASTER_DB_PASSWORD'),
        'HOST': os.getenv('MASTER_DB_HOST'),
        'CONN_MAX_AGE': 0,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('REPLICA_DB_NAME'),
        'USER': os.getenv('REPLICA_DB_USER'),
        'PASSWORD': os.getenv('REPLICA_DB_PASSWORD'),
        'HOST': os.getenv('REPLICA_DB_HOST'),
        'CONN_MAX_AGE': 0,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

DATABASE_ROUTERS = ['qyzmettap_back.router.ReplicaRouter']
USE_REPLICA_DATABASE = get_env_or_default('USE_REPLICA_DATABASE', 'false').lower() == 'true'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'to7zhan@gmail.com'
EMAIL_HOST_PASSWORD = 'xsqwlvubqsdncdqo'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

AUTH_USER_MODEL = 'market.UserInstance'

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=72),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')