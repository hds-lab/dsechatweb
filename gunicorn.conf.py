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

# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1

accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '/var/log/dsechatweb.gunicorn.access.log')
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '/var/log/dsechatweb.gunicorn.error.log')
