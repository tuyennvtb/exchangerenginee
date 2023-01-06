import traceback
from celery import shared_task
import logging

from .services.schedule_service import Schedule_Service


@shared_task
def cmc_setup():
    Schedule_Service().setup()
