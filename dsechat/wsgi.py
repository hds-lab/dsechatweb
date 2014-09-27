"""
WSGI config for dsechat project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import libs.env_file
libs.env_file.load()

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsechat.settings.development")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
