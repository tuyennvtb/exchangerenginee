# Generated by Django 3.0.7 on 2021-01-09 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0008_auto_20201227_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokercoinpricemodel',
            name='market_pair',
            field=models.CharField(max_length=100, null=True),
        ),
    ]