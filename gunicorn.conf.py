# Configuration for gunicorn
# This file will be interpolated by django-supervisor using the Django template engine

import os, sys
# import multiprocessing

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from dsechat.libs import env_file
env_file.load()

bind = "127.0.0.1:%(port)s" % { 'port': os.environ.get('PORT') }

# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1
