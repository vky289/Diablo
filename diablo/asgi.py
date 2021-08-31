"""
ASGI config for diablo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from app.dbs.routing import ws_url_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": #AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(ws_url_patterns),
        ),
    #),
})
