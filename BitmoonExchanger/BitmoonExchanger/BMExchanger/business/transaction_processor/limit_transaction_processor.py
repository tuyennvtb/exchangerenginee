from ....BMUtils.utils.constants import *
from ....BMUtils.utils.exchanger_utils import Exchanger_Utils
from ....BMUtils.utils.cache_utils import CacheUtils

from ...models import ExchangerTransactionStepLimit
from ....BMBrokers.services.broker_trading_service import BrokerTradingService

from sentry_sdk import capture_exception

class LimitTransactionProcessor:
    def __init__(self,transaction,coin_setting,market_pair):
        self.transaction =transaction
        self.coin_setting = coin_setting
        self.market_pair = market_pair

    def process(self):
        print("I am running LimitTransactionProcessor")


        

        if self.transaction.action==ExchangerTransactionType.BUY:
            self._process_buy()
        else:
            self._process_sell()
    def _process_buy(self):
        #We have VND, Calculate Fee -> Convert to USD ->

        print(self.market_pair)

        transaction_step = ExchangerTransactionStepLimit()
        transaction_step.transaction_id = self.transaction.ID
        transaction_step.user_id = self.transaction.user_id
        transaction_step.action = self.transaction.action
        transaction_step.trade_mode = self.transaction.trade_mode
        transaction_step.broker_id = self.coin_setting['broker_id']
        transaction_step.market_pair = self.market_pair['market_pair']

        transaction_step.coin_amount_submitted = self.transaction.coin_amount_submitted - self.transaction.coin_amount_filled
        transaction_step.submitted_price = (float(self.market_pair['ask_price']) * 101.0/100.0)

        
        transaction_step.vnd_match_price =  Exchanger_Utils.get_coin_price(self.transaction.coin_id).vnd_ask_price
        transaction_step.system_status = TransactionStatusConstants.PROCESSING

        transaction_step.save()

        self.transaction.system_status  = TransactionStatusConstants.PROCESSING
        self.transaction.save()


        order_id = BrokerTradingService().submit_transaction_limit(broker_id=transaction_step.broker_id,action=transaction_step.action,pair=transaction_step.market_pair,amount=transaction_step.coin_amount_submitted,price=transaction_step.submitted_price)
        
        
        if order_id:
            transaction_step.broker_unique_id = order_id        
            transaction_step.save()
            
            
            #Successfull
            return True
        else:
            transaction_step.system_status = TransactionStatusConstants.ERROR
            transaction_step.save()
            self.transaction.system_status  = TransactionStatusConstants.ERROR
            self.transaction.save()

            return False

    def _process_sell(self):
        
        
        transaction_step = ExchangerTransactionStepLimit()
        transaction_step.transaction_id = self.transaction.ID
        transaction_step.user_id = self.transaction.user_id
        transaction_step.action = self.transaction.action
        transaction_step.trade_mode = self.transaction.trade_mode
        transaction_step.broker_id = self.coin_setting['broker_id']
        transaction_step.market_pair = self.market_pair['market_pair']
        transaction_step.coin_amount_submitted = self.transaction.reserved_amount - self.transaction.coin_amount_filled

        transaction_step.submitted_price = (float(self.market_pair['bid_price']) * 99.0/100.0)        
        

        transaction_step.vnd_match_price =  Exchanger_Utils.get_coin_price(self.transaction.coin_id).vnd_bid_price
        transaction_step.system_status = TransactionStatusConstants.PROCESSING

        transaction_step.save()

        self.transaction.system_status  = TransactionStatusConstants.PROCESSING
        self.transaction.save()


        order_id = BrokerTradingService().submit_transaction_limit(broker_id=transaction_step.broker_id,action=transaction_step.action,pair=transaction_step.market_pair,amount=transaction_step.coin_amount_submitted,price=transaction_step.submitted_price)
        
        if order_id:
            transaction_step.broker_unique_id = order_id
            transaction_step.save()
        else:
            try:
                transaction_step.system_status = TransactionStatusConstants.ERROR
                transaction_step.save()
                self.transaction.system_status  = TransactionStatusConstants.ERROR
                self.transaction.save()

            except Exception as e:
                print(e)

