from ..models import ExchangerTransactionStepLimit, ExchangerTransactionStepMarket
from ...BMBrokers.models import Broker_Account_Order
from ...BMUtils.utils.constants import *
from sentry_sdk import capture_exception

from ...BMBrokers.services.broker_trading_service import BrokerTradingService
from ...BMUtils.utils.exchanger_utils import Exchanger_Utils

import time

class Fulfillment:
    def __init__(self):
        pass

    
    def process_steps(self):
        pass

    def process_limit_step(self,step_id):
        time.sleep(1)
        try:
            step = ExchangerTransactionStepLimit.objects.filter(ID=step_id).get()
            if step.system_status != TransactionStatusConstants.DONE:
                print("#1")
                return
            
            if step.fulfillment_broker_unique_id is not None :
                print("#2")
                return
            
            if step.fulfillment_broker_unique_id is not None and len(step.fulfillment_broker_unique_id)==0:
                print("#3")
                return
            
            
            if not step.market_pair.endswith(CoinConstants.BITCOIN):
                step.fulfillment_broker_unique_id='N/A'
                step.save()             
                print("#4")
                return

            
            try:
                order = Broker_Account_Order.objects.filter(orderId=step.broker_unique_id).get()
                fulfillment_broker_unique_id  = self._refill(order=order)
                if fulfillment_broker_unique_id is None:
                    step.fulfillment_broker_unique_id = 'ERROR'
                else:
                    step.fulfillment_broker_unique_id = fulfillment_broker_unique_id
                    self._mark_match_order(order_id=fulfillment_broker_unique_id)
                step.save()
            except Exception as e:
                print(e)
                capture_exception(e)
            

        except Exception as e:
            print(e)
            capture_exception(e)
            pass

    def process_market_step(self,step_id):
        time.sleep(1)
        try:
            step = ExchangerTransactionStepMarket.objects.filter(ID=step_id).get()
            print(step.system_status)
            if step.system_status != TransactionStatusConstants.DONE: 
                print("#1")
                return

            if step.fulfillment_broker_unique_id is not None :
                print("#2")
                return
            
            
            if step.fulfillment_broker_unique_id is not None and len(step.fulfillment_broker_unique_id)==0:
                print("#3")
                return
            
            
            if not step.market_pair.endswith(CoinConstants.BITCOIN):
                print("#4")
                step.fulfillment_broker_unique_id='N/A'
                step.save()             
                return

            
            try:
                order = Broker_Account_Order.objects.filter(orderId=step.broker_unique_id).get()
                
                fulfillment_broker_unique_id  = self._refill(order=order)
                if fulfillment_broker_unique_id is None:
                    step.fulfillment_broker_unique_id = 'ERROR'
                else:
                    step.fulfillment_broker_unique_id = fulfillment_broker_unique_id
                    self._mark_match_order(order_id=fulfillment_broker_unique_id)
                step.save()
            except Exception as e: 
                capture_exception(e)
            
        except Exception as e:
            print(e)
            capture_exception(e)
            pass


    def _refill(self,order):
        if order.broker_id == 'binance':
            return BrokerTradingService().submit_transaction_market(broker_id=order.broker_id,action=order.action,pair='BTCUSDT',total_amount=order.total_amount,by='quantity')

        elif order.broker_id=='huobi-global':
            total_amount = order.total_amount
            
            if order.action == ExchangerTransactionType.BUY:
                bitcoin_price = Exchanger_Utils.get_bitcoin_price()
                total_amount = float(order.total_amount) * float(bitcoin_price.usd_bid_price)
            return BrokerTradingService().submit_transaction_market(broker_id=order.broker_id,action=order.action,pair='BTCUSDT',total_amount=total_amount)


        return None
    def _mark_match_order(self,order_id):

        try:
            order = Broker_Account_Order.objects.filter(orderId=order_id).get()
            if order.status == BrokerOrderStatus.FILLED:
                order.status = BrokerOrderStatus.FULFILL_MATCHED
                order.save()
        
        except Exception as e:
            capture_exception(e)