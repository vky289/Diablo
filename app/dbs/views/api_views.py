import os

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_rq import get_queue

from app.dbs.models import DBInstance, DBCompare, DBObjectCompare, DBObjectFKCompare, DBTableCompare, DBTableColumnCompare, DBCompareDBResults, DBTableCompareTokens
from app.dbs.serializers import DbObjectSerializer, DBFKSerializer
from app.dbs.serializers import DBTableCompareSerializer, DBTableColumnSerializer, DBInstanceSerializer, DBCompareSerializer
from utils.enums import DBObject, DbType
from utils.db_connection import postgres_db, oracle_db
from diablo.tasks import compare_db_rows, compare_db_data_types, truncate_table, copy_table_content, compare_db_views, compare_db_seq, \
    compare_db_fk, compare_db_trig, compare_db_ind, delete_instance_n_its_data, compare_db_for_geom_module_id, compare_db_tables_fk_ui, compare_db_proc
from utils.compare_data import comparator
from app.core.models import SYSetting
from app.dbs.tasks import real_table_data_compare

from django.utils.encoding import smart_str
from django.http import FileResponse
from django.core.signals import request_finished
from pytz import timezone
from datetime import datetime, timedelta

central = timezone('US/Central')


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
        return self.queryset.order_by("src_db", "dst_db", "-last_compared")


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


class DBProcListSet(viewsets.ModelViewSet):
    serializer_class = DbObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DBObjectCompare.objects.all()
    http_method_names = ['get', ]

    def get_queryset(self):
        src_db = self.request.query_params.get('src_db')
        dst_db = self.request.query_params.get('dst_db')
        compare_db = self.request.query_params.get('compare_db')
        if compare_db is not None:
            return self.queryset.filter(type=DBObject.PROCEDURE, compare_dbs=compare_db).order_by("table_name")
        elif src_db is not None and dst_db is not None:
            return self.queryset.filter(type=DBObject.PROCEDURE, compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db = dst_db)).order_by("table_name")
        else:
            return self.queryset.filter(type=DBObject.PROCEDURE).order_by("table_name")

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
        elif action == 'pingDB':
            result = None
            status = -1
            obj = DBInstance
            obj.host = self.request.data.get('host')
            obj.port = self.request.data.get('port')
            obj.username = self.request.data.get('username')
            obj.password = self.request.data.get('password')
            obj.sid = self.request.data.get('sid')
            obj.service = self.request.data.get('service')
            if self.request.data.get('type') == DbType.ORACLE:
                result, status = oracle_db(obj).ping_db()
            if self.request.data.get('type') == DbType.POSTGRES:
                result, status = postgres_db(obj).ping_db()
            if result is not None and status == 0:
                data = {'SuccessMessage': 'Succeeded! ' + str(result)}
            else:
                data = {'errorMessage': 'Failed! ' + str(result)}
            return JsonResponse(data)


