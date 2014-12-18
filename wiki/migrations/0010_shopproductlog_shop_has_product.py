# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0009_shopproductlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopproductlog',
            name='shop_has_product',
            field=models.ForeignKey(default=1, to='wiki.ShopHasProduct'),
            preserve_default=False,
        ),
    ]
