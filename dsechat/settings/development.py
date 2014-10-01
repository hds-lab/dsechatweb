# -*- coding: utf-8 -*-

import logging
from dsechat.settings.common import *


##################################################################
# Debug settings
##################################################################

# Set debug
DEBUG = True
ALLOWED_HOSTS=('localhost',)

# Turns on/off template debug mode.
TEMPLATE_DEBUG = DEBUG

##################################################################
# Email settings
##################################################################

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = SITE_DIR / 'mail'

##################################################################
# Databases settings
##################################################################

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

##################################################################
# Installed apps
##################################################################

DEVELOPMENT_APPS = (
    # Development specific apps here

    # If you're using Django 1.7.x or later
    'debug_toolbar.apps.DebugToolbarConfig',
    'djsupervisor',
)
djsupervisor
INSTALLED_APPS = EXTERNAL_APPS + DEVELOPMENT_APPS + INTERNAL_APPS
