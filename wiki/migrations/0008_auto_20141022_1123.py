# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0007_shop_verified'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shop',
            old_name='verified',
            new_name='scanning',
        ),
    ]
