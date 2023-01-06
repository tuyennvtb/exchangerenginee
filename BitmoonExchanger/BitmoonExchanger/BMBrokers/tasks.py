import traceback
from celery import shared_task
import logging
import time
import datetime


from .services.schedule_service import ScheduleService
_logger = logging.getLogger(__name__)

@shared_task
def fetch_balance():
    ScheduleService().fetch_balance()

@shared_task
def fetch_deposit_history():
    ScheduleService().fetch_deposit_history()

@shared_task
def fetch_deposit_address():
    ScheduleService().fetch_deposit_address()


@shared_task
def fetch_coin_info():
    ScheduleService().fetch_coin_info()

@shared_task
def fetch_coin_network():
    ScheduleService().fetch_coin_network()


@shared_task
def fetch_withdraw_history():
    ScheduleService().fetch_withdraw_history()    
