from django.urls import re_path
from detector.consumers import InboxConsumer
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/inbox/$", InboxConsumer.as_asgi()),
    re_path(r'ws/logs/$', consumers.LogConsumer.as_asgi()),
]
