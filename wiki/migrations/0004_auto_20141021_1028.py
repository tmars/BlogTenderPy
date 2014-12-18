# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_shop_config'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shop',
            old_name='config',
            new_name='excludes',
        ),
        migrations.RemoveField(
            model_name='shophasproduct',
            name='additional_data',
        ),
        migrations.AddField(
            model_name='shop',
            name='selectors',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shophasproduct',
            name='brand_str',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shophasproduct',
            name='category_str',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
