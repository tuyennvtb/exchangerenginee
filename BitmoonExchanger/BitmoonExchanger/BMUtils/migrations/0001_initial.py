# Generated by Django 3.0.7 on 2020-12-19 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Logger_Incoming_Request',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=100)),
                ('payload', models.TextField()),
                ('response', models.TextField()),
            ],
            options={
                'db_table': 'logger_incoming_request',
            },
        ),
        migrations.CreateModel(
            name='Logger_Outgoing_Request',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=100)),
                ('payload', models.TextField()),
                ('response', models.TextField()),
            ],
            options={
                'db_table': 'logger_outcoming_request',
            },
        ),
    ]