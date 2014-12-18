# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0012_product_packing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shop',
            name='excludes',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='product_url',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='scanning',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='selectors',
        ),
    ]
