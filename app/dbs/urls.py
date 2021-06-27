# -*- encoding: utf-8 -*-
from app.dbs.views.common_views import DbInstanceDetailView, DbCompareDetailView
from app.dbs.views.common_views import DbInstanceEditView, DbCompareResultView, DBCompareDataTypeResultView, DBCompareTableViewResult
from app.dbs.views.api_views import DBInstanceListSet, DBCompareListSet
from app.dbs.views.api_views import DBViewListSet, DBFKListSet, DBSeqListSet, DBTableListSet, DBTableColumnListSet


from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dbInstance', DBInstanceListSet)
router.register(r'dbCompare', DBCompareListSet)
router.register(r'dbTable', DBTableListSet)
router.register(r'dbTableColumn', DBTableColumnListSet)
router.register(r'dbvView', DBViewListSet)
router.register(r'dbFK', DBFKListSet)
router.register(r'dbSeq', DBSeqListSet)

app_name = 'dbs'
urlpatterns = [
    path(r'api/', include((router.urls, 'db'), namespace='dbb')),
    # path('db_instance_add', DbInstanceActionView.as_view(), name='db_instance_add'),
    path('view/', DbInstanceDetailView.as_view(), name='db_details'),
    path('edit/<int:pk>', DbInstanceEditView.as_view(), name='db_edit_details'),
    path('compare/', DbCompareDetailView.as_view(), name='compare_db'),
    path('compare/<int:id1>/<int:id2>/', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/<int:id1>/<int:id2>/cv', DBCompareTableViewResult.as_view(), name='view_results'),
    path('compare/<int:id1>/<int:id2>/compare/', DbCompareResultView.as_view(), name='compare_dbs'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/', DBCompareDataTypeResultView.as_view(), name='compare_data_types'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/<int:row_count>', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/dbs/', DbCompareResultView.as_view(), name='compare_db_res'),
]
