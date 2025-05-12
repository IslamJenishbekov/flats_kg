import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Инициализация Django перед импортом любых модулей, зависящих от settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FlatsKG.settings')
import django

django.setup()  # Инициализируем Django

# Теперь безопасно импортировать модули, зависящие от settings
import chats.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})
