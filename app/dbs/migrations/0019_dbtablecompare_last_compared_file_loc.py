# Generated by Django 3.1.13 on 2021-09-29 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbs', '0018_auto_20210823_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbtablecompare',
            name='last_compared_file_loc',
            field=models.CharField(blank=True, default=None, max_length=1000, null=True),
        ),
    ]
