from django.urls import include, path
from .views import login_view, register_user, profile_user
from django.contrib.auth.views import LogoutView
from app.core.views.common_views import index

app_name = 'auth'
urlpatterns = [
    path(r'', index, name='home'),
    path(r'login/', login_view, name='login'),
    path(r'register/', register_user, name='register'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    path(r'profile/', profile_user, name='profile'),
]
