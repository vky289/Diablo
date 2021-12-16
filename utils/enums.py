from django.db import models
from django.utils.translation import gettext_lazy as _


class DbType(models.TextChoices):
    ORACLE = 'oracle', _('oracle')
    POSTGRES = 'postgres', _('postgres')


class DBObject(models.TextChoices):
    VIEW = 'view', _('view')
    SEQUENCE = 'sequence', _('sequence')
    TRIGGER = 'trigger', _('trigger')
    INDEX = 'index', _('index')


class DBSrcDst(models.TextChoices):
    SRC = 'src', _('src')
    DST = 'dst', _('dst')
