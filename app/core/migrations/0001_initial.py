# Generated by Django 3.0.5 on 2021-05-05 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RQQueue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('func_name', models.CharField(max_length=400, null=True)),
                ('status', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
