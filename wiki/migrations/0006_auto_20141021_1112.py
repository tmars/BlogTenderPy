# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0005_shop_check_product_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shop',
            old_name='check_product_url',
            new_name='product_url',
        ),
    ]
