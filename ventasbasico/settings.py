"""
Django settings for ventasbasico project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-a!)1(l*2=!gtiys$g6i^4p4d9b%60z^el0v$)0&6%d1nyr&kd#')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG ='True'

ALLOWED_HOSTS = [
    ".railway.app",      # Railway
    ".onrender.com",     # Render (por si volvés a usarlo)
    "127.0.0.1",
    "localhost"
]

# Agregar hostname dinámico de Railway o Render
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')

if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Configuración CSRF para Railway
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "https://*.onrender.com",
]

if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',
    'ventasbasico',
    'rest_framework',
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Railway provee DATABASE_URL automáticamente
#DATABASE_URL = os.getenv('DATABASE_URL')

DATABASES = {
    "default":{
        "ENGINE":"django.db.backends.sqlite3",
        "NAME":"bd.sqlite3",
    }
}


#if DATABASE_URL:
    # Usar DATABASE_URL si existe (Railway/Render)
#    DATABASES = {
#        'default': dj_database_url.parse(
#            DATABASE_URL,
#            conn_max_age=600,
#            conn_health_checks=True,
#            ssl_require=False  # Railway maneja SSL automáticamente
#        )
#    }
#else:
    # Configuración manual para desarrollo local
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.postgresql',
#            'NAME': os.getenv('DB_NAME', 'postgres'),
#            'USER': os.getenv('DB_USER'),
#            'PASSWORD': os.getenv('DB_PASSWORD'),
#            'HOST': os.getenv('DB_HOST'),
#            'PORT': os.getenv('DB_PORT', '6543'),
#            'CONN_MAX_AGE': 600,
#            'OPTIONS': {
#                'connect_timeout': 10,
#                'sslmode': os.getenv('PGSSLMODE', 'prefer'),
#            }
#        }
#    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ Carpetas adicionales donde Django busca archivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Carpeta global
]

# ✅ Configuración diferente para desarrollo y producción
if DEBUG:
    # Desarrollo: usar el sistema simple de Django
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True
else:
    # Producción: usar Whitenoise comprimido
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = False
    WHITENOISE_AUTOREFRESH = False
    WHITENOISE_MANIFEST_STRICT = False

WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: False

# Directories donde Django busca archivos estáticos adicionales
STATICFILES_DIRS = []

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Configuración de seguridad para producción
if not DEBUG:
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Permitir que Railway/Render maneje SSL
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
