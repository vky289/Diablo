# Generated by Django 3.0.5 on 2021-06-10 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dbs', '0010_auto_20210520_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='DBObjectFKCompare',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('const_name', models.CharField(blank=True, max_length=50, null=True)),
                ('src_1_table_name', models.CharField(blank=True, max_length=50, null=True)),
                ('src_1_col_name', models.CharField(blank=True, max_length=50, null=True)),
                ('src_2_table_name', models.CharField(blank=True, max_length=50, null=True)),
                ('src_2_col_name', models.CharField(blank=True, max_length=50, null=True)),
                ('dst_1_table_name', models.CharField(blank=True, max_length=50, null=True)),
                ('dst_1_col_name', models.CharField(blank=True, max_length=50, null=True)),
                ('dst_2_table_name', models.CharField(blank=True, max_length=50, null=True)),
                ('dst_2_col_name', models.CharField(blank=True, max_length=50, null=True)),
                ('compare_dbs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='s4_db_d4_db', to='dbs.DBCompare')),
            ],
            options={
                'ordering': ('const_name', 'src_1_table_name', 'src_1_col_name', 'src_2_table_name', 'src_2_col_name'),
            },
        ),
        migrations.AddIndex(
            model_name='dbobjectfkcompare',
            index=models.Index(fields=['const_name', 'src_1_table_name', 'src_1_col_name'], name='dbs_dbobjec_const_n_a81825_idx'),
        ),
    ]
