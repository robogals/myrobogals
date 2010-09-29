DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Mark Parncutt', 'mark@robogals.org'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'myrobogals'
DATABASE_USER = 'myrobogals'
DATABASE_PASSWORD = 'myrobogals'
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'Etc/UTC'

LANGUAGES = (
	('en', 'English'),
	#('nl', 'Dutch'),
	#('ja', 'Japanese'),
)

LANGUAGE_CODE = 'en'

SITE_ID = 1

USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/home/myrobogals/robogals/rgmedia'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'https://media.my.robogals.org'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'https://media.my.robogals.org/admin/'

# Directory for uploaded profile images
PROFILE_IMAGE_UPLOAD_DIR = 'profilepics/'

# Maximum size for uploaded images in kilobytes
PROFILE_IMAGE_MAX_SIZE = 512

# The default profile image for users who haven't uploaded one yet
PROFILE_IMAGE_DEFAULT = 'profilepics/default.png'

SECRET_KEY = 'kl;h45yrfgu;y;08op2534mj23kjjljk4ilk'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'myrobogals.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'myrobogals.urls'
LOGIN_URL = '/login/'

TEMPLATE_DIRS = (
    '/var/home/myrobogals/robogals/rgtemplates',
)

INSTALLED_APPS = (
    'myrobogals.auth',
    'myrobogals.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'myrobogals.rgprofile',
    'myrobogals.rgchapter',
    'myrobogals.rgteaching',
    'myrobogals.rgmessages',
)
