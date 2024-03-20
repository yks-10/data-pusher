"""
ASGI config for datapusher project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datapusher.settings')
django.setup()


from datapusher.consumers import DataHandlerConsumer
application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

application = ProtocolTypeRouter({
    "http": application,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("server/incoming_data/", DataHandlerConsumer.as_asgi()),
        ])
    ),
})


