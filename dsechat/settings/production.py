from common import *
from os import environ

# Below are things we might need to deal with later
########## EMAIL CONFIGURATION
########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SITE_DIR + '/db/development.sqlite'
    },

    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': SITE_DIR + '/db/testing.sqlite'
    }
}

########## CACHE CONFIGURATION
########## STORAGE CONFIGURATION

########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = environ.get('SECRET_KEY', SECRET_KEY)
########## END SECRET CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
# Just to make totally sure...
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION

########## COMPRESSION CONFIGURATION
# See: http://django_compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = True
########## END COMPRESSION CONFIGURATION

# The hosts that we are allowed to serve as
ALLOWED_HOSTS = environ.get("ALLOWED_HOSTS", 'localhost').split(',')
