from .base import *


DEBUG = False


CORS_ALLOW_HEADERS = [
    'Authorization',
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CSRF_TRUSTED_ORIGINS = [
    'https://qyzmetapp-front.vercel.app',
    'https://qyzmettap.sky-ddns.kz',
    'http://localhost:5173',
    'http://localhost:3000',
]

CORS_ALLOWED_ORIGINS = [
    'https://qyzmetapp-front.vercel.app',
    'http://localhost:5173',
    'http://localhost:3000',
]