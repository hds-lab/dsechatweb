from common import *
from os import environ
import dj_database_url

# Below are things we might need to deal with later
########## EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///%s' % (SITE_DIR / 'db/development.sqlite'))
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
COMPRESS_OFFLINE = True
########## END COMPRESSION CONFIGURATION

# The hosts that we are allowed to serve as
ALLOWED_HOSTS = environ.get("ALLOWED_HOSTS", 'localhost').split(',')

##################################################################
# Gunicorn config
##################################################################

WEB_BIND_IP = environ.get("WEB_BIND_IP", 'localhost')
PORT = int(environ.get("PORT", '8000'))
GUNICORN_CONF = 'gunicorn.conf.py'

##################################################################
# Installed apps
##################################################################

PRODUCTION_APPS = (
    # Production-specific apps here

    'djsupervisor',
)

INSTALLED_APPS = EXTERNAL_APPS + PRODUCTION_APPS + INTERNAL_APPS
