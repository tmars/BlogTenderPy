#!/usr/bin/python2.7
import os
import sys
from main import settings

sys.path.insert(0, os.path.join(settings.ROOT_DIR, "private"))
sys.path.insert(0, "/usr/lib64/python2.6/site-packages")

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
