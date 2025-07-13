import os

import dotenv

dotenv.load_dotenv()
from datetime import timedelta
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-%hjisw!0c0)bs&s9m#0e(#(=g54-#f+q2-d3+p%puk)0=5qrp#"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "api",
    "rest_framework",
    "silk",
    "drf_spectacular",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
]

ROOT_URLCONF = "products.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "products.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "api.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],  # This ia a Generic Filtering, it applies to all the views (It could also be used at the individual view level)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # To throttle the requests for anonymous users
        # "rest_framework.throttling.UserRateThrottle", # To throttle the requests for authenticated users
        # "api.throttles.BurstRateThrottle", # To throttle the requests for burst (UserRateThrottle)
        # "api.throttles.SustainedRateThrottle", # To throttle the requests for sustained (UserRateThrottle)
        "rest_framework.throttling.ScopedRateThrottle", # To throttle the requests for scoped (UserRateThrottle)
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "2/minute",  # 2 requests per minute for anonymous users
        # "user": "4/minute", # 4 requests per minute for authenticated users
        # "burst": "10/minute",  # 10 requests per minute for burst (UserRateThrottle)
        # "sustained": "15/hour",  # 15 requests per hour for sustained (UserRateThrottle)
        "products": "2/minute",  # 2 requests per minute for products
        "orders": "4/minute",  # 4 requests per minute for orders
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Products API",
    "DESCRIPTION": "API for products",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # 1 hour access token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # 7 days refresh token
    # "ROTATE_REFRESH_TOKENS": False,  # Set True if you want refresh tokens to change on use
    # "BLACKLIST_AFTER_ROTATION": False,  # Use with token blacklisting (optional)
    # "ALGORITHM": "HS256",  # Algorithm to use for signing the tokens
    # "SIGNING_KEY": SECRET_KEY,  # Use your Django SECRET_KEY
    # "AUTH_HEADER_TYPES": ("Bearer",),  # Accept Authorization: Bearer <token>
}
