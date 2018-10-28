#!/usr/bin/env python

import sys
import os

from django.core.management import execute_from_command_line

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
execute_from_command_line([sys.argv[0], 'makemigrations'])
