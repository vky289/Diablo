from django.urls import path
from app.core.views.common_views import DjangoRQDetailView, NotificationDetailsView

app_name = 'core'
urlpatterns = [
    path('queue/get', DjangoRQDetailView.as_view(), name='current_rq_queue'),
    path('notifications/', NotificationDetailsView.as_view(), name='notifications')
]
