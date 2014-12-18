# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lib.mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('site', models.CharField(max_length=200, blank=True)),
                ('image', models.CharField(max_length=200, blank=True)),
                ('description', models.TextField(blank=True)),
                ('verified', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verified', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('categories', models.ManyToManyField(to='wiki.Category')),
                ('parent', lib.mptt.fields.TreeForeignKey(related_name='children', blank=True, to='wiki.CategoryGroup', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('image', models.CharField(max_length=200, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('avg_price', models.DecimalField(max_digits=10, decimal_places=0)),
                ('min_price', models.DecimalField(max_digits=10, decimal_places=0)),
                ('max_price', models.DecimalField(max_digits=10, decimal_places=0)),
                ('brand', models.ForeignKey(to='wiki.Brand', null=True)),
                ('category', models.ForeignKey(to='wiki.Category', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('site', models.CharField(max_length=200)),
                ('image', models.CharField(max_length=200, blank=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShopHasProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=200)),
                ('price', models.DecimalField(max_digits=10, decimal_places=0)),
                ('name', models.CharField(max_length=200)),
                ('image', models.CharField(max_length=200, null=True, blank=True)),
                ('available', models.NullBooleanField()),
                ('additional_data', models.TextField(null=True, blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('product', models.ForeignKey(blank=True, to='wiki.Product', null=True)),
                ('shop', models.ForeignKey(to='wiki.Shop')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Substance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='product',
            name='substance',
            field=models.ForeignKey(blank=True, to='wiki.Substance', null=True),
            preserve_default=True,
        ),
    ]
