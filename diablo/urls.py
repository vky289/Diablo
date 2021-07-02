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
from rest_framework import routers

from app.authentication.views import UserViewSet, GroupViewSet, PermissionViewSet
from app.dbs.views.api_views import DBInstanceListSet, DBCompareListSet, DBTableActionView, DBInstanceActionView
from app.dbs.views.api_views import DBViewListSet, DBFKListSet, DBSeqListSet, DBTrigListSet, DBIndListSet, DBTableListSet, DBTableColumnListSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# for REST API auto binding
router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)

router.register(r'dbInstance', DBInstanceListSet)
router.register(r'dbCompare', DBCompareListSet)
router.register(r'dbTable', DBTableListSet)
router.register(r'dbTableColumn', DBTableColumnListSet)
router.register(r'dbFK', DBFKListSet)
router.register(r'dbView', DBViewListSet, basename='dbView')
router.register(r'dbInd', DBIndListSet, basename='dbInd')
router.register(r'dbSeq', DBSeqListSet, basename='dbSeq')
router.register(r'dbTrig', DBTrigListSet, basename='dbTrig')

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'django-rq/', include('django_rq.urls')),
    # Auth routes - login / register
    path(r'', include('app.authentication.urls'), name='auth'),
    # Apps
    path(r'', include('app.core.urls'), name='core'),
    url(r'inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path(r'dbs/', include('app.dbs.urls'), name='dbs'),
    # Rest API's
    path(r'api/v1/', include((router.urls, 'diablo'), namespace='api')),
    path(r'api/v1/dbInstanceAction/<slug:action>', DBInstanceActionView.as_view(), name="dbInstanceAction"),
    path(r'api/v1/dbTableAction/<slug:action>', DBTableActionView.as_view(), name="dbTableAction"),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

