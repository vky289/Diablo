# -*- encoding: utf-8 -*-
from app.dbs.views.common_views import DbInstanceDetailView, DbCompareDetailView
from app.dbs.views.common_views import DbInstanceEditView, DbCompareResultView, DBCompareDataTypeResultView, DBCompareDataResultView
from django.urls import path

app_name = 'dbs'
urlpatterns = [
    # path('db_instance_add', DbInstanceActionView.as_view(), name='db_instance_add'),
    path('view/', DbInstanceDetailView.as_view(), name='db_details'),
    path('edit/<int:pk>', DbInstanceEditView.as_view(), name='db_edit_details'),
    path('', DbCompareDetailView.as_view(), name='compare_db'),
    path('compare/', DbCompareDetailView.as_view(), name='compare_db'),
    path('compare/<int:id1>/<int:id2>/', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/<int:id1>/<int:id2>/compare/', DbCompareResultView.as_view(), name='compare_dbs'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/', DBCompareDataTypeResultView.as_view(), name='compare_data_types'),
    path('compareD/<int:id1>/<int:id2>/<str:table_name>/', DBCompareDataResultView.as_view(), name='compare_data'),
    path('compare/<int:id1>/<int:id2>/<str:table_name>/<int:row_count>', DbCompareResultView.as_view(), name='compare_db_results'),
    path('compare/dbs/', DbCompareResultView.as_view(), name='compare_db_res'),
]
