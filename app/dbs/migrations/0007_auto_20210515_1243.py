# Generated by Django 3.0.5 on 2021-05-15 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbs', '0006_dbtablecolumncompare_precision'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dbinstance',
            options={'ordering': (('host', 'name', 'sid', 'service'),)},
        ),
    ]
