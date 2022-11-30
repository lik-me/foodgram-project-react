import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
    "users",
    "recipes",
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

ROOT_URLCONF = 'apps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
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

WSGI_APPLICATION = 'apps.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432')
    }
}


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


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework.authentication.TokenAuthentication",],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

DJOSER = {
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserRegistrationSerializer',
        'user': 'api.serializers.UserListSerializer',
        'current_user': 'api.serializers.UsersSerializer',
        'token_create': 'api.serializers.UserTokenCreateSerializer',
    },
}

AUTH_USER_MODEL = "users.User"

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ADMIN_EMAIL = "support_api@mail.com"

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

VALIDATION_ERRORS = {
    "FIELD_REQUIRED": "Обязательное поле.",
    "USER_EMAIL_NOT_FOUND": "Пользователь с таким email не найден.",
    "USER_NAME_EMAIL_WRONG": "Имя пользователя и пароль не совпадают. Введите правильные данные.",
    "RECIPE_AMOUNT_WRONG": "Убедитесь, что значение поля 'Количество' для ингридиента больше либо равно 1.",
    "RECIPE_NAME_WRONG": "Убедитесь, что длина поля <= 200 cимволов.",
    "COOKING_TIME_WRONG": "Убедитесь, что значение поля cooking_time >= 1.",
    "USER_ALREADY_SUBSCRIBED": "Вы уже подписаны на этого пользователя.",
    "SELF_SUBSCRIBED": "Нельзя подписаться на самого себя.",
    "USER_SUBSCRIBE_WRONG": "Вы не подписаны на этого пользователя.",
    "RECIPE_ALREADY_IN_SHOPPING_CART": "Рецепт уже есть в списке покупок.",
    "RECIPE_NOT_FOUND_IN_SHOPPING_CART": "В списке покупок рецепт не найден.",
    "RECIPE_ALREADY_IN_FAVORITED": "Рецепт уже есть в избранном.",
    "RECIPE_NOT_FOUND_IN_FAVORITED": "В избранном рецепт не найден!",
}

RECIPES_PER_PAGE = 10
