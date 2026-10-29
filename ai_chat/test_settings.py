import os
os.environ.setdefault('SECRET_KEY', 'isolated-tests-not-a-deployment-key')
from setup.settings import *  # noqa: F401,F403
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
LMSTUDIO_CHAT_MODEL = 'test-model'
