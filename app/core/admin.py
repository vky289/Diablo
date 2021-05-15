from django.contrib import admin
from app.core.models import RQQueue, SYSetting


class RQQueueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'func_name',
        'status',
        'ended_at',
    )


class SYSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'value',
    )


admin.site.register(RQQueue, RQQueueAdmin)
admin.site.register(SYSetting, SYSettingsAdmin)
