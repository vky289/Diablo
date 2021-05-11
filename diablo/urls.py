"""diablo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from app.core.views.common_views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('django-rq/', include('django_rq.urls')),
    # Auth routes - login / register
    path("", include("app.authentication.urls"), name="auth"),

    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

    # Apps
    path("", include("app.core.urls"), name='core'),
    path("dbs/", include("app.dbs.urls"), name='dbs'),
    path('django-rq/', include('django_rq.urls')),
]
