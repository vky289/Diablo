from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from diablo.tasks import compare_db_rows, compare_db_data_types, compare_db_tables_fk_ui, \
    compare_db_views, compare_db_seq, compare_db_fk, \
    compare_db_trig, compare_db_ind, compare_db_for_geom_module_id, enable_all_postgre_triggers, disable_all_postgre_triggers, compare_db_proc
from diablo.tasks import truncate_table, copy_table_content
from diablo.tasks import delete_instance_n_its_data
from django.urls import reverse
from django.http import HttpResponseRedirect
from django_rq import get_queue
from utils.compare_database import any_db

from app.dbs.models import DBInstance, DBCompare, DBTableCompare, DBTableColumnCompare, DBCompareDBResults
from utils.enums import DbType, DBSrcDst
from utils.db_connection import oracle_db, postgres_db
from datetime import datetime, timedelta
from pytz import timezone

central = timezone('US/Central')

add_instance = 'dbs.view_dbinstance'


class DbInstanceDetailView(PermissionRequiredMixin, ListView):
    permission_required = add_instance
    model = DBInstance
    template_name = 'view-db.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_instance'] = DBInstance.objects.order_by('-host', 'name')
        context['db_types'] = DbType
        context['segment'] = 'view-db'
        return context

    def create_db_object(self, obj, request):
        obj.host = request.POST.get('host')
        obj.name = request.POST.get('name')
        obj.port = request.POST.get('port')
        obj.username = request.POST.get('username')
        obj.password = request.POST.get('password')
        obj.sid = '' if request.POST.get('sid') is None else request.POST.get('sid')
        obj.service = '' if request.POST.get('service') is None else request.POST.get('service')
        obj.type = request.POST.get('type')
        return obj


    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.user.has_perm('dbs.add_dbinstance'):
                result, status = None, None
                if self.request.POST.get('saveDB'):
                    obj = DBInstance()
                    obj = self.create_db_object(obj, request)
                    if obj.type == DbType.ORACLE:
                        result, status = oracle_db(obj).ping_db()
                    if obj.type == DbType.POSTGRES:
                        result, status = postgres_db(obj).ping_db()
                    if status == 0:
                        obj.save()
                        messages.success(request, f'DB Connections Successfully saved! ' + str(result))
                    else:
                        messages.error(request, f'Check DB Settings! ' + str(result))
                if request.user.has_perm('dbs.change_dbinstance'):
                    if self.request.POST.get('editDB'):
                        obj = DBInstance.objects.get(id=self.request.POST.get('id'))
                        obj = self.create_db_object(obj, request)
                        if obj.type == DbType.ORACLE:
                            result, status = oracle_db(obj).ping_db()
                        if obj.type == DbType.POSTGRES:
                            result, status = postgres_db(obj).ping_db()
                        if status == 0:
                            obj.save()
                            messages.success(request, f'DB Connections Updated saved! ' + str(result))
                        else:
                            messages.error(request, f'Check DB Settings! ' + str(result))
                    if self.request.POST.get('delete'):
                        delete_instance_n_its_data.delay(self.request.POST.get('id'))
                        messages.error(request, f'Delete initiated!!')
                else:
                    messages.success(request, 'You don\'t have permission to modify/delete DB details!!')
            else:
                messages.success(request, 'You don\'t have permission to add DB details!!')
            return HttpResponseRedirect(reverse('dbs:db_details'))


class DbInstanceEditView(PermissionRequiredMixin, ListView):
    permission_required = add_instance
    model = DBInstance
    template_name = 'edit-db.html'

    def get_db_instance_id(self):
        return self.kwargs['pk']

    def get_db_instance(self) -> DBInstance:
        return DBInstance.objects.get(id=self.get_db_instance_id())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_instance'] = DBInstance.objects.get(id=self.get_db_instance_id())
        context['db_types'] = DbType
        return context


class DbCompareDetailView(PermissionRequiredMixin, ListView):
    permission_required = 'dbs.view_dbcompare'
    model = DBInstance
    template_name = 'compare-db.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_instance_or'] = DBInstance.objects.all().order_by('name', 'host')
        #context['db_instance_pg'] = context['db_instance_or']
        #context['db_instance_or'] = DBInstance.objects.filter(type='oracle').order_by('-host', 'name')
        context['db_instance_pg'] = DBInstance.objects.filter(type='postgres').order_by('name', 'host')
        context['segment'] = 'compare-db'
        return context


