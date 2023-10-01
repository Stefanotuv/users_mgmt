"""
Django settings for users_mgmt project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
import dotenv
import certifi

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Add .env variables anywhere before SECRET_KEY
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# Quick-start development  development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# this has to be added to ensure the collection static works
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'crispy_forms',
    'bootstrap4',
    'crispy_bootstrap4',
    # added to create user and profile
    'allauth',
    'allauth.account',
    'django.contrib.sites',
    'users.apps.UsersConfig',
    'connect_mgmt',
    'camera',
    'face_recognition_app',


    # api
    'rest_framework'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "users_mgmt.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, 'templates'),
            # os.path.join(BASE_DIR, 'connect_mgmt/templates'),
        ]
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],

        },
    },
]

WSGI_APPLICATION = "users_mgmt.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# added to use the custom user model
AUTH_USER_MODEL = 'users.User'
SITE_ID = 1
LOGIN_REDIRECT_URL = 'users_profile'
LOGIN_URL = 'users_login'

MEDIA_URL = '/users/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'users','media') # MEDIA_ROOT = BASE_DIR
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'users/static'),
    os.path.join(BASE_DIR, 'users/media'),
    os.path.join(BASE_DIR, 'connect_mgmt/static'),
    os.path.join(BASE_DIR, 'connect_mgmt/media'),
    os.path.join(BASE_DIR, 'camera/static'),
    os.path.join(BASE_DIR, 'camera/media'),
)

# for email
EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']
# EMAIL_USE_SSL = False
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = os.environ['EMAIL_PORT']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
# https://medium.com/@ste.tuveri/chatgpt-helped-with-django-email-from-google-certificate-error-ssl-certificate-verify-failed-771c560c1009
os.environ['SSL_CERT_FILE'] = certifi.where()

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
REST_FRAMEWORK = {
    # ...
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # ...
}
# for crispy form
CRISPY_TEMPLATE_PACK = 'bootstrap4'