from django.contrib import admin
from app.dbs.models import DBInstance


class DBInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'host',
        'port',
        'type',
        'username',
        'password',
        'sid',
        'service',
        'added_by',
    )


admin.site.register(DBInstance, DBInstanceAdmin)