class DBCompareDataTypeResultView(PermissionRequiredMixin, ListView):
    permission_required = 'dbs.view_dbtablecolumncompare'
    model = DBTableColumnCompare
    template_name = 'compare-data-type.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        src_db = self.kwargs['id1']
        dst_db = self.kwargs['id2']
        table_name = self.kwargs['table_name']
        db_compare = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)

        dist_col_names = DBTableColumnCompare.objects.filter(compare_dbs=db_compare, table_name=table_name).distinct("column_name")
        src_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare, table_name=table_name, type=DBInstance.objects.get(id=src_db).type)
        dst_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare, table_name=table_name, type=DBInstance.objects.get(id=dst_db).type)

        dd = []
        for d_c_n in dist_col_names:
            final_dict = dict()
            dd_1 = d_c_n.column_name
            final_dict['column_name'] = dd_1
            final_dict['ui'] = dd_1
            for src in src_table_col:
                if dd_1 == src.column_name:
                    final_dict['src_data_type'] = src.datatype + '(' + src.precision + ')'
                    final_dict['src_is_ui'] = src.is_ui

            for dst in dst_table_col:
                if dd_1 == dst.column_name:
                    final_dict['dst_data_type'] = dst.datatype + '(' + dst.precision + ')'
                    final_dict['dst_is_ui'] = dst.is_ui
            dd.append(final_dict)
        context['data_type_compare_res'] = dd
        context['table_name'] = table_name
        context['src_db_type'] = DBInstance.objects.get(id=src_db).type
        context['dst_db_type'] = DBInstance.objects.get(id=dst_db).type
        context['segment'] = 'compare-db'
        return context


class DBCompareDataResultView(PermissionRequiredMixin, ListView):
    permission_required = 'dbs.view_dbtablecolumncompare'
    model = DBTableColumnCompare
    template_name = 'compare-data.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        src_db = self.kwargs['id1']
        dst_db = self.kwargs['id2']
        table_name = self.kwargs['table_name']
        if table_name is not None:
            table_name = table_name.upper()
        db_compare = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)

        dist_col_names = DBTableColumnCompare.objects.filter(compare_dbs=db_compare,
                                                             table_name=table_name).distinct("column_name")
        src_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare,
                                                            table_name=table_name,
                                                            type=DBInstance.objects.get(id=src_db).type,
                                                            src_dst=DBSrcDst.SRC)
        dst_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare,
                                                            table_name=table_name,
                                                            type=DBInstance.objects.get(id=dst_db).type,
                                                            src_dst=DBSrcDst.DST)

        dd = []
        for d_c_n in dist_col_names:
            final_dict = dict()
            dd_1 = d_c_n.column_name
            final_dict['column_name'] = dd_1
            final_dict['ui'] = dd_1
            for src in src_table_col:
                if dd_1 == src.column_name:
                    final_dict['src_data_type'] = src.datatype + '(' + src.precision + ')'
                    final_dict['src_is_ui'] = src.is_ui

            for dst in dst_table_col:
                if dd_1 == dst.column_name:
                    final_dict['dst_data_type'] = dst.datatype + '(' + dst.precision + ')'
                    final_dict['dst_is_ui'] = dst.is_ui
            dd.append(final_dict)
        context['data_compare_res'] = dd
        context['id1'] = src_db
        context['id2'] = dst_db
        context['table_name'] = table_name
        context['src_db_type'] = DBInstance.objects.get(id=src_db).type
        context['dst_db_type'] = DBInstance.objects.get(id=dst_db).type
        context['segment'] = 'compare-db'
        return context

    # def post(self, request, *args, **kwargs):
    #     if request.method == 'POST':
    #         src_db, dst_db, compare_db = get_src_db_dst_db_with_compare_db(request, self.kwargs)
    #         if self.request.POST.get('compareData'):
    #             compare_list = self.request.POST.getlist('compare_list')
    #         return HttpResponseRedirect(reverse('dbs:compare_db_results', kwargs={'id1': src_db.id, 'id2': dst_db.id}))


