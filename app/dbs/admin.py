from django.contrib import admin
from app.dbs.models import DBInstance, DBCompare, DBTableCompare, DBTableColumnCompare, DBStats, DBObjectCompare


class DBInstanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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


class DBCompareAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'src_db',
        'dst_db',
        'added_on',
    )


class DBTableCompareAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'table_name',
        'compare_dbs',
        'src_row_count',
        'dst_row_count',
        'mismatch_in_cols_count',
        'geom',
        'added_on',
    )


class DBTableColumnCompareAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'table_name',
        'compare_dbs',
        'type',
        'column_name',
        'datatype',
        'precision',
        'added_on',
    )


class DBObjectCompareAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'table_name',
        'compare_dbs',
        'src_exists',
        'dst_exists',
        'type',
        'added_on',
    )


class DBStatsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'table_name',
        'compare_dbs',
        'total_rows_inserted',
        'total_rows_errors',
        'added_on',
    )


admin.site.register(DBInstance, DBInstanceAdmin)
admin.site.register(DBCompare, DBCompareAdmin)
admin.site.register(DBTableCompare, DBTableCompareAdmin)
admin.site.register(DBTableColumnCompare, DBTableColumnCompareAdmin)
admin.site.register(DBObjectCompare, DBObjectCompareAdmin)
admin.site.register(DBStats, DBStatsAdmin)
