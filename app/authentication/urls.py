from django.urls import include, path
from .views import login_view, register_user, profile_user, UserViewSet, GroupViewSet, PermissionViewSet
from django.contrib.auth.views import LogoutView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)

app_name = "auth"
urlpatterns = [
    path('api/', include((router.urls, 'ap'), namespace='api')),
    path('accounts/login/', login_view, name="login"),
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", profile_user, name="profile"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
