from django.db import models
from django.contrib.auth.models import User


class RQQueue(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    func_name = models.CharField(max_length=400, blank=False, null=True)
    status = models.CharField(max_length=100, blank=False, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
