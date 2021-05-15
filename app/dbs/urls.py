# -*- encoding: utf-8 -*-
from app.dbs.views.common_views import DbInstanceDetailView, DbCompareDetailView
from app.dbs.views.common_views import DbInstanceEditView, DbCompareResultView, DBCompareDataTypeResultView

from django.urls import path, re_path

app_name = 'dbs'
urlpatterns = [
    # path('db_instance_add', DbInstanceActionView.as_view(), name='db_instance_add'),
    path('view/', DbInstanceDetailView.as_view(), name='db_details'),
    path('edit/<int:pk>', DbInstanceEditView.as_view(), name='db_edit_details'),
    path('compare/', DbCompareDetailView.as_view(), name='compare_db'),
    path('compare/<int:id1>/<int:id2>/', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/', DBCompareDataTypeResultView.as_view(), name='compare_data_types'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/<int:row_count>', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/dbs/', DbCompareResultView.as_view(), name='compare_db_res'),
]
