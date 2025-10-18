import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import detector.routing  # <-- make sure this exists

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soilution.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # Enables access to user info in WebSocket
        URLRouter(
            detector.routing.websocket_urlpatterns
        )
    ),
})

