# Generated by Django 3.0.7 on 2020-11-22 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0016_exchangertransaction_refund_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangertransactionsteplimit',
            name='final_money_added',
            field=models.DecimalField(decimal_places=9, default=0, max_digits=29, null=True),
        ),
    ]
