# Generated by Django 3.2 on 2021-04-08 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20210406_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='lentTo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='lentToFriend',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]