# Generated by Django 3.0.7 on 2020-12-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0005_auto_20201226_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerCoinMappingModel',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('broker_id', models.CharField(db_index=True, max_length=100)),
                ('coin_id', models.CharField(db_index=True, max_length=100, null=True)),
                ('coin_name', models.CharField(default='Unknown', max_length=100, null=True)),
                ('coin_symbol', models.CharField(db_index=True, max_length=100)),
                ('created_at', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('status', models.IntegerField(default=0, null=True)),
                ('description', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'broker_coin_mapping',
                'unique_together': {('broker_id', 'coin_id')},
            },
        ),
    ]
