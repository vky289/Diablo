__author__ = 'vsellamuthu@agileassets.com'

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.core.models import SYSetting


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
