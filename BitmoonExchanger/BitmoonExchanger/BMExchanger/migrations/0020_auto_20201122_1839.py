# Generated by Django 3.0.7 on 2020-11-22 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0019_auto_20201122_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangercoinsetting',
            name='coin_group',
            field=models.IntegerField(default=0, null=True),
        ),
    ]