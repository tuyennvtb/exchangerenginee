# Generated by Django 3.0.7 on 2020-11-27 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0023_auto_20201127_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangertransactionstepmarket',
            name='temp_cost_amount_after_fee',
            field=models.DecimalField(decimal_places=9, max_digits=19, null=True),
        ),
    ]