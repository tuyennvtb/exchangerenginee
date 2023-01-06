import traceback
from celery import shared_task
import logging

from .services.publishing_service import PublishingService

from ..BMUtils.utils.cache_utils import CacheUtils
from ..BMUtils.utils.constants import *

import time
import datetime


_logger = logging.getLogger(__name__)


@shared_task
def publish_coins():
    pass

@shared_task
def publish_coin_settings():
    pass

@shared_task
def publish_orderbook():
    PublishingService().publish_orderbook()

    