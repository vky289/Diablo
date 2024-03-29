"""
Django settings for diablo project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTION = True

env = environ.Env()
env_file = os.path.join(BASE_DIR, 'config', '.env')
environ.Env.read_env(env_file=env_file)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = env.str("SECRET_KEY")
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'easyaudit',
    "django_rq",
    'notifications',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'channels',

    #inner app
    'app',
    'app.dbs.apps.DbsConfig',
    'app.core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
]

ROOT_URLCONF = 'diablo.urls'
LOGIN_REDIRECT_URL = "/"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "/"  # Route defined in app/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "core/templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.filesystem.Loader',
            ]
        },
    },
]

WSGI_APPLICATION = 'diablo.wsgi.application'

ASGI_APPLICATION = 'diablo.asgi.application'

CELERY_BROKER_URL = 'redis://' + env.str('REDIS_HOST') + ':' + str(env.int('REDIS_PORT'))

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': env.db()
}

RQ_QUEUES = {
    "default": {"HOST": env.str('REDIS_HOST'), "PORT": env.int('REDIS_PORT'), "DB": 0, "DEFAULT_TIMEOUT": 3600, },
    "high": {"HOST": env.str('REDIS_HOST'), "PORT": env.int('REDIS_PORT'), "DB": 0, "DEFAULT_TIMEOUT": 3600, },
    "low": {"HOST": env.str('REDIS_HOST'), "PORT": env.int('REDIS_PORT'), "DB": 0, "DEFAULT_TIMEOUT": 3600, },
    "scheduler": {"HOST": env.str('REDIS_HOST'), "PORT": env.int('REDIS_PORT'), "DB": 0, "DEFAULT_TIMEOUT": 3600, },
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        #'BACKEND': 'asgi_redis.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(env.str('REDIS_HOST'), env.int('REDIS_PORT'))],
            "channel_capacity": {
                "http.request": 200,
                "http.response!*": 10,
                # re.compile(r"^websocket.send\!.+"): 20,
            },
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


LOG_LEVEL = env.str('LOG_LEVEL', default='INFO')
LOG_FILE = env.str('LOG_FILE', default='./logs.log')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': f'{LOG_LEVEL}',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': f'{LOG_LEVEL}',
            'class': 'logging.FileHandler',
            'filename': f'{LOG_FILE}',
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'core/static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

# LOGIN_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_NOTIFICATIONS_CONFIG = {
    'SOFT_DELETE': True,
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'PAGE_SIZE': 5000
}
