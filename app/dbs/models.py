from django.db import models
from django.contrib.auth.models import User
from utils.enums import DbType


class DBInstance(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    host = models.CharField(max_length=100, blank=False)
    port = models.IntegerField(blank=False)
    username = models.CharField(max_length=32, blank=False)
    password = models.CharField(max_length=32, blank=False)
    sid = models.CharField(max_length=10, blank=True, default=None)
    service = models.CharField(max_length=10, blank=True, default=None)
    type = models.CharField(max_length=100, choices=DbType.choices)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    added_on = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name


class SYSettings(models.Model):
    name = models.CharField(primary_key=True, max_length=100, blank=False)
    settings = models.CharField(max_length=400, blank=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, default=None)

    def __str__(self):
        return self.name


class DBTableCompare(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=400, blank=False)
    src_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='source_db')
    dst_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='destination_db')
    src_row_count = models.IntegerField(null=True, default=0)
    dst_row_count = models.IntegerField(null=True, default=0)
    mismatch_in_cols_count = models.BooleanField(default=False)

    def __str__(self):
        return self.id


class DBTableColumnCompare(models.Model):
    id = models.AutoField(primary_key=True)
    table_name = models.CharField(max_length=400, blank=False)
    src_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='source_db_column')
    dst_db = models.ForeignKey(DBInstance, on_delete=models.CASCADE, related_name='destination_db_column')
    type = models.CharField(max_length=100, choices=DbType.choices)
    column_name = models.CharField(max_length=100, blank=False)
    datatype = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.id