# Generated by Django 3.2 on 2021-04-06 19:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='container',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='account.container'),
            preserve_default=False,
        ),
    ]
