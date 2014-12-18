# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0002_auto_20141011_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='config',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