def get_src_db_dst_db_with_compare_db(request, kwargs, src_id, dst_id):
    src_db, dst_db, compare_db = None, None, None
    if len(kwargs) > 1:
        src_id = kwargs['id1']
        dst_id = kwargs['id2']
    try:
        src_db = DBInstance.objects.get(id=src_id)
        dst_db = DBInstance.objects.get(id=dst_id)

        if src_db and dst_db:
            try:
                ob = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)
                ob.last_compared = datetime.now(central)
                ob.save()
                compare_db = ob
            except DBCompare.DoesNotExist:
                compare_db = DBCompare()
                compare_db.src_db = src_db
                compare_db.dst_db = dst_db
                compare_db.last_compared = datetime.now(central)
                compare_db.save()
    except DBInstance.DoesNotExist:
        messages.success(request, 'Something went wrong! Src_DB Dst_DB can\'t be mapped. Contact Admin')

    return src_db, dst_db, compare_db


def record_compare_start(compare_db, request, src_id, dst_id, func_name):
    try:
        com = DBCompareDBResults.objects.get(compare_dbs=compare_db, func_call=func_name)
        last_comp = (datetime.now(central) - com.last_compared)
        delta_limit_5 = (timedelta(seconds=60))
        if com.status == 0 and last_comp < delta_limit_5:
            messages.error(request, "Try again in 5 min! There is already a background process comparing the same DB!")
            return HttpResponseRedirect(reverse('dbs:compare_db_results', kwargs={'id1': src_id, 'id2': dst_id}))
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


