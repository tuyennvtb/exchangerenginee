from __future__ import absolute_import, unicode_literals

import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BitmoonExchanger.settings')

app = Celery('BitmoonExchanger')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace='BitmoonExchanger')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()




app.conf.beat_schedule = {

    'retry_wallet': {
        'task': 'BitmoonExchanger.BMExchanger.tasks.retry_wallet',
        'schedule': crontab()
    },
    'publish_coins': {
        'task': 'BitmoonExchanger.BMExchanger.tasks_publishing.publish_coins',
        'schedule': crontab()
    },
    'publish_coin_settings': {
        'task': 'BitmoonExchanger.BMExchanger.tasks_publishing.publish_coin_settings',
        'schedule': crontab()
    },
    'publish_orderbook': {
        'task': 'BitmoonExchanger.BMExchanger.tasks_publishing.publish_orderbook',
        'schedule': crontab()
    },
    'cmc_coins': {
        'task': 'BitmoonExchanger.Api.tasks.cmc_setup',
        'schedule': crontab(minute=30,hour='*/6')
    },

    'broker_fetch_balance': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_balance',
        'schedule': crontab()
    },
    'broker_fetch_deposit_history': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_deposit_history',
        'schedule': crontab(minute='*/5')
    },

    'broker_fetch_deposit_address': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_deposit_address',
        'schedule': crontab(minute='*/10')
    },
    'fetch_withdraw_history': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_withdraw_history',
        'schedule': crontab(minute='*/3')
    },

    'broker_fetch_coin_info': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_coin_info',
        'schedule': crontab(minute='30')
    },
    'fetch_coin_network': {
        'task': 'BitmoonExchanger.BMBrokers.tasks.fetch_coin_network',
        'schedule': crontab(minute='35')
    },    
    'withdraw_now':{
        'task': 'BitmoonExchanger.BMExchanger.tasks.withdraw_now',
        'schedule': crontab(minute='*/2')

    },
    'update_withdraw_status':{
        'task': 'BitmoonExchanger.BMExchanger.tasks.update_withdraw_status',
        'schedule': crontab(minute='*/5')

    }


}