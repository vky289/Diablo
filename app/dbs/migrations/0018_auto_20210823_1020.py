# Generated by Django 3.0.5 on 2021-08-23 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbs', '0017_auto_20210818_1759'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='dbcomparedbresults',
            name='dbs_dbcompa_compare_bd845a_idx',
        ),
        migrations.AddField(
            model_name='dbcomparedbresults',
            name='func_call',
            field=models.CharField(default=None, max_length=400),
        ),
        migrations.AddIndex(
            model_name='dbcomparedbresults',
            index=models.Index(fields=['func_call', 'compare_dbs', 'last_compared', 'status'], name='dbs_dbcompa_func_ca_d3de6b_idx'),
        ),
    ]