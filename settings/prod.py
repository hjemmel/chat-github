# ``settings_prod.py``
from settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('RDS_DB_NAME'),
        'USER': os.environ.get('RDS_USERNAME'),
        'PASSWORD': os.environ.get('RDS_PASSWORD'),
        'HOST': os.environ.get('RDS_HOSTNAME'),
        'PORT': os.environ.get('RDS_PORT'),
    }
}

GITHUB_APP_ID = ''
GITHUB_API_SECRET = ''

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.contrib.github.GithubBackend',
)
