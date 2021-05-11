from django.contrib import admin
from app.core.models import RQQueue


class RQQueueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'func_name',
        'status',
        'ended_at',
    )


admin.site.register(RQQueue, RQQueueAdmin)
