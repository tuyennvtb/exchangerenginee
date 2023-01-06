# Generated by Django 3.0.7 on 2021-09-05 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMBrokers', '0026_auto_20210524_0022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Broker_Network_Info',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('broker_id', models.CharField(db_index=True, max_length=100)),
                ('coin_symbol', models.CharField(max_length=100)),
                ('network', models.CharField(max_length=100)),
                ('network_name', models.CharField(max_length=255)),
                ('is_default', models.BooleanField()),
                ('withdraw_enable', models.BooleanField()),
                ('deposit_enable', models.BooleanField()),
                ('address_regex', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'broker_network_info',
                'unique_together': {('broker_id', 'coin_symbol', 'network')},
            },
        ),
    ]