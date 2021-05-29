import django_rq
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from django import template
from django.views.generic import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from redis import Redis
from rq import Queue
from rq.registry import FinishedJobRegistry, StartedJobRegistry
from rq.job import Job
from app.core.models import RQQueue
from django.http import HttpResponseRedirect
from django.urls import reverse
from app.dbs.models import DBCompare, DBStats
from django.db.models.functions import TruncMonth
from django.db.models import Count
from easyaudit.models import RequestEvent
from django.db.models import Q
from notifications.models import Notification
from notifications.views import NotificationViewList
from django.shortcuts import get_object_or_404

redis = Redis(host="localhost", db=0, port=6379, socket_connect_timeout=10, socket_timeout=10)


class DjangoRQDetailView(PermissionRequiredMixin, ListView):
    permission_required = 'dbs.add_dbinstance'
    template_name = 'current-queue.html'
    model = RQQueue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'queue'
        queue = Queue(connection=redis)
        context['pending_job'] = len(queue.job_ids)
        context['current_queue'] = RQQueue.objects.all()
        return context

    def store_job_date(self, q_j):
        r_obj = RQQueue.objects.filter(name=q_j.id)
        if not r_obj:
            obj = RQQueue()
            obj.name = q_j.id
            obj.func_name = q_j.func_name
            obj.created_at = q_j.created_at
            #obj.ended_at = q_j.ended_at
            obj.status = q_j._status
            obj.save()

    def post(self, *args, **kwargs):
        queue = Queue(connection=redis)

        for jj in queue.jobs:
            self.store_job_date(jj)

        started_registry = StartedJobRegistry('default', connection=redis)
        job_ids = started_registry.get_job_ids()
        for j_id in job_ids:
            bj = RQQueue.objects.filter(name=j_id)
            if bj:
                abj = RQQueue.objects.get(name=j_id)
                abj.status = 'started'
                abj.save()

        finished_registry = FinishedJobRegistry('default', connection=redis)
        job_ids = finished_registry.get_job_ids()
        for j_id in job_ids:
            bj = RQQueue.objects.filter(name=j_id)
            job_q = Job.fetch(j_id, connection=redis)
            if bj:
                abj = RQQueue.objects.get(name=j_id)
                abj.status = 'finished'
                abj.ended_at = job_q.ended_at
                abj.save()
            else:
                self.store_job_date(job_q)
        return HttpResponseRedirect(reverse('core:current_rq_queue'))


def rep_make_result_set(dataset):
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ss = {}
    for dd in dataset:
        ss[dd.get('month').strftime("%b")] = dd.get('c')
    final_dataset = []
    for m_l in month_list:
        if ss.get(m_l) is None:
            final_dataset.append({'month': m_l, 'y': 0})
        else:
            final_dataset.append({'month': m_l, 'y': ss.get(m_l)})
    return final_dataset


@login_required(login_url="/login/")
def index(request):
    context = {}
    context['segment'] = 'home'

    dbs = DBCompare.objects.annotate(month=TruncMonth('added_on')).values('month').annotate(c=Count('id')).values('month', 'c')
    tabs = DBStats.objects.annotate(month=TruncMonth('added_on')).values('month').annotate(c=Count('id')).values('month', 'c')
    post_data_request = RequestEvent.objects.filter(Q(method='POST')).annotate(month=TruncMonth('datetime')).values('month').annotate(c=Count(
        'month')).values('month', 'c').order_by()
    get_data_request = RequestEvent.objects.filter(Q(method='GET')).annotate(month=TruncMonth('datetime')).values('month').annotate(c=Count(
        'month')).values('month', 'c').order_by()
    data_compared = RequestEvent.objects.filter(Q(method='POST') & Q(url__contains='/dbs/compare/')).annotate(month=TruncMonth(
        'datetime')).values(
        'month').annotate(c=Count('month')).values('month', 'c').order_by()

    db_compared = rep_make_result_set(dbs)
    tables_compared = rep_make_result_set(tabs)
    post_req = rep_make_result_set(post_data_request)
    get_req = rep_make_result_set(get_data_request)
    data_compared_req = rep_make_result_set(data_compared)

    context['dataset'] = db_compared
    context['rows_insert'] = tables_compared
    context['post_req'] = post_req
    context['get_req'] = get_req
    context['data_compared_req'] = data_compared_req

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


class NotificationDetailsView(PermissionRequiredMixin, NotificationViewList):
    permission_required = 'dbs.view_dbinstance'
    model = Notification
    template_name = 'notifications-zone.html'
    success = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(recipient=self.request.user).active()
        return context

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            checks = self.request.POST.getlist('checks[]')
            if self.request.POST.get('mark_as_read'):
                for cc in checks:
                    notif = get_object_or_404(
                            Notification, recipient=request.user, id=cc)
                    notif.mark_as_read()
            if self.request.POST.get('mark_all_read'):
                checks = Notification.objects.filter(recipient=request.user).all()
                for cc in checks:
                    notif = get_object_or_404(
                        Notification, recipient=request.user, id=cc.id)
                    notif.mark_as_read()
            if self.request.POST.get('mark_as_unread'):
                for cc in checks:
                    notif = get_object_or_404(
                        Notification, recipient=request.user, id=cc)
                    notif.mark_as_unread()
            if self.request.POST.get('delete'):
                for cc in checks:
                    notif = get_object_or_404(
                        Notification, recipient=request.user, id=cc)
                    notif.deleted = True
            if self.request.POST.get('delete_all'):
                Notification.objects.filter(recipient=request.user).mark_all_as_deleted()
        return HttpResponseRedirect(reverse('core:notifications'))
