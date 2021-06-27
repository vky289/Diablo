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
from rest_framework import routers

from app.authentication.views import UserViewSet, GroupViewSet, PermissionViewSet
from app.dbs.views.api_views import DBInstanceListSet, DBCompareListSet
from app.dbs.views.api_views import DBViewListSet, DBFKListSet, DBSeqListSet, DBTableListSet, DBTableColumnListSet



router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)

router.register(r'dbInstance', DBInstanceListSet)
router.register(r'dbCompare', DBCompareListSet)
router.register(r'dbTable', DBTableListSet)
router.register(r'dbTableColumn', DBTableColumnListSet)
router.register(r'dbvView', DBViewListSet)
router.register(r'dbFK', DBFKListSet)
router.register(r'dbSeq', DBSeqListSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    url('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # Auth routes - login / register
    path("", include("app.authentication.urls"), name="auth"),
    # Apps
    path('', index, name='home'),
    path("", include("app.core.urls"), name='core'),
    path("dbs/", include("app.dbs.urls"), name='dbs'),
    # Rest API's
    path('api/v1/', include((router.urls, 'diablo'), namespace='api')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
