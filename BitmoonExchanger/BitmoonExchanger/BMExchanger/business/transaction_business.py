from ...BMUtils.utils.constants import *
from ...BMUtils.utils.exchanger_utils import Exchanger_Utils
from ...BMUtils.utils.cache_utils import CacheUtils
from ...BMUtils.utils.datetime_utils import DatetimeUtils


from ..models import ExchangerTransaction,ExchangerTransactionStepLimit,ExchangerTransactionStepMarket
from .transaction_processor.market_transaction_processor import MarketTransactionProcessor
from .transaction_processor.market_transaction_order_matching import MarketTransactionOrderMatching

from .transaction_processor.limit_transaction_processor import LimitTransactionProcessor
from .transaction_processor.limit_transaction_order_matching import LimitTransactionOrderMatching
from .transaction_processor.transaction_wallet_processor import TransactionWalletProcessor

from ...BMBrokers.services.broker_trading_service import BrokerTradingService
from django.db import transaction as django_transaction
from sentry_sdk import capture_exception

from ..tasks_publishing import publish_orderbook

class TransactionBusiness:
    
    def __init__(self,unique_id):
        self.unique_id = unique_id
        

    def _get_transaction_by_unique_id(self,unique_id):
        
        return transaction
                
    def process(self):
        
        cacheKey = "{0}_{1}".format(CacheKey.TRANSACTION_MARKET_PROCESS_LOCKING,self.unique_id)
        print(cacheKey)
        if CacheUtils.get_key(cacheKey):
            print("Another process is processing for : {0}".format(self.unique_id))
            #return

        CacheUtils.cache_key(cacheKey,True,30)

        with django_transaction.atomic():
            transaction = ExchangerTransaction.objects.filter(unique_id=self.unique_id).get()


            coin_setting = Exchanger_Utils.get_coin_setting(coin_id=transaction.coin_id)

            if coin_setting is None:
                print("Setting not found")
                return

            

            market_pair = Exchanger_Utils.get_market_pair(broker_id=coin_setting['broker_id'],coin_id=transaction.coin_id)

            if not market_pair:
                print("Market not found")
                return
        

            if transaction.system_status not in [TransactionStatusConstants.OPEN,TransactionStatusConstants.PARTIAL]:
                return

            #Only process Cancel when status is in OPEN, PARTIAL
            if transaction.display_status != TransactionStatusConstants.REQUEST_CANCEL:
                # #Call Match Broker Order
                # self.match_broker_order()
                # return

                if transaction.trade_mode == ExchangerModeConstants.LIMIT:
                    success = LimitTransactionProcessor(transaction=transaction,coin_setting=coin_setting,market_pair=market_pair).process()


                if transaction.trade_mode == ExchangerModeConstants.MARKET:
                    success = MarketTransactionProcessor(transaction=transaction,coin_setting=coin_setting,market_pair=market_pair).process()


            django_transaction.on_commit(self.match_broker_order)

        publish_orderbook.delay()

    def match_broker_order(self):
        print("I am running match_broker_order")
        with django_transaction.atomic():
            transaction = ExchangerTransaction.objects.filter(unique_id=self.unique_id).get()            

            if transaction.trade_mode == ExchangerModeConstants.LIMIT:
                success = LimitTransactionOrderMatching(transaction=transaction).match_broker_order()
                pass

            if transaction.trade_mode == ExchangerModeConstants.MARKET:
                success = MarketTransactionOrderMatching(transaction=transaction).match_broker_order()

            django_transaction.on_commit(self.call_to_update_wallet)

    def call_to_update_wallet(self):
        print("I am running call_to_update_wallet")
        try:
            with django_transaction.atomic():
                transaction = ExchangerTransaction.objects.filter(unique_id=self.unique_id).get()
                if transaction.wallet_status <=0 and transaction.wallet_request_count < 10:
                    TransactionWalletProcessor(transaction=transaction).call_to_update_wallet()
        except Exception as e:
            capture_exception(e)