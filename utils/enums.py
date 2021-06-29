from django.db import models
from django.utils.translation import gettext_lazy as _


def dont_call_in_template(cls):
    cls.do_not_call_in_templates = True
    return cls


@dont_call_in_template
class DbType(models.TextChoices):
    ORACLE = 'oracle', _('oracle')
    POSTGRES = 'postgres', _('postgres')


@dont_call_in_template
class DBObject(models.TextChoices):
    VIEW = 'view', _('view')
    SEQUENCE = 'sequence', _('sequence')
    TRIGGER = 'trigger', _('trigger')
    INDEX = 'index', _('index')

