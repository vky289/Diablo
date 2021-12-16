__author__ = 'vsellamuthu@agileassets.com'

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.core.models import SYSetting
from diablo import scheduled_tasks
from redis import Redis
import django_rq

redis = Redis(host="diablo-redis", db=0, port=6379, socket_connect_timeout=10, socket_timeout=10)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = 'admin'
            email = __author__
            password = 'admin'
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
        cols_to_avoid = SYSetting.objects.filter(name='COL_TO_AVOID')
        if len(cols_to_avoid) == 0:
            sy_set = SYSetting()
            sy_set.name = 'COL_TO_AVOID'
            sy_set.value = 'ROW_NUM,COMMENT_ID,GEOM'
            sy_set.save()
        cols_to_avoid = SYSetting.objects.filter(name='COL_COMPARE_MAX')
        if len(cols_to_avoid) == 0:
            sy_set = SYSetting()
            sy_set.name = 'COL_COMPARE_MAX'
            sy_set.value = '100000'
            sy_set.save()

        # To-Do: Cleanup RQQueue Jobs
        # scheduler2 = django_rq.get_scheduler('scheduler')
        #
        # for e_jobs in scheduler2.get_jobs():
        #     if e_jobs.func_name != 'diablo.scheduled_tasks.clean_up_rq_tab':
        #         scheduler2.cron(
        #             cron_string='*/5 * * * *',
        #             func=scheduled_tasks.clean_up_rq_tab,
        #             repeat=None
        #         )
        #         print('Cron Job to cleanup r-queue\'s initiated')
