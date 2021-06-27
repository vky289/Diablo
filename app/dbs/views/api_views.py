from rest_framework import viewsets
from rest_framework import permissions
from app.dbs.models import DBInstance, DBCompare, DBObjectCompare, DBObjectFKCompare, DBTableCompare, DBTableColumnCompare
from app.dbs.serializers import DbObjectSerializer, DBFKSerializer
from app.dbs.serializers import DBTableCompareSerializer, DBTableColumnSerializer, DBInstanceSerializer, DBCompareSerializer
from utils.enums import DBObject


class DBInstanceListSet(viewsets.ModelViewSet):
    serializer_class = DBInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBInstance.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        return self.queryset.order_by("name", "host")


class DBCompareListSet(viewsets.ModelViewSet):
    serializer_class = DBCompareSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        return self.queryset.order_by("src_db", "dst_db")


class DBTableListSet(viewsets.ModelViewSet):
    serializer_class = DBTableCompareSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBTableCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        if self.request.query_params.get('compare_db') is not None:
            return self.queryset.filter(compare_dbs=self.request.query_params.get('compare_db')).order_by("table_name")
        else:
            return self.queryset.order_by("table_name")


class DBTableColumnListSet(viewsets.ModelViewSet):
    serializer_class = DBTableColumnSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBTableColumnCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        if self.request.query_params.get('compare_db') is not None:
            return self.queryset.filter(compare_dbs=self.request.query_params.get('compare_db')).order_by("table_name", "column_name")
        else:
            return self.queryset.order_by("table_name", "column_name")


class DBViewListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        if self.request.query_params.get('compare_db') is not None:
            return self.queryset.filter(type=DBObject.VIEW, compare_dbs=self.request.query_params.get('compare_db')).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.VIEW).order_by("table_name")


class DBSeqListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        if self.request.query_params.get('compare_db') is not None:
            return self.queryset.filter(type=DBObject.SEQUENCE, compare_dbs=self.request.query_params.get('compare_db')).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.SEQUENCE).order_by("table_name")


class DBFKListSet(viewsets.ModelViewSet):
    serializer_class = DBFKSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectFKCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        if self.request.query_params.get('compare_db') is not None:
            return self.queryset.filter(compare_dbs=self.request.query_params.get('compare_db')).order_by("const_name")
        else:
            return self.queryset.order_by("const_name")