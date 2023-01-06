from ....BMUtils.utils.constants import *
from ....BMUtils.utils.exchanger_utils import Exchanger_Utils
from ....BMUtils.utils.datetime_utils import DatetimeUtils
from ....BMUtils.utils.setting_utils import SettingUtils
from ....BMUtils.utils.money_utils import MoneyUtils
from ...models import ExchangerTransactionStepMarket, ExchangerTransaction
from ..publish_business import PublishBusiness
from ....BMBrokers.services.broker_trading_service import BrokerTradingService

from sentry_sdk import capture_exception

from ...tasks_transaction import fulfill_market_step


class MarketTransactionOrderMatching:
    def __init__(self,transaction):
        self.transaction = transaction
        self.coin_setting = Exchanger_Utils.get_coin_setting(coin_id=self.transaction.coin_id)
    
    def match_broker_order(self):
        print("Running : MarketTransactionOrderMatching")
        if self.transaction.system_status == TransactionStatusConstants.DONE:
            return 
        if self.transaction.action == ExchangerTransactionType.BUY:
            self._match_broker_order_market_buy()
        else:
            self._match_broker_order_market_sell()

        self._submit_wallet()

    def _submit_wallet(self):
        pass 

    def _match_broker_order_market_buy(self):
        if self.coin_setting is None:
            print("Coin Setting not found")
            return

        try:
            steps = ExchangerTransactionStepMarket.objects.filter(transaction_id=self.transaction.ID,system_status=TransactionStatusConstants.PROCESSING).all()
            if len(steps) == 1:
                step = steps[0]
            
                if step.system_status == TransactionStatusConstants.PROCESSING and step.broker_unique_id !='':
                    account_order = BrokerTradingService().find_account_order(broker_id=step.broker_id,order_id=step.broker_unique_id)
                    
                    if account_order is not None and account_order.status == BrokerOrderStatus.FILLED:                  
                            account_order.status= BrokerOrderStatus.MATCHED
                            account_order.save()

                            if step.market_pair.endswith(CoinConstants.USDT):
                                step.final_usd_price  = account_order.avg_price
                            else:
                                bitcoin_price = Exchanger_Utils.get_bitcoin_price()
                                step.final_usd_price = float(bitcoin_price.usd_ask_price)*float(account_order.avg_price)

                            step.coin_amount_filled = account_order.fill_quantity
                            step.market_total_amount_filled = account_order.total_amount
                            step.usd_rate_vnd = SettingUtils.get_usd_rate_vnd()

                            #step.coin_fee = self.coin_setting['client_buy_profit']
                            #step.temp_vnd_price = float(step.final_usd_price) * float(step.usd_rate_vnd) * (100 + float(step.coin_fee))/100
                            step.cost_amount = step.temp_cost_amount
                            step.cost_amount_after_fee = step.temp_cost_amount_after_fee
                            step.total_fee = step.temp_fee_amount
                            step.final_vnd_price = step.temp_cost_amount / step.coin_amount_filled

                            step.final_money_added = step.coin_amount_filled 

                            step.system_status = TransactionStatusConstants.DONE
                            step.save()

                            try:
                                fulfill_market_step.delay(step_id=step.ID)
                            except Exception as e:
                                capture_exception(e)


        except Exception as e:
            capture_exception(e)
            
            print(e)
            pass

        
        steps = ExchangerTransactionStepMarket.objects.filter(transaction_id=self.transaction.ID).all()
      

        for step in steps:
            if step.system_status == TransactionStatusConstants.DONE:                
                
                    #DONE
                self.transaction.coin_amount_filled = step.coin_amount_filled
                self.transaction.total_final_fee = self.transaction.fee_reserved
                self.transaction.reserved_remainings=0
                
                self.transaction.cost_amount = self.transaction.reserved_amount
                self.transaction.total_amount_after_fee = self.transaction.market_total_amount_submitted
                self.transaction.market_total_amount_filled = self.transaction.market_total_amount_submitted
                self.transaction.avg_price_vnd = step.final_vnd_price
                self.transaction.avg_price_usd = step.final_usd_price
                self.transaction.estimate_vnd_amount = self.transaction.market_total_amount_submitted

                self.transaction.final_money_added = step.final_money_added 
                self.transaction.refund_amount = 0

                self.transaction.system_status = TransactionStatusConstants.DONE
                self.transaction.display_status = TransactionStatusConstants.DONE
                self.transaction.updated_at = DatetimeUtils.getCurrentTime()
                self.transaction.save()

                PublishBusiness().publish_transaction(self.transaction)
        
        
        
        


    def _match_broker_order_market_sell(self):
        print("I am runing _match_broker_order_market_sell")
        if self.coin_setting is None:
            print("Coin Setting not found")
            return

        try:
            steps = ExchangerTransactionStepMarket.objects.filter(transaction_id=self.transaction.ID,system_status=TransactionStatusConstants.PROCESSING).all()
            if len(steps)==1:
                step = steps[0]
            
                if step.system_status == TransactionStatusConstants.PROCESSING and step.broker_unique_id !='':
                    account_order = BrokerTradingService().find_account_order(broker_id=step.broker_id,order_id=step.broker_unique_id)
                    
                    if account_order is not None and account_order.status == BrokerOrderStatus.FILLED:                  
                            
                            if step.market_pair.endswith(CoinConstants.USDT):
                                step.final_usd_price  = account_order.avg_price
                            else:
                                bitcoin_price = Exchanger_Utils.get_bitcoin_price()
                                step.final_usd_price = float(bitcoin_price.usd_bid_price)*float(account_order.avg_price)

                            step.market_total_amount_filled  = account_order.fill_quantity
                            step.coin_amount_filled = step.market_total_amount_submitted

                            step.usd_rate_vnd = SettingUtils.get_usd_rate_vnd()
                            step.coin_fee = self.coin_setting['client_sell_profit']
                            step.final_vnd_price = float(step.final_usd_price) * float(step.usd_rate_vnd) * (100 - float(step.coin_fee))/100


                            step.cost_amount = MoneyUtils.round_money(number= float(step.coin_amount_filled)*float(step.final_vnd_price) , currency=CoinConstants.VND)
                            step.total_fee = MoneyUtils.round_money(number=float(step.cost_amount) * float(self.transaction.fee_percent)/100.0,currency=CoinConstants.VND)
                            step.cost_amount_after_fee = step.cost_amount - step.total_fee
                            step.final_money_added = step.cost_amount_after_fee

                            step.system_status = TransactionStatusConstants.DONE
                            step.save()

                            account_order.status= BrokerOrderStatus.MATCHED
                            account_order.save()
                            
                            try:
                                fulfill_market_step.delay(step_id=step.ID)
                            except Exception as e:
                                capture_exception(e)



        except Exception as e:
            print(e)
            capture_exception(e)
            pass

        

        steps = ExchangerTransactionStepMarket.objects.filter(transaction_id=self.transaction.ID).all()
        
        

        for step in steps:
            if step.system_status == TransactionStatusConstants.DONE:
                
                #DONE
                self.transaction.coin_amount_filled = step.coin_amount_filled
                self.transaction.market_total_amount_filled = step.coin_amount_filled
                self.transaction.total_final_fee = step.total_fee
                self.transaction.reserved_remainings = 0
                self.transaction.cost_amount = step.cost_amount
                
                self.transaction.cost_amount_after_fee = step.cost_amount_after_fee
                self.transaction.estimate_vnd_amount = step.cost_amount_after_fee
                self.transaction.avg_price_vnd  = step.final_vnd_price
                self.transaction.avg_price_usd = step.final_usd_price

                self.transaction.system_status = TransactionStatusConstants.DONE
                self.transaction.display_status = TransactionStatusConstants.DONE
                self.transaction.updated_at = DatetimeUtils.getCurrentTime()

                self.transaction.final_money_added = step.final_money_added
                self.transaction.refund_amount = 0 

                
                self.transaction.save()

                PublishBusiness().publish_transaction(self.transaction)

                return