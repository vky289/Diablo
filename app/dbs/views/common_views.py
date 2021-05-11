from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import RedirectView, DetailView, TemplateView, ListView
from django.urls import reverse
from django.http import HttpResponseRedirect
from app.dbs.models import DBInstance, DBTableCompare
from utils.enums import DbType
from django.contrib import messages
from diablo.tasks import compare_db_rows, compare_db_data_types, truncate_table, copy_table_content
from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox
from utils.enable_disable_triggers import triggers

@staticmethod
def save_db_instance_object(obj, request):

    return obj


class DbInstanceDetailView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.action_all'
    model = DBInstance
    template_name = 'view-db.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_instance'] = DBInstance.objects.order_by('-host', 'name')
        context['db_types'] = DbType
        context['segment'] = 'view-db'
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            obj = DBInstance()
            obj.host = request.POST.get('host')
            obj.name = request.POST.get('name')
            obj.port = request.POST.get('port')
            obj.username = request.POST.get('username')
            obj.password = request.POST.get('password')
            obj.sid = request.POST.get('sid')
            obj.service = request.POST.get('service')
            obj.type = request.POST.get('type')
            obj.save()
            messages.info(request, f'DB Connections Successfully saved!')
            return HttpResponseRedirect(reverse('dbs:db_details'))


class DbInstanceEditView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.action_all'
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

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if self.request.POST.get('save'):
                id = self.request.POST.get('id')
                url_args = (id, )
                obj = DBInstance.objects.get(id=id)
                obj.host = request.POST.get('host')
                obj.name = request.POST.get('name')
                obj.port = request.POST.get('port')
                obj.username = request.POST.get('username')
                obj.password = request.POST.get('password')
                obj.sid = request.POST.get('sid')
                obj.service = request.POST.get('service')
                obj.type = request.POST.get('type')
                obj.save()
                messages.info(request, f'DB Connections Updated saved!')
                return HttpResponseRedirect(reverse('dbs:db_edit_details', args=url_args))
            if self.request.POST.get('delete'):
                id = self.request.POST.get('id')
                obj = DBInstance.objects.get(id=id)
                obj.delete()
                messages.info(request, f'DB Connections successfully deleted!')
                return HttpResponseRedirect(reverse('dbs:db_details'))


class DbCompareDetailView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.action_all'
    model = DBInstance
    template_name = 'compare-db.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_instance'] = DBInstance.objects.order_by('name', '-host')
        context['compare_results'] = DBTableCompare.objects.values_list('src_db', 'dst_db').distinct()
        try:
            compare_q = set()
            for ll in context['compare_results']:
                compare_q.add((DBInstance.objects.get(id=ll[0]), DBInstance.objects.get(id=ll[1]),))
            context['compare_q'] = compare_q
        except DBInstance.DoesNotExist:
            pass
        context['segment'] = 'compare-db'
        return context


class DbCompareResultView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.action_all'
    model = DBInstance
    template_name = 'compare-db-results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['db_compare_results'] = DBTableCompare.objects.filter(src_db=self.kwargs['id1'], dst_db=self.kwargs['id2']).exclude(
            src_row_count=None, dst_row_count=None).exclude(src_row_count=None).order_by(
            '-src_row_count')
        try:
            context['src_db_v'] = DBInstance.objects.get(id=self.kwargs['id1'])
            context['dst_db_v'] = DBInstance.objects.get(id=self.kwargs['id2'])
        except DBInstance.DoesNotExist:
            pass
        context['id1'] = self.kwargs['id1']
        context['id2'] = self.kwargs['id2']
        try:
            context['row_count'] = self.kwargs['row_count']
            context['table_name'] = self.kwargs['table_name']
        except:
            pass
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
                src_id = self.request.POST.get('src_db')
                dst_id = self.request.POST.get('dst_db')
                src_db = DBInstance.objects.get(id=src_id)
                dst_db = DBInstance.objects.get(id=dst_id)
                if src_id is None or dst_id is None:
                    messages.error(request, "Make sure to select source and destination DB!")
                    return HttpResponseRedirect(reverse('dbs:compare_db'))
                if src_id is not None and dst_id is not None and src_id == dst_id:
                    messages.error(request, "Cannot compare same DB!")
                    return HttpResponseRedirect(reverse('dbs:compare_db'))
                compare_db_rows.delay(src_db, dst_db)
                # compare_db_data_types.delay(src_db, dst_db)
                # any_db(src_db, dst_db).c_db()
                messages.info(request, f'DB table row comparisons started!')
            if self.request.POST.get('truncate'):
                table_name = self.kwargs['table_name']
                dst_db = DBInstance.objects.get(id=dst_id)
                truncate_table.delay(dst_db, table_name)
                # delete(dst_db=dst_db).execute_it(table_name)
                messages.info(request, 'Truncate initiated for the DB table {}'.format(table_name))
            if self.request.POST.get('copy'):
                row_count = self.kwargs['row_count']
                table_name = self.kwargs['table_name']
                batch_size = 100000
                for upper_bound in range(0, int(row_count), batch_size):
                    copy_table_content.delay(src_db, dst_db, table_name, upper_bound + batch_size - 1, upper_bound, False)
                    # xerox(src_db=src_db, dst_db=dst_db, table_name=table_name,
                    #       table_row_count=row_count, upper_bound=upper_bound, commit_each=True).execute_it()
                messages.info(request, 'Copy initiated for the DB table {}'.format(table_name))
            if self.request.POST.get('disableTrigger'):
                triggers(dst_db).execute_it(ty='DISABLE')
                messages.info(request, 'All the triggers are disabled!')
            if self.request.POST.get('enableTrigger'):
                triggers(dst_db).execute_it(ty='ENABLE')
                messages.error(request, 'All the triggers are enabled!')

        return HttpResponseRedirect(reverse('dbs:compare_db_results', kwargs={'id1': src_id, 'id2': dst_id}))
        #return HttpResponseRedirect(reverse('dbs:compare_db_res'))

