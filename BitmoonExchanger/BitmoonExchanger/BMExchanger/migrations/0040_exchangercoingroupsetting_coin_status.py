# Generated by Django 3.0.7 on 2021-01-24 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0039_exchangercoingroupsetting_broker_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangercoingroupsetting',
            name='coin_status',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
