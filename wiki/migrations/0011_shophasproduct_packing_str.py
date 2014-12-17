# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0010_shopproductlog_shop_has_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='shophasproduct',
            name='packing_str',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
