
from dotenv import load_dotenv
import os
import ldap
from django_auth_ldap.config import LDAPSearch, ActiveDirectoryGroupType
import logging


logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


load_dotenv()


# ============================================
# Configurações gerais
# ============================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates/')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'captcha',
    'authenticate',
    'ginstech',
    'chatbot'
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

ROOT_URLCONF = 'ginstech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ginstech.context_processors.grupos_do_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'ginstech.wsgi.application'


# ============================================
# Configuração de Banco de Dados
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# ============================================
# Configuração de Autenticação via LDAP
# ============================================

ldap.set_option(ldap.OPT_REFERRALS, 0)  # DESABILITA REFERRALS
ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)  # Usa LDAPv3

AUTH_LDAP_CONNECTION_OPTIONS = {ldap.OPT_REFERRALS: 0}
AUTH_LDAP_SERVER_URI = os.environ.get('LDAP_SERVER_URI', 'ldap://dc.seudominio.local')
AUTH_LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'usuario@seudominio.local')
AUTH_LDAP_BIND_PASSWORD = os.environ.get('LDAP_BIND_PASSWORD', 'senha123')

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.environ.get('LDAP_BASE_DN'),
    ldap.SCOPE_SUBTREE,
    os.environ.get('LDAP_USER_FILTER')
)

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_MIRROR_GROUPS = True
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    os.environ.get('LDAP_GROUP_DN'),
    ldap.SCOPE_SUBTREE,
    os.environ.get('LDAP_GROUP_FILTER')
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend'
)


# ============================================
# Configurações de senha
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================
# Internacionalização
# ============================================

LANGUAGE_CODE = 'PT-BR'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ============================================
# Arquivos estáticos
# ============================================

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
MEDIA_URL = '/media/'


# ============================================
# Outros
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gustavoinunes@hotmail.com'
EMAIL_HOST_PASSWORD = ''

ROLEPERMISSIONS_MODULE = "permissoes.roles"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400
