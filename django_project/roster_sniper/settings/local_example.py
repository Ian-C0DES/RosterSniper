"""
The local settings file is meant to include passwords or any other setting which
for whatever reason shouldn't be tracked by git. DO NOT specify them here! You
MUST copy this file, rename it to 'local.py', and then change the settings as
you like. The renamed file is in the gitignore and will not be tracked.
"""

DEBUG = True

if DEBUG:
	from .development import *
else:
	from .production import *


## General local settings example ##############################################

# List of people who get error email notifications
# Django only sends them when DEBUG=False however
# core.utils.send_admin_email() will send regardless of DEBUG status
# ADMINS = [('your_name', 'your_email')]


## Development local settings example ##########################################

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'example@gmail.com'
# EMAIL_HOST_PASSWORD = 'some_password'
# EMAIL_PORT = 587

# Custom database or logger..


## Production local settings example ###########################################

"""
The following can be used to generate a new SECRET_KEY
>>> python -c 'from django.core.management import utils; print(utils.get_random_secret_key())'
cm+6y_4_jd^ri3kx##spu3axn*)d-=a6d)ej)@1wwh%z1kj)g@
"""
# SECRET_KEY = 'a_secret_key'

# DATABASES['default']['PASSWORD'] = 'some_password'
