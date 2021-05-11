# -*- encoding: utf-8 -*-


from django.urls import path
from .views import login_view, register_user, profile_user, notifications
from django.contrib.auth.views import LogoutView

app_name = "auth"
urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_user, name="profile"),
    path("notifications/", notifications, name="notifications")
]
