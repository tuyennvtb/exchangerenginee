# Generated by Django 3.0.7 on 2020-11-22 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0013_auto_20201116_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangertransaction',
            name='price_vnd_when_submit',
            field=models.DecimalField(decimal_places=9, max_digits=19, null=True),
        ),
    ]