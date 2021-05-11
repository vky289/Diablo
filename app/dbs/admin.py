from django.contrib import admin
from app.dbs.models import DBInstance, SYSettings


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


class DBSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'settings',
        'added_by',
    )


admin.site.register(DBInstance, DBInstanceAdmin)
admin.site.register(SYSettings, DBSettingsAdmin)
