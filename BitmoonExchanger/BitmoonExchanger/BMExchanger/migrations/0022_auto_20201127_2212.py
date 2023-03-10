# Generated by Django 3.0.7 on 2020-11-27 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0021_exchangertransactionsteplimit_coin_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangertransactionsteplimit',
            name='final_vnd_price',
            field=models.DecimalField(decimal_places=9, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='exchangertransactionsteplimit',
            name='temp_vnd_price',
            field=models.DecimalField(decimal_places=9, max_digits=19, null=True),
        ),
    ]
