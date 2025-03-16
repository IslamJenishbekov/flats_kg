# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import chats.routing  # Укажите путь к вашему файлу routing.py
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # Обычные HTTP-запросы
#     "websocket": AuthMiddlewareStack(  # WebSocket-соединения
#         URLRouter(
#             chats.routing.websocket_urlpatterns
#         )
#     ),
# })