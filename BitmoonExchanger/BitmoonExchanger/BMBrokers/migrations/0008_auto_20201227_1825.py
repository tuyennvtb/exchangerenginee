# Generated by Django 3.0.7 on 2020-12-27 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0007_auto_20201227_1822'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brokercoinpricemodel',
            old_name='broker_listing_status',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='brokermarketpairmodel',
            old_name='broker_listing_status',
            new_name='status',
        ),
    ]
