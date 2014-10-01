# -*- coding: utf-8 -*-

import sys
from os import environ
import django
from path import path


# #################################################################
# Application configuration
# #################################################################

# The ID of the current site in the django_site database table.
SITE_ID = 1

# Directories
PROJECT_DIR = path(__file__).abspath().realpath().dirname().parent
PROJECT_NAME = PROJECT_DIR.basename()
SITE_DIR = PROJECT_DIR.parent
APPS_DIR = PROJECT_DIR / 'apps'
LIBS_DIR = PROJECT_DIR / 'libs'

# Append directories to sys.path
sys.path.append(SITE_DIR)
sys.path.append(APPS_DIR)
sys.path.append(LIBS_DIR)

# Root URLs module
ROOT_URLCONF = 'dsechat.urls'

# WSGI application
WSGI_APPLICATION = 'dsechat.wsgi.application'

# Secret key
# This is used to provide cryptographic signing, and should be set
# to a unique, unpredictable value.
SECRET_KEY = 'yoursecretkey'

##################################################################
# Language and timezone settings
##################################################################

# Specifies whether Django’s translation system should be enabled.
USE_I18N = True

# Specifies if localized formatting of data will be enabled by
# default or not.
USE_L10N = True

# Specifies if datetimes will be timezone-aware by default or not.
USE_TZ = True

# A string representing the time zone for this installation.
TIME_ZONE = 'UTC'

# A string representing the language code for this installation.
LANGUAGE_CODE = 'en'

##################################################################
# Authentication settings
##################################################################

# The model to use to represent a User.
AUTH_USER_MODEL = 'accounts.User'

# The URL where requests are redirected for login.
LOGIN_URL = '/accounts/login/'

# The URL where requests are redirected for logout.
LOGOUT_URL = '/accounts/logout/'

# The URL where requests are redirected after login.
LOGIN_REDIRECT_URL = '/accounts/profile/'

##################################################################
# Middleware settings
##################################################################

# The default number of seconds to cache a page when the caching
# middleware or cache_page() decorator is used.
CACHE_MIDDLEWARE_SECONDS = 5

# The cache key prefix that the cache middleware should use.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_NAME + '_'

# A tuple of middleware classes to use.
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

##################################################################
# Static settings
##################################################################

# The absolute path to the directory where collectstatic will
# collect static files for deployment.
STATIC_ROOT = ''

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/'

# Additional locations the staticfiles app will traverse if the
# FileSystemFinder finder is enabled.
STATICFILES_DIRS = (
    PROJECT_DIR / 'static',
)

# The list of finder backends that know how to find static files
# in various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    # other finders...
    'compressor.finders.CompressorFinder',
)

##################################################################
# Compressor settings
##################################################################

COMPRESS_PRECOMPILERS = (
    ('text/less', (SITE_DIR / 'node_modules/.bin/lessc') + ' {infile} {outfile}'),
)

##################################################################
# Templates settings
##################################################################

# List of locations of the template source files.
TEMPLATE_DIRS = (
    PROJECT_DIR / 'templates',
)

# A tuple of template loader classes, specified as strings.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# A tuple of callables that are used to populate the context in
# RequestContext.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth'
)

##################################################################
# Test runner settings
##################################################################

# The name of the class to use for starting the test suite.
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

##################################################################
# Logging settings
##################################################################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "time_formatter": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'time_formatter'
        },
        'error_console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'time_formatter'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


##################################################################
# Installed apps
##################################################################

EXTERNAL_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Other external apps
    'compressor',
    'lineage',
    'registration',
    'bootstrap3',
)

INTERNAL_APPS = (
    # Application specific apps
    'dsechat.apps.web',
    'dsechat.apps.accounts',
)

##################################################################
# Registration settings
##################################################################

# Log the user in immediately after registration
REGISTRATION_AUTO_LOGIN = True

# Is new user registration permitted?
REGISTRATION_OPEN = True


##################################################################
# Site settings
##################################################################

STUDY_CONTACT_NAME = environ.get("STUDY_CONTACT_NAME", 'Study Contact')
STUDY_CONTACT_EMAIL = environ.get("STUDY_CONTACT_EMAIL", 'study@example.com')
SITE_CONTACT_EMAIL = environ.get("SITE_CONTACT_EMAIL", 'info@example.com')
XMPP_SERVER = environ.get("XMPP_SERVER", 'xmpp.example.com')
XMPP_BOSH_URL = environ.get("XMPP_BOSH_URL", '/http-bind/')
XMPP_SERVER_PORT = int(environ.get("XMPP_SERVER_PORT", 5222))
XMPP_MUC_ROOM = environ.get("XMPP_MUC_ROOM", 'Data Science')
XMPP_MUC_SERVER = environ.get("XMPP_MUC_SERVER", 'conference.%s' % XMPP_SERVER)
