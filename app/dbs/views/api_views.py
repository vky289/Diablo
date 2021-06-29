from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_rq import get_queue

from app.dbs.models import DBInstance, DBCompare, DBObjectCompare, DBObjectFKCompare, DBTableCompare, DBTableColumnCompare
from app.dbs.serializers import DbObjectSerializer, DBFKSerializer
from app.dbs.serializers import DBTableCompareSerializer, DBTableColumnSerializer, DBInstanceSerializer, DBCompareSerializer
from utils.enums import DBObject
from diablo.tasks import compare_db_rows, compare_db_data_types, truncate_table, copy_table_content, compare_db_views, compare_db_seq, \
    compare_db_fk, compare_db_trig, compare_db_ind, delete_instance_n_its_data


class DBInstanceListSet(viewsets.ModelViewSet):
    serializer_class = DBInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBInstance.objects.all()
    http_method_names = ['get', 'post']

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
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db=dst_db)).order_by("table_name")
        else:
            return self.queryset.order_by("table_name")


class DBTableColumnListSet(viewsets.ModelViewSet):
    serializer_class = DBTableColumnSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBTableColumnCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(compare_dbs=compare_db).order_by("table_name", "column_name")
        else:
            return self.queryset.order_by("table_name", "column_name")


class DBViewListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(type=DBObject.VIEW, compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(type=DBObject.VIEW, compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.VIEW).order_by("table_name")


class DBSeqListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(type=DBObject.SEQUENCE, compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(type=DBObject.SEQUENCE, compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.SEQUENCE).order_by("table_name")


class DBTrigListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(type=DBObject.TRIGGER, compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(type=DBObject.TRIGGER, compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.TRIGGER).order_by("table_name")


class DBIndListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(type=DBObject.INDEX, compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(type=DBObject.INDEX, compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.INDEX).order_by("table_name")


class DBFKListSet(viewsets.ModelViewSet):
    serializer_class = DBFKSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectFKCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(compare_dbs=compare_db).order_by("const_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("const_name")
        else:
            return self.queryset.order_by("const_name")


class DBInstanceActionView(generics.RetrieveUpdateAPIView):
    serializer_class = DBInstanceSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = DBTableCompare.objects.all()

    def get(self, request, *args, **kwargs):
        return render(request, "page-405.html", status=405)

    def pre_save(self, request, *args, **kwargs):
        pass

    def put(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        action = self.kwargs.get('action')
        if action == 'delete':
            delete_instance_n_its_data.delay(id)
            return JsonResponse(data={'SuccessMessage': 'Delete initiated!!'})


class DBTableActionView(generics.RetrieveUpdateAPIView):
    serializer_class = DBTableCompareSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = DBTableCompare.objects.all()

    def get(self, request, *args, **kwargs):
        return render(request, "page-405.html", status=405)

    def pre_save(self, request, *args, **kwargs):
        pass

    def cant_be_empty(self, key, value):
        if value is None or len(value) == 0:
            raise ValidationError(
                {key: key + " - Missing input."}
            )

    def put(self, request, *args, **kwargs):
        src_id = self.request.query_params.get('src_id')
        dst_id = self.request.query_params.get('dst_id')
        table_name = self.request.query_params.get('table_name')
        row_count = self.request.query_params.get('row_count')
        unparsed_data = self.request.data.get('unparsed_value')

        self.cant_be_empty('dst_id', dst_id)
        action = self.kwargs.get('action')
        if action == 'compare':
            self.cant_be_empty('src_id', src_id)

            try:
                src_db = DBInstance.objects.get(id=src_id)
                dst_db = DBInstance.objects.get(id=dst_id)
            except DBInstance.DoesNotExist:
                return HttpResponseBadRequest
            compare_db = None
            try:
                ob = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)
                compare_db = ob
            except DBCompare.DoesNotExist:
                compare_db = DBCompare()
                compare_db.src_db = src_db
                compare_db.dst_db = dst_db
                compare_db.save()
            queue = get_queue('high')
            row_compare = queue.enqueue(compare_db_rows, args=(request.user, src_db, dst_db, compare_db))
            queue.enqueue(compare_db_data_types, args=(request.user, src_db, dst_db, compare_db), depends_on=row_compare)

            queue = get_queue('low')
            queue.enqueue(compare_db_views, args=(request.user, src_db, dst_db, compare_db))
            queue.enqueue(compare_db_seq, args=(request.user, src_db, dst_db, compare_db))
            queue.enqueue(compare_db_fk, args=(request.user, src_db, dst_db, compare_db))
            queue.enqueue(compare_db_ind, args=(request.user, src_db, dst_db, compare_db))
            queue.enqueue(compare_db_trig, args=(request.user, src_db, dst_db, compare_db))
            return JsonResponse(data={'SuccessMessage': 'DB table row comparisons started!'})

        elif action == 'bulkImport':
            self.cant_be_empty('src_id', src_id)
            b_tables = self.request.query_params.get('bulk_tables')
            self.cant_be_empty('b_tables', b_tables)
            bulk_tables = b_tables.split(',')
            try:
                src_db = DBInstance.objects.get(id=src_id)
                dst_db = DBInstance.objects.get(id=dst_id)
            except DBInstance.DoesNotExist:
                return HttpResponseBadRequest
            for each_table in bulk_tables:
                val_rows = each_table.split('(')
                table_name = val_rows[0]
                row_count = val_rows[1][0:len(val_rows[1])-1]
                batch_size = 100000
                for upper_bound in range(0, int(row_count), batch_size):
                    copy_table_content.delay(request.user, src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, False)
            return JsonResponse(data={'SuccessMessage': 'Bulk copy initiated! for the DB table {}'.format(b_tables)})
        elif action == 'copy':
            self.cant_be_empty('src_id', src_id)
            self.cant_be_empty('table_name', table_name)
            self.cant_be_empty('row_count', row_count)
            try:
                src_db = DBInstance.objects.get(id=src_id)
                dst_db = DBInstance.objects.get(id=dst_id)
            except DBInstance.DoesNotExist:
                return HttpResponseBadRequest
            batch_size = 100000
            for upper_bound in range(0, int(row_count), batch_size):
                copy_table_content.delay(request.user, src_db, dst_db, table_name,
                                         upper_bound + batch_size - 1, upper_bound, False)
            return JsonResponse(data={'SuccessMessage': 'Copy initiated for the DB table {}'.format(table_name)})
        elif action == 'truncate':
            self.cant_be_empty('table_name', table_name)
            try:
                dst_db = DBInstance.objects.get(id=dst_id)
            except DBInstance.DoesNotExist:
                return HttpResponseBadRequest
            truncate_table.delay(request.user, dst_db, table_name)
            return JsonResponse(data={'SuccessMessage': 'Truncate initiated for the DB table {}'.format(table_name)})
