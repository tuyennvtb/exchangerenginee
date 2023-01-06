# Generated by Django 3.0.7 on 2020-11-22 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0015_exchangertransaction_final_money_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangertransaction',
            name='refund_amount',
            field=models.DecimalField(decimal_places=9, default=0, max_digits=29, null=True),
        ),
    ]
