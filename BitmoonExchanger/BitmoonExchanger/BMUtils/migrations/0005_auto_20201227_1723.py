# Generated by Django 3.0.7 on 2020-12-27 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMUtils', '0004_auto_20201219_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logger_incoming_request',
            name='timestamp',
            field=models.DateTimeField(null=True),
        ),
    ]
