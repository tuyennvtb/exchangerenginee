# Generated by Django 3.0.7 on 2020-12-27 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0006_brokercoinmappingmodel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brokercoinpricemodel',
            old_name='status',
            new_name='broker_listing_status',
        ),
        migrations.RenameField(
            model_name='brokermarketpairmodel',
            old_name='status',
            new_name='broker_listing_status',
        ),
    ]
