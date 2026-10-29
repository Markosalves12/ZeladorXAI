"""ZeladorX AI: shared models, isolated read-only assistant, local LM Studio."""
import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
def flag(name, default=False):
    return os.getenv(name, str(default)).lower() in ('true', '1', 'yes')
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured('Configure SECRET_KEY com a mesma chave da família ZeladorX.')
DEBUG = flag('DEBUG')
ALLOWED_HOSTS = [v.strip() for v in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if v.strip()]
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'zeladorx', 'empresaprimaria', 'empresasecundario', 'gerente', 'notifications',
    'permissionscontrol', 'settings', 'semana', 'unidade', 'localidade', 'terrenos',
    'vegetacao', 'catalogo_de_servicos', 'areas', 'servicos', 'ai_chat.apps.AiChatConfig',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'setup.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': ['django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'setup.wsgi.application'
ASGI_APPLICATION = 'setup.asgi.application'
DATABASES = {'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=60) if os.getenv('DATABASE_URL') else {
    'ENGINE': 'django.db.backends.postgresql', 'NAME': os.getenv('DB_NAME', 'zeladorx'),
    'USER': os.getenv('DB_USER', 'postgres'), 'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', '127.0.0.1'), 'PORT': os.getenv('DB_PORT', '5432')}}
AUTH_USER_MODEL = 'gerente.Gerente'
# Keep BOTH paths: existing family sessions store the backend's dotted path.
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend', 'gerente.backends.CaseInsensitiveModelBackend']
SESSION_ENGINE = os.getenv('SESSION_ENGINE', 'django.contrib.sessions.backends.db')
SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'sessionid')
SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN') or None
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = flag('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = flag('CSRF_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_NAME = 'zeladorxai_csrftoken'
CSRF_TRUSTED_ORIGINS = [v.strip() for v in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if v.strip()]
SECURE_SSL_REDIRECT = flag('SECURE_SSL_REDIRECT', not DEBUG)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles-ai'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# No Google storage integration is activated in this initial local platform.
# To restore later: configure django-storages, GS_BUCKET_NAME and server credentials.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'no-reply@localhost')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
LMSTUDIO_URL = os.getenv('LMSTUDIO_URL', 'http://127.0.0.1:1234/v1').rstrip('/')
LMSTUDIO_CHAT_MODEL = os.getenv('LMSTUDIO_CHAT_MODEL', '')
LMSTUDIO_EMBED_MODEL = os.getenv('LMSTUDIO_EMBED_MODEL', '')
LMSTUDIO_API_KEY = os.getenv('LMSTUDIO_API_KEY', '')
LMSTUDIO_TIMEOUT = int(os.getenv('LMSTUDIO_TIMEOUT', '180'))
MCP_USER_ID_RANDOM = os.getenv('MCP_USER_ID_RANDOM', '')
