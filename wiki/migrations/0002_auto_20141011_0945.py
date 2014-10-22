# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='avg_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='max_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='min_price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0),
        ),
    ]
