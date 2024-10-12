"""
WSGI config for actors_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

# os.environ["NUMBA_CACHE_DIR"] = "/var/www/actors-app/.tmp"
# os.environ["XDG_DATA_HOME"] = "/var/www/actors-app/.tmp"

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "actors_app.settings_prod")

application = get_wsgi_application()
# call_command("migrate")
