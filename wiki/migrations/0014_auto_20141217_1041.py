# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0013_auto_20141214_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='avg_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='max_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='min_price',
        ),
        migrations.AddField(
            model_name='product',
            name='_avg_price',
            field=models.DecimalField(null=True, decimal_places=0, max_digits=10, db_column=b'avg_price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='_max_price',
            field=models.DecimalField(null=True, decimal_places=0, max_digits=10, db_column=b'max_price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='_min_price',
            field=models.DecimalField(null=True, decimal_places=0, max_digits=10, db_column=b'min_price'),
            preserve_default=True,
        ),
    ]
