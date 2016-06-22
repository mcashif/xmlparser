# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-21 21:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='XMLData',
            fields=[
                ('nodeID', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nodeName', models.CharField(max_length=200, null=True)),
                ('nodeparentName', models.CharField(max_length=200, null=True)),
                ('nodeparentID', models.IntegerField(default=0)),
                ('nodeattribute', models.CharField(max_length=520, null=True)),
                ('nodedata', models.CharField(max_length=10024, null=True)),
                ('linktoparent', models.CharField(max_length=5024, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='XMLFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=200, null=True)),
                ('file_data', models.FileField(upload_to='dbdata')),
                ('dump_url', models.URLField(blank=True)),
            ],
        ),
    ]