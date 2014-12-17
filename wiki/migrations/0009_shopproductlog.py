# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0008_auto_20141022_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopProductLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=0)),
                ('available', models.NullBooleanField()),
                ('update', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
