import traceback
from celery import shared_task
import logging

from .services.transaction_service import TransactionService
from .services.schedule_service import ScheduleService
from .business.withdraw_business import WithdrawBusiness




from ..BMUtils.utils.cache_utils import CacheUtils
from ..BMUtils.utils.constants import *

import time
import datetime


_logger = logging.getLogger(__name__)
@shared_task
def process_transaction(unique_id):
    print("I am processing now: {0}".format(unique_id))
    TransactionService().process_transaction(unique_id=unique_id)
    pass

@shared_task
def process_trade_transaction(buy_unique_id,sell_unique_id):
    print("I am processing now Trade: {0}, {1}".format(buy_unique_id,sell_unique_id))
    TransactionService().process_trade_transaction(buy_unique_id=buy_unique_id,sell_unique_id=sell_unique_id)


@shared_task
def retry_wallet():
    ScheduleService().retry_wallet()


@shared_task
def publish_orderbook():
    return


@shared_task
def withdraw_now():
    WithdrawBusiness().do_withdraw()
    pass

@shared_task
def update_withdraw_status():
    WithdrawBusiness().match_withdraw()
    WithdrawBusiness().notify_withdraw()