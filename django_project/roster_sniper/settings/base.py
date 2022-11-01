"""
The base settings file is meant to be imported by the dev/prod settings files.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
INSTALLED_APPS = [
	# stackoverflow.com/a/34214067
	'core.apps.RSConfig',
	'users.apps.UsersConfig',

	'crispy_forms',

	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'roster_sniper.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'roster_sniper.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

# Where collectstatic files are placed
STATIC_ROOT = BASE_DIR / 'static'
# URL that static files are served from
STATIC_URL = '/static/'

# Where user-uploaded files go (via FileField or ImageField) (not currently used)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# URL that user-uploaded files are served from
# MEDIA_URL = '/media/'

# Named URL pattern where requests are redirected for login when using the login_required() decorator
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

# Email
# Production/development specific settings go in their respective setting modules
# https://docs.djangoproject.com/en/stable/topics/email/
EMAIL_USE_TLS = True

# DEFAULT_FROM_EMAIL - Default email address that regular emails are sent from
# SERVER_EMAIL       - Email address that error messages are sent from
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'RosterSniper <no-reply@rostersniper.com>'

CRISPY_TEMPLATE_PACK = 'bootstrap4'
