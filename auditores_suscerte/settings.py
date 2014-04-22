# -*- coding: UTF8 -*-
"""
Django settings for auditores_suscerte project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

PERIODO_REV_ACREDITACION = 3 # Definido en meses, por defecto 3

LIST_PER_PAGE = 25

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 120
PASSWORD_COMPLEXITY = {
    "UPPER":  1,
    "LOWER":  1,
    "DIGITS": 1,
}

RECAPTCHA_PUBLIC_KEY = '6Ld-Z_ASAAAAAB948Z2NOCG2VKDVPC80ShdNwp10'
RECAPTCHA_PRIVATE_KEY = '6Ld-Z_ASAAAAAN38iuzIo2tH3QPZDiGnrZgMV-7a'
RECAPTCHA_USE_SSL = True

MANAGERS = ('adiaz@suscerte.gob.ve',)

HOST = 'http://localhost:8000'

LOGIN_URL='/login'
LOGIN_REDIRECT_URL = '/perfil/'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import glob
conffiles = glob.glob(os.path.join(os.path.dirname(__file__), 'local_conf', '*.conf'))
conffiles.sort()
for f in conffiles:
        execfile(os.path.abspath(f))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a8g#%2&3y2_u5x12!e4r8&pd8&x#hqxj$%9_w)*jq9(c3dvdoy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost']

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'main/templates').replace('\\','/'),
    os.path.join(os.getcwd(), 'main/templates'),
    os.path.join(os.getcwd(), 'main/templates/admin'),
)

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'debug_toolbar',
    'captcha',
    'axes',
    'passwords',
    'compressor',
    'curriculum',
    'lugares',
    'auth',
    'personas',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'axes.middleware.FailedLoginMiddleware'
)

ROOT_URLCONF = 'auditores_suscerte.urls'

WSGI_APPLICATION = 'auditores_suscerte.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es-ve'

TIME_ZONE = 'America/Caracas'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

MEDIA_URL = '/main/media/'
MEDIA_ROOT =os.path.join(os.getcwd(), 'main/media/')
STATIC_ROOT =os.path.join(os.getcwd(), 'main/static/')
STATIC_URL = '/main/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.getcwd(), 'main/static/public'), 
)

STATICFILES_FINDERS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder',
)
#compresor

COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True

# Customizing Axes
AXES_LOGIN_FAILURE_LIMIT = 6
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = True