class DbCompareResultView(PermissionRequiredMixin, ListView):
    permission_required = add_instance
    model = DBInstance
    template_name = 'compare-db-results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        src_db = self.kwargs['id1']
        dst_db = self.kwargs['id2']
        try:
            db_compare = DBCompare.objects.filter(src_db=src_db, dst_db=dst_db)
            if len(db_compare) > 0:
                db_compare_entry = DBTableCompare.objects.filter(compare_dbs=db_compare[0].id)
                context['compare_dbs'] = db_compare[0].id
                if len(db_compare_entry) > 0:
                    context['last_update'] = db_compare_entry.latest('added_on').added_on
                context['db_compare_res_bulk'] = DBTableCompare.objects.filter(compare_dbs=db_compare[0].id).exclude(
                    src_row_count=None, dst_row_count=None).exclude(src_row_count=None).exclude(src_row_count=0).order_by(
                    'table_name')
        except DBCompare.DoesNotExist:
            pass
        try:
            context['src_db_v'] = DBInstance.objects.get(id=self.kwargs['id1'])
            context['dst_db_v'] = DBInstance.objects.get(id=self.kwargs['id2'])
        except DBInstance.DoesNotExist:
            pass
        context['id1'] = src_db
        context['id2'] = dst_db
        try:
            context['row_count'] = self.kwargs['row_count']
            context['table_name'] = self.kwargs['table_name']
        except:
            pass
        context['segment'] = 'compare-db'
        return context

    def post(self, request, *args, **kwargs):
        src_id = None
        dst_id = None
        src_db = None
        dst_db = None
        compare_db = None
        if request.method == 'POST':
            src_id = self.request.POST.get('src_db')
            dst_id = self.request.POST.get('dst_db')
            src_db, dst_db, compare_db = get_src_db_dst_db_with_compare_db(request, self.kwargs, src_id, dst_id)
            if self.request.POST.get('compare'):
                if request.user.has_perm('dbs.can_compare_db'):
                    try:
                        src_db = DBInstance.objects.get(id=src_id)
                        dst_db = DBInstance.objects.get(id=dst_id)
                    except DBInstance.DoesNotExist:
                        messages.success(request, 'Something went wrong! Src_DB Dst_DB can\'t be mapped. Contact Admin')
                    if src_id is None or dst_id is None:
                        messages.error(request, "Make sure to select source and destination DB!")
                        return HttpResponseRedirect(reverse('dbs:compare_db'))
                    if src_id is not None and dst_id is not None and src_id == dst_id:
                        messages.error(request, "Cannot compare same DB!")
                        return HttpResponseRedirect(reverse('dbs:compare_db'))

                    try:
                        ob = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)
                        ob.last_compared = datetime.now(central)
                        ob.save()
                        compare_db = ob
                    except DBCompare.DoesNotExist:
                        compare_db = DBCompare()
                        compare_db.src_db = src_db
                        compare_db.dst_db = dst_db
                        compare_db.last_compared = datetime.now(central)
                        compare_db.save()

                    args = (request.user, src_db, dst_db, compare_db)

                    # any_db(request.user, src_db, dst_db, compare_db).row_count_db()
                    # any_db(request.user, src_db, dst_db, compare_db).table_column_pk_ui_comparision()
                    # any_db(request.user, src_db, dst_db, compare_db).table_data_type_db()

                    queue_high = get_queue('high')
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_rows.__name__)
                    queue_high.enqueue(compare_db_rows, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_data_types.__name__)
                    data_type_compare = queue_high.enqueue(compare_db_data_types, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_for_geom_module_id.__name__)
                    queue_high.enqueue(compare_db_for_geom_module_id, args=args, depends_on=data_type_compare)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_tables_fk_ui.__name__)
                    queue_high.enqueue(compare_db_tables_fk_ui, args=args, depends_on=data_type_compare)


                    queue_low = get_queue('low')
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_views.__name__)
                    queue_low.enqueue(compare_db_views, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_seq.__name__)
                    queue_low.enqueue(compare_db_seq, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_fk.__name__)
                    queue_low.enqueue(compare_db_fk, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_trig.__name__)
                    queue_low.enqueue(compare_db_trig, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_ind.__name__)
                    queue_low.enqueue(compare_db_ind, args=args)
                    record_compare_start(compare_db=compare_db, request=request, src_id=src_id, dst_id=dst_id, func_name=compare_db_proc.__name__)
                    queue_low.enqueue(compare_db_proc, args=args)

                    messages.success(request, 'DB table row comparisons started!')
                else:
                    messages.error(request, 'Permission required to compare DB!!')
                # return HttpResponseRedirect(reverse('dbs:compare_dbs', kwargs={'id1': src_id, 'id2': dst_id}))
            if self.request.POST.get('truncate'):
                if request.user.has_perm('dbs.can_truncate_table_content'):
                    table_name = self.kwargs['table_name']

                    truncate_table.delay(request.user, dst_db, table_name)
                    # delete(dst_db=dst_db).execute_it(table_name)
                    messages.success(request, 'Truncate initiated for the DB table {}'.format(table_name))
                else:
                    messages.success(request, 'Truncate permission required!!')
            if self.request.POST.get('copy'):
                if request.user.has_perm('dbs.can_copy_table_content'):
                    row_count = self.kwargs['row_count']
                    table_name = self.kwargs['table_name']
                    batch_size = 100000
                    for upper_bound in range(0, int(row_count), batch_size):
                        copy_table_content.delay(request.user, src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, True)
                        # xerox(src_db=src_db, dst_db=dst_db, table_name=table_name,
                        #       table_row_count=row_count, upper_bound=upper_bound, commit_each=True).execute_it()
                    messages.success(request, 'Copy initiated for the DB table {}'.format(table_name))
                else:
                    messages.success(request, 'Copy permission required!!')
            if self.request.POST.get('bulkCopy'):
                if request.user.has_perm('dbs.can_bulk_import'):
                    bulk_tables = request.POST.getlist('bulkTables')
                    for each_table in bulk_tables:
                        val_rows = each_table.split('(')
                        table_name = val_rows[0]
                        row_count = val_rows[1][0:len(val_rows[1])-1]
                        batch_size = 100000
                        for upper_bound in range(0, int(row_count), batch_size):
                            copy_table_content.delay(request.user, src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, False)
                    messages.success(request, 'Bulk copy initiated!')
                else:
                    messages.success(request, 'Bulk copy permission required!!')
            if self.request.POST.get('disableTrigger'):
                if request.user.has_perm('dbs.can_disable_triggers'):
                    # disable_all_postgre_triggers.delay(dst_db, compare_db)
                    disable_all_postgre_triggers(dst_db, compare_db)
                    messages.success(request, 'Process initialed to disable all the triggers!')
                else:
                    messages.success(request, 'Disable Trigger permission required!!')
            if self.request.POST.get('enableTrigger'):
                if request.user.has_perm('dbs.can_enable_triggers'):
                    enable_all_postgre_triggers.delay(dst_db, compare_db)
                    messages.error(request, 'Process initialed to enable all the triggers!')
                else:
                    messages.success(request, 'Enable Trigger permission required!!')

        return HttpResponseRedirect(reverse('dbs:compare_db_results', kwargs={'id1': src_id, 'id2': dst_id}))

