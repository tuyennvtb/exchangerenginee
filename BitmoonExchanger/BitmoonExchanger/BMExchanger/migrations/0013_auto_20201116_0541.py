# Generated by Django 3.0.7 on 2020-11-16 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMExchanger', '0012_auto_20201116_0541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangertransaction',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='exchangertransaction',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]
