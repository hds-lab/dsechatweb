#!/usr/bin/env python
import os
import sys

from dsechat.libs import env_file

if __name__ == "__main__":
    env_file.load()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsechat.settings.development")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
