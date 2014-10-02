# Configuration for gunicorn

import os, sys
# import multiprocessing

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from dsechat.libs import env_file
env_file.load()

bind = "%(ip)s:%(port)s" % {
    'port': os.environ.get('PORT', '8000'),
    'ip': os.environ.get('WEB_BIND_IP', '127.0.0.1')
}

from django.conf import settings
# workers = multiprocessing.cpu_count() * 2 + 1
workers = os.environ.get("GUNICORN_WORKERS", 1)
accesslog = settings.SITE_DIR / 'local' / 'gunicorn.access.log'
errorlog = settings.SITE_DIR / 'local' / 'gunicorn.error.log'
