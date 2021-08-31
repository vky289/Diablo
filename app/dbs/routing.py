from django.urls import path
from .consumer import JobUpdateConsumer

ws_url_patterns = [
    path("ws/ticks/", JobUpdateConsumer.as_asgi())
]
