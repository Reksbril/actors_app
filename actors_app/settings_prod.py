from .settings_common import *

from pathlib import Path

DEBUG = False

TMP_WORKDIR = Path("/var/www/actors-app/.tmp")
DATABASE_ROOT = Path("/var/www/actors-app/db")
MEDIA_ROOT = DATABASE_ROOT / "uploads"

DEPS_BINARIES_PATH = Path("/var/www/actors-app/deps")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_ROOT / "db.sqlite3",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": TMP_WORKDIR / "info.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],  # add "console" to print debug logs to console
            "level": "INFO",  # Change this to DEBUG to debug tests easier
            "propagate": True,
        }
    },
}
