import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tic_tac_toe.settings")

application = get_wsgi_application()
