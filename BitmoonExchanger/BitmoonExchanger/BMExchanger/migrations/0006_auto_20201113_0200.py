# Generated by Django 3.0.7 on 2020-11-13 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0005_exchangertransactionstep_usd_rate_vnd'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exchangertransactionstep',
            old_name='actual_price',
            new_name='actual_usd_price',
        ),
        migrations.RenameField(
            model_name='exchangertransactionstep',
            old_name='price',
            new_name='final_usd_price',
        ),
        migrations.AddField(
            model_name='exchangertransactionstep',
            name='vnd_match_price',
            field=models.DecimalField(decimal_places=9, max_digits=19, null=True),
        ),
    ]