class TableResultDownload(generics.RetrieveUpdateAPIView):
    serializer_class = DBTableCompareSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = DBTableCompare.objects.all()

    def get(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        if token is not None:
            try:
                file_for_token = DBTableCompareTokens.objects.get(token=token)

                t_file = open(file_for_token.file_path, 'rb')
                new_file_name = file_for_token.file_path.split('/')[-1]
                response = FileResponse(t_file)
                response['Content-Length'] = t_file.tell()
                response['Content-type'] = 'application/octet-stream'
                response['Content-Disposition'] = f'attachment; filename=%s' % smart_str(new_file_name)
                return response
            except DBTableCompareTokens.DoesNotExist:
                pass

        return JsonResponse(data={'SuccessMessage': 'Not found'})


class DBTableActionView(generics.RetrieveUpdateAPIView):
    serializer_class = DBTableCompareSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = DBTableCompare.objects.all()

    def get(self, request, *args, **kwargs):
        deferred = False
        src_id = self.request.query_params.get('src_id')
        dst_id = self.request.query_params.get('dst_id')
        table_name = self.request.query_params.get('table_name')
        compare_list = self.request.query_params.get('compare_list')
        compare_lis = None
        if compare_list is not None or compare_list == '':
            compare_lis = compare_list.split(',')
            if len(compare_lis) == 1:
                compare_lis = compare_lis[0]
            else:
                compare_lis = set(compare_lis)

        action = self.kwargs.get('action')
        if action == 'compareRawData':
            try:
                self.cant_be_empty('src_id', src_id)
                self.cant_be_empty('table_name', table_name)
                self.cant_be_empty('dst_id', dst_id)
                try:
                    src_db = DBInstance.objects.get(id=src_id)
                    dst_db = DBInstance.objects.get(id=dst_id)
                except DBInstance.DoesNotExist:
                    return HttpResponseBadRequest
                try:
                    com_db = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)
                    table_compare_record = DBTableCompare.objects.get(compare_dbs=com_db, table_name=table_name)
                    table_row_count = table_compare_record.src_row_count
                    table_compare_max = 100000

                    try:
                        cols = SYSetting.objects.get(name="COL_COMPARE_MAX")
                        table_compare_max = cols.value
                        table_compare_max = int(table_compare_max)
                    except SYSetting.DoesNotExist:
                        pass

                    if table_row_count >= int(table_compare_max):
                        deferred = True
                except DBCompare.DoesNotExist:
                    return JsonResponse(data={'SuccessMessage': 'Can\'t find db compare reference'}, status=501)

                tfile = None
                try:
                    if not deferred:
                        tfile, new_file_name = comparator(request.user, src_db=src_db, dst_db=dst_db,
                                                          compare_db=com_db). \
                            compare_data(table_name=table_name, pk_col=compare_lis, table_row_count=table_row_count)

                        obj = DBTableCompare.objects.get(compare_dbs=DBCompare.objects.get(src_db=src_db, dst_db=dst_db), table_name=table_name)
                        if obj.last_compared_file_loc is not None:
                            os.remove(obj.last_compared_file_loc)
                        obj.last_compared_file_loc = tfile.name
                        obj.save()

                        response = FileResponse(open(tfile.name, 'rb'))
                        response['Content-Length'] = tfile.tell()
                        response['Content-type'] = 'application/octet-stream'
                        response['Content-Disposition'] = f'attachment; filename=%s' % smart_str(new_file_name + '.json')
                        return response
                    else:
                        real_table_data_compare.delay(request.user, src_db=src_db, dst_db=dst_db,
                                                      com_db=com_db, table_name=table_name, compare_list=compare_lis, table_row_count=table_row_count)
                        return JsonResponse(data={'SuccessMessage': 'Process started, check back in Notification section'}, status=400)
                except RuntimeError as e:
                    return JsonResponse(data={'SuccessMessage': str(e)}, status=501)
                finally:
                    if tfile is not None and request_finished:
                        os.remove(tfile.name)

                return JsonResponse(data={'SuccessMessage': 'Something went wrong'}, status=200)
            except ValidationError as e:
                return JsonResponse(data={'SuccessMessage': e.args[0]}, status=400)
        return render(request, "page-405.html", status=405)

    def pre_save(self, request, *args, **kwargs):
        pass

    def cant_be_empty(self, key, value):
        if value is None or len(value) == 0 or value == 'undefined':
            raise ValidationError(
                key + " - Missing input."
            )

    def record_compare_start(self, compare_db, func_name):
        try:
            com = DBCompareDBResults.objects.get(compare_dbs=compare_db, func_call=func_name)
            last_comp = (datetime.now(central) - com.last_compared)
            delta_limit_5 = (timedelta(seconds=60))
            if com.status == 0 and last_comp < delta_limit_5:
                return JsonResponse(data={'SuccessMessage': 'Try again in 5 min! There is already a background process comparing the same DB!'})
            else:
                com.status = 0
                com.last_compared = datetime.now(central)
                com.func_call = func_name
                com.save()
        except DBCompareDBResults.DoesNotExist:
            com = DBCompareDBResults()
            com.compare_dbs = compare_db
            com.func_call = func_name
            com.last_compared = datetime.now(central)
            com.status = 0
            com.save()

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
            args = (request.user, src_db, dst_db, compare_db)

            queue_high = get_queue('high')
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_rows.__name__)
            queue_high.enqueue(compare_db_rows, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_data_types.__name__)
            data_type_compare = queue_high.enqueue(compare_db_data_types, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_for_geom_module_id.__name__)
            queue_high.enqueue(compare_db_for_geom_module_id, args=args, depends_on=data_type_compare)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_tables_fk_ui.__name__)
            queue_high.enqueue(compare_db_tables_fk_ui, args=args, depends_on=data_type_compare)

            queue_low = get_queue('low')
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_views.__name__)
            queue_low.enqueue(compare_db_views, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_seq.__name__)
            queue_low.enqueue(compare_db_seq, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_fk.__name__)
            queue_low.enqueue(compare_db_fk, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_trig.__name__)
            queue_low.enqueue(compare_db_trig, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_ind.__name__)
            queue_low.enqueue(compare_db_ind, args=args)
            self.record_compare_start(compare_db=compare_db, func_name=compare_db_proc.__name__)
            queue_low.enqueue(compare_db_proc, args=args)


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
                    copy_table_content.delay(request.user, src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, 10000, False)
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
                                         upper_bound + batch_size - 1, upper_bound, True)
            return JsonResponse(data={'SuccessMessage': 'Copy initiated for the DB table {}'.format(table_name)})
        elif action == 'truncate':
            self.cant_be_empty('table_name', table_name)
            try:
                dst_db = DBInstance.objects.get(id=dst_id)
            except DBInstance.DoesNotExist:
                return HttpResponseBadRequest
            truncate_table.delay(request.user, dst_db, table_name)
            return JsonResponse(data={'SuccessMessage': 'Truncate initiated for the DB table {}'.format(table_name)})
