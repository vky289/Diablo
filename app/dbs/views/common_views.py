from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import RedirectView, DetailView, TemplateView, ListView
from django.contrib import messages
from diablo.tasks import compare_db_rows, compare_db_data_types, truncate_table, copy_table_content, compare_db_views, compare_db_seq
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django_rq import get_queue

from app.dbs.models import DBInstance, DBCompare, DBTableCompare, DBTableColumnCompare, DBObjectCompare

from utils.enums import DbType, DBObject
from utils.enable_disable_triggers import triggers
from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox


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

    def save_db_details(self, obj, request):
        obj.host = request.POST.get('host')
        obj.name = request.POST.get('name')
        obj.port = request.POST.get('port')
        obj.username = request.POST.get('username')
        obj.password = request.POST.get('password')
        obj.sid = request.POST.get('sid')
        obj.service = request.POST.get('service')
        obj.type = request.POST.get('type')
        obj.save()


    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.user.has_perm('dbs.add_dbinstance'):
                if self.request.POST.get('saveDB'):
                    obj = DBInstance()
                    self.save_db_details(obj, request)
                    messages.info(request, f'DB Connections Successfully saved!')
                if request.user.has_perm('dbs.change_dbinstance'):
                    if self.request.POST.get('editDB'):
                        obj = DBInstance.objects.get(id=self.request.POST.get('id'))
                        self.save_db_details(obj, request)
                        messages.info(request, f'DB Connections Updated saved!')
                    if self.request.POST.get('delete'):
                        obj = DBInstance.objects.get(id=self.request.POST.get('id'))
                        obj.delete()
                        messages.info(request, f'DB Connections successfully deleted!')
                else:
                    messages.info(request, 'You don\'t have permission to modify/delete DB details!!')
            else:
                messages.info(request, 'You don\'t have permission to add DB details!!')
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
        context['db_instance_or'] = DBInstance.objects.all().order_by('-host', 'name')
        context['db_instance_pg'] = context['db_instance_or']
        #context['db_instance_or'] = DBInstance.objects.filter(type='oracle').order_by('-host', 'name')
        #context['db_instance_pg'] = DBInstance.objects.filter(type='postgres').order_by('-host', 'name')
        context['compare_results'] = DBCompare.objects.values_list('src_db',
                                                                   'dst_db'
                                                                   ).distinct()
        try:
            compare_q = set()
            for ll in context['compare_results']:
                compare_q.add((DBInstance.objects.get(id=ll[0]), DBInstance.objects.get(id=ll[1]),))
            context['compare_q'] = compare_q
        except DBInstance.DoesNotExist:
            pass
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
        src_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare, table_name=table_name, type=DbType.ORACLE)
        dst_table_col = DBTableColumnCompare.objects.filter(compare_dbs=db_compare, table_name=table_name, type=DbType.POSTGRES)

        dd = []
        for d_c_n in dist_col_names:
            final_dict = dict()
            dd_1 = d_c_n.column_name
            final_dict['column_name'] = dd_1
            for src in src_table_col:
                if dd_1 == src.column_name:
                    final_dict['src_data_type'] = src.datatype + '(' + src.precision + ')'

            for dst in dst_table_col:
                if dd_1 == dst.column_name:
                    final_dict['dst_data_type'] = dst.datatype + '(' + dst.precision + ')'
            dd.append(final_dict)
        context['data_type_compare_res'] = dd
        context['src_db_type'] = DBInstance.objects.get(id=src_db).type
        context['dst_db_type'] = DBInstance.objects.get(id=dst_db).type
        context['segment'] = 'compare-db'
        return context


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
                context['db_compare_results'] = DBTableCompare.objects.filter(compare_dbs=db_compare[0].id).exclude(
                    src_row_count=None, dst_row_count=None).exclude(src_row_count=None).order_by(
                    '-src_row_count')
                context['db_view_results'] = DBObjectCompare.objects.filter(compare_dbs=db_compare[0].id, type=DBObject.VIEW).exclude(
                    src_exists=False, dst_exists=False).order_by(
                    'table_name')
                context['db_seq_results'] = DBObjectCompare.objects.filter(compare_dbs=db_compare[0].id, type=DBObject.SEQUENCE).exclude(
                    src_exists=False, dst_exists=False).order_by(
                    'table_name')
                db_compare_entry = DBTableCompare.objects.filter(compare_dbs=db_compare[0].id)
                if len(db_compare_entry) > 0:
                    max_date = db_compare_entry.latest('added_on').added_on
                    parsed_ago = (timezone.now() - max_date)
                    context['last_update'] = f'{parsed_ago.days * 1440 + int(parsed_ago.seconds / 60)} minutes ago'
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
        if request.method == 'POST':
            try:
                src_id = self.kwargs['id1']
                dst_id = self.kwargs['id2']
                src_db = DBInstance.objects.get(id=src_id)
                dst_db = DBInstance.objects.get(id=dst_id)
            except:
                pass
            if self.request.POST.get('compare'):
                if request.user.has_perm('dbs.can_compare_db'):
                    src_id = self.request.POST.get('src_db')
                    dst_id = self.request.POST.get('dst_db')
                    if src_id is None or dst_id is None:
                        messages.error(request, "Make sure to select source and destination DB!")
                        return HttpResponseRedirect(reverse('dbs:compare_db'))
                    if src_id is not None and dst_id is not None and src_id == dst_id:
                        messages.error(request, "Cannot compare same DB!")
                        return HttpResponseRedirect(reverse('dbs:compare_db'))
                    src_db = DBInstance.objects.get(id=src_id)
                    dst_db = DBInstance.objects.get(id=dst_id)
                    compare_db = None
                    try:
                        ob = DBCompare.objects.get(src_db=src_db, dst_db=dst_db)
                        compare_db = ob
                    except DBCompare.DoesNotExist:
                        compare_db = DBCompare()
                        compare_db.src_db = src_db
                        compare_db.dst_db = dst_db
                        compare_db.save()

                    queue = get_queue('default')
                    row_compare = queue.enqueue(compare_db_rows, args=(request.user, src_db, dst_db, compare_db))
                    queue.enqueue(compare_db_data_types, args=(request.user, src_db, dst_db, compare_db), depends_on=row_compare)

                    queue.enqueue(compare_db_views, args=(request.user, src_db, dst_db, compare_db))
                    queue.enqueue(compare_db_seq, args=(request.user, src_db, dst_db, compare_db))
                    #any_db(request.user, src_db, dst_db).c_db()
                    #any_db(request.user, src_db, dst_db).cdata_db()
                    #any_db(request.user, src_db, dst_db).cdata_view()
                    messages.info(request, f'DB table row comparisons started!')
                else:
                    messages.info(request, 'Permission required to compare DB!!')
                return HttpResponseRedirect(reverse('dbs:compare_dbs', kwargs={'id1': src_id, 'id2': dst_id}))
            if self.request.POST.get('truncate'):
                if request.user.has_perm('dbs.can_truncate_table_content'):
                    table_name = self.kwargs['table_name']
                    dst_db = DBInstance.objects.get(id=dst_id)
                    truncate_table.delay(request.user, dst_db, table_name)
                    # delete(dst_db=dst_db).execute_it(table_name)
                    messages.info(request, 'Truncate initiated for the DB table {}'.format(table_name))
                else:
                    messages.info(request, 'Truncate permission required!!')
            if self.request.POST.get('copy'):
                if request.user.has_perm('dbs.can_copy_table_content'):
                    row_count = self.kwargs['row_count']
                    table_name = self.kwargs['table_name']
                    batch_size = 100000
                    for upper_bound in range(0, int(row_count), batch_size):
                        copy_table_content.delay(request.user, src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, False)
                        # xerox(src_db=src_db, dst_db=dst_db, table_name=table_name,
                        #       table_row_count=row_count, upper_bound=upper_bound, commit_each=True).execute_it()
                    messages.info(request, 'Copy initiated for the DB table {}'.format(table_name))
                else:
                    messages.info(request, 'Copy permission required!!')
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
                    messages.info(request, 'Bulk copy initiated!')
                else:
                    messages.info(request, 'Bulk copy permission required!!')
            if self.request.POST.get('disableTrigger'):
                if request.user.has_perm('dbs.can_disable_triggers'):
                    triggers(dst_db).execute_it(ty='DISABLE')
                    messages.info(request, 'All the triggers are disabled!')
                else:
                    messages.info(request, 'Disable Trigger permission required!!')
            if self.request.POST.get('enableTrigger'):
                if request.user.has_perm('dbs.can_enable_triggers'):
                    triggers(dst_db).execute_it(ty='ENABLE')
                    messages.error(request, 'All the triggers are enabled!')
                else:
                    messages.info(request, 'Enable Trigger permission required!!')

        return HttpResponseRedirect(reverse('dbs:compare_db_results', kwargs={'id1': src_id, 'id2': dst_id}))

