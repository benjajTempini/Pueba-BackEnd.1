from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# ----------------------
# Cargar variables de entorno
# ----------------------
load_dotenv()

# ----------------------
# Rutas base
# ----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# Seguridad
# ----------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-secret')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1"
]

# ----------------------
# Apps instaladas
# ----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',
    'ventasbasico',
]

# ----------------------
# Middleware
# ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ventasbasico.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ventasbasico.wsgi.application'

# ----------------------
# Base de datos Supabase
# ----------------------
# Si DATABASE_URL no está en .env, usar variables individuales
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Forzar puerto 6543 y sslmode=require si no están
    if '?sslmode=' not in DATABASE_URL:
        DATABASE_URL += '?sslmode=require'
    if ':' not in DATABASE_URL.split('@')[1]:
        # Añadir puerto 6543 si no está
        parts = DATABASE_URL.split('@')
        host_db = parts[1].split('/')
        DATABASE_URL = f"{parts[0]}@{host_db[0]}:6543/{host_db[1]}?sslmode=require"

    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    # Variables individuales como fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('NAME'),
            'USER': os.getenv('USER'),
            'PASSWORD': os.getenv('PASSWORD'),
            'HOST': os.getenv('HOST'),
            'PORT': os.getenv('DB_PORT', '6543'),
        }
    }

# ----------------------
# Validación de contraseñas
# ----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------
# Internacionalización
# ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------
# Archivos estáticos
# ----------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ----------------------
# Predeterminado para claves primarias
# ----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------
# Logging
# ----------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ----------------------
# Seguridad adicional en producción
# ----------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
