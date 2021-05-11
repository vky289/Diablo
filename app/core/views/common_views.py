import django_rq
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from django import template
from django.views.generic import RedirectView, DetailView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from redis import Redis
from rq import Queue
from rq.registry import FinishedJobRegistry, StartedJobRegistry
from rq.job import Job
from app.core.models import RQQueue
from django.http import HttpResponseRedirect
from django.urls import reverse


redis = Redis(host="localhost", db=0, port= 6379, socket_connect_timeout=10, socket_timeout=10)


class DjangoRQDetailView(PermissionRequiredMixin, ListView):
    permission_required = 'accounts.action_all'
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

@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'home'

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