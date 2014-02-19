'''
Django settings for myrobogals project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
'''

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
'''
################################################################################
THIS KEY MUST BE REPLACED AND KEPT HIDDEN IN PRODUCTION.

REMOVE THIS FILE FROM TRACKING ONCE COMPLETE.
################################################################################
'''
SECRET_KEY = 'z)ok$qe^lr(me@tcl0%0o*5xkua6s^7qo2!awyzwtrx2-ji@6='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# ALLOWED_HOSTS is ignored for DEBUG = True
ALLOWED_HOSTS = [
  '.my.robogals.org',   # Standard domain and subdomains
  '.my.robogals.org.',  # + FQDN
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'oauth2_provider',
    'myrg_users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'myrg_core.urls'

WSGI_APPLICATION = 'myrg_core.wsgi.application'


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

LANGUAGE_CODE = 'en-gb'

# These languages are/will be supported by myRobogals.
# Identifiers must use approved ISO 639-1-based language codes and must be
# consistent with localisation folder names in respective applications.
# 
# Languages here are also shared with the languages setting for users.
#
# https://docs.djangoproject.com/en/1.6/ref/settings/#std:setting-LANGUAGES

LANGUAGES = (
    ('en', _('English')),                   # This MUST exist
    #('en-au', _('English (Australian)')),
    #('en-gb', _('English (British)')),
    #('en-us', _('English (American)')),
    ('ja', _('Japanese')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# Custom user model
AUTH_USER_MODEL = 'myrg_users.RobogalsUser'


# Django REST Framework

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard permissions, or allow read-only access for
    #unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    # django-oauth-toolkit requires slightly different set up:
    # https://django-oauth-toolkit.readthedocs.org/en/0.5.0/rest-framework/getting_started.html
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),

}
