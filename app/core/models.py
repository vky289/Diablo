from django.db import models
from app.dbs.models import DBCompare


class RQQueue(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    func_name = models.CharField(max_length=400, blank=False, null=True)
    status = models.CharField(max_length=100, blank=False, null=True)
    compare_dbs = models.ForeignKey(DBCompare, on_delete=models.CASCADE, related_name='s_q_db_d_q_db', default=None, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class SYSetting(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, unique=True)
    value = models.CharField(max_length=1000, blank=False)

    def __str__(self):
        return self.name + " - " + self.value
