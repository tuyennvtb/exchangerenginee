# Generated by Django 3.0.7 on 2020-12-19 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMUtils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logger_Transaction',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_id', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('timestamp', models.DateField(null=True)),
            ],
            options={
                'db_table': 'logger_transaction',
            },
        ),
        migrations.AddField(
            model_name='logger_incoming_request',
            name='timestamp',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='logger_outgoing_request',
            name='timestamp',
            field=models.DateField(null=True),
        ),
    ]
