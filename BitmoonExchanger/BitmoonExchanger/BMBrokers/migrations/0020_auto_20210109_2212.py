# Generated by Django 3.0.7 on 2021-01-09 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0019_broker_coin_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker_coin_info',
            name='deposit_status',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='broker_coin_info',
            name='min_withdraw_amount',
            field=models.DecimalField(decimal_places=9, default=0, max_digits=29, null=True),
        ),
        migrations.AddField(
            model_name='broker_coin_info',
            name='withdraw_status',
            field=models.IntegerField(null=True),
        ),
    ]
