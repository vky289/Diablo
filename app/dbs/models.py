from django.db import models
from django.contrib.auth.models import User
from utils.enums import DbType, DBObject


class DBInstance(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    host = models.CharField(max_length=100, blank=False)
    port = models.IntegerField(blank=False)
    username = models.CharField(max_length=32, blank=False)
    password = models.CharField(max_length=32, blank=False)
    sid = models.CharField(max_length=100, blank=True, default=None)
    service = models.CharField(max_length=100, blank=True, default=None)
    type = models.CharField(max_length=100, choices=DbType.choices)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name + ' - ' + self.host + ' - ' + str(self.port) + ' - ' + self.username + ' - ' + self.service

    class Meta:
        ordering = ('host', 'name', 'sid', 'service')
        permissions = [
            ('can_disable_triggers', 'User can disable triggers'),
            ('can_enable_triggers', 'User can enable triggers'),
            ('can_bulk_import', 'User can do bulk import'),
            ('can_copy_table_content', 'User can do table copy'),
            ('can_truncate_table_content', 'User can truncate table content'),
        ]


class DBCompare(models.Model):
    id = models.AutoField(primary_key=True)
    src_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='source_db')
    dst_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='destination_db')
    added_on = models.DateTimeField(auto_now_add=True, blank=True)
    last_compared = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.src_db.name + "-" + self.dst_db.name

    class Meta:
        permissions = [
            ('can_compare_db', 'User can compare DB instance'),
        ]
        indexes = [
            models.Index(fields=['src_db', 'dst_db']),
        ]


class DBTableCompare(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=400, blank=False)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s_db_d_db')
    src_row_count = models.IntegerField(null=True, default=0)
    dst_row_count = models.IntegerField(null=True, default=0)
    mismatch_in_cols_count = models.BooleanField(default=False)
    geom = models.BooleanField(default=False)
    module_id = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['table_name', 'compare_dbs', 'added_on', ]),
        ]


class DBTableColumnCompare(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=400, blank=False)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s1_db_d1_db')
    type = models.CharField(max_length=100, choices=DbType.choices)
    column_name = models.CharField(max_length=100, blank=False)
    datatype = models.CharField(max_length=100, blank=False)
    precision = models.CharField(max_length=10, blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)
    is_ui = models.BooleanField(default=False)

    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['table_name', 'compare_dbs', 'column_name', 'added_on', ]),
        ]


class DBObjectCompare(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=400, blank=False)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s3_db_d3_db')
    src_exists = models.BooleanField(default=False, null=True)
    dst_exists = models.BooleanField(default=False, null=True)
    type = models.CharField(max_length=100, choices=DBObject.choices)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ('table_name', )


class DBObjectFKCompare(models.Model):
    id = models.AutoField(primary_key=True)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s4_db_d4_db')
    const_name = models.CharField(max_length=50, blank=True, null=True)
    src_1_table_name = models.CharField(max_length=50, blank=True, null=True)
    src_1_col_name = models.CharField(max_length=50, blank=True, null=True)
    src_2_table_name = models.CharField(max_length=50, blank=True, null=True)
    src_2_col_name = models.CharField(max_length=50, blank=True, null=True)
    dst_1_table_name = models.CharField(max_length=50, blank=True, null=True)
    dst_1_col_name = models.CharField(max_length=50, blank=True, null=True)
    dst_2_table_name = models.CharField(max_length=50, blank=True, null=True)
    dst_2_col_name = models.CharField(max_length=50, blank=True, null=True)
    src_exists = models.BooleanField(default=False, null=True)
    dst_exists = models.BooleanField(default=False, null=True)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ('const_name', 'src_1_table_name', 'src_1_col_name', 'src_2_table_name', 'src_2_col_name', )
        indexes = [
            models.Index(fields=['const_name', 'src_1_table_name', 'src_1_col_name', ]),
        ]


class DBStats(models.Model):
    id = models.AutoField(primary_key=True)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s2_db_d2_db')
    table_name = models.CharField(max_length=400, blank=False)
    total_rows_inserted = models.IntegerField(null=True, default=0)
    total_rows_errors = models.IntegerField(null=True, default=0)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)
