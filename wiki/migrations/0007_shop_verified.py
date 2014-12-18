# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0006_auto_20141021_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='verified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
