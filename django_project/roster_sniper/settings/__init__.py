"""
Settings are imported as follows:
    __init__ -> local (optional) -> development/production -> base

This lets the local settings file modify settings specified in the development,
production, or base settings file. It also lets the development or production
settings files modify settings specified in the base settings file. For example,
development.py can include

>>> INSTALLED_APPS += 'some_debug_app'

because the INSTALLED_APPS list is defined in base.py. In addition to the
previous statement, local.py can also include

>>> DATABASES['default']['PASSWORD'] = 'some_password'

because the DATABASES dictionary is defined in development.py/production.py.

For more information about Django settings, check out the following links
General information:   https://docs.djangoproject.com/en/stable/topics/settings/
List of all settings:  https://docs.djangoproject.com/en/stable/ref/settings/
"""

import os


try:
	from .local import *

# Defaults to development mode if local.py and environment variable don't exist
except ImportError:
	if os.environ.get('RS_ENVIRONMENT') == 'production':
		from .production import *
	else:
		from .development import *
