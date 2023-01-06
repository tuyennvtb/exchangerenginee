from ....BMUtils.utils.constants import *
from ....BMUtils.utils.exchanger_utils import Exchanger_Utils
from ....BMUtils.utils.datetime_utils import DatetimeUtils
from ....BMUtils.utils.setting_utils import SettingUtils
from ....BMUtils.utils.money_utils import MoneyUtils

from ...models import ExchangerTransactionStepLimit, ExchangerTransaction

from ..publish_business import PublishBusiness
from ....BMBrokers.services.broker_trading_service import BrokerTradingService

from sentry_sdk import capture_exception

from ...tasks_transaction import fulfill_limit_step


class LimitTransactionOrderMatching:
    def __init__(self,transaction):
        self.transaction = transaction
        self.coin_setting = Exchanger_Utils.get_coin_setting(coin_id=self.transaction.coin_id)
    
    def match_broker_order(self):
        print("Running : LimitTransactionOrderMatching")
        if self.transaction.action == ExchangerTransactionType.BUY:
            self._match_broker_order_limit_buy()
        else:
            self._match_broker_order_limit_sell()

        self._submit_wallet()

    def _submit_wallet(self):
        pass
    def _match_broker_order_limit_buy(self):
        if self.coin_setting is None:
            print("Coin Setting not found")
            return
        print("Running : _match_broker_order_limit_buy")
        try:
            
            steps = ExchangerTransactionStepLimit.objects.filter(transaction_id=self.transaction.ID,system_status=TransactionStatusConstants.PROCESSING).all()
            if len(steps) == 1 : 
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

                            step.coin_amount_filled = min(account_order.fill_quantity,step.coin_amount_submitted)
                            step.coin_amount_remainings = step.coin_amount_submitted - step.coin_amount_filled

                            step.usd_rate_vnd = SettingUtils.get_usd_rate_vnd()
                            step.coin_fee = self.coin_setting['client_buy_profit']
                            step.temp_vnd_price = float(step.final_usd_price) * float(step.usd_rate_vnd) * (100 + float(step.coin_fee))/100
                            step.final_vnd_price = min(self.transaction.submitted_price_vnd,step.temp_vnd_price)

                            step.cost_amount = MoneyUtils.round_money(number=float(step.coin_amount_filled) * float(step.final_vnd_price), currency=CoinConstants.VND)
                            step.total_fee = MoneyUtils.round_money(number=float(step.cost_amount) * float(self.transaction.fee_percent) /100.0,currency=CoinConstants.VND)
                            step.cost_amount_after_fee = step.cost_amount + step.total_fee
                            step.final_money_added = step.coin_amount_filled
                            

                            step.system_status = TransactionStatusConstants.DONE
                            step.save()

                            self.transaction.coin_amount_filled = float(self.transaction.coin_amount_filled) + float(step.coin_amount_filled)
                            self.transaction.cost_amount = float(self.transaction.cost_amount) + float(step.cost_amount)
                            self.transaction.cost_amount_after_fee = float(self.transaction.cost_amount_after_fee) + float(step.cost_amount_after_fee)
                            self.transaction.reserved_remainings = float(self.transaction.reserved_remainings)  - float(self.transaction.cost_amount)
                            self.transaction.total_final_fee = float(self.transaction.total_final_fee)  + float(step.total_fee)

                            self.transaction.save()

                            try:
                                fulfill_limit_step.delay(step_id=step.ID)
                            except Exception as e:
                                capture_exception(e)

                            


                
        except Exception as e:           
            
            print(e)

            capture_exception(e)
            pass


                 
        steps = ExchangerTransactionStepLimit.objects.filter(transaction_id=self.transaction.ID).all()

        amount_filled = 0
        total_fee = 0
        cost_amount =0
        cost_amount_after_fee =0

        

        for step in steps:
            if step.system_status == TransactionStatusConstants.DONE:
                amount_filled += step.coin_amount_filled
                total_fee += step.total_fee
                cost_amount+=step.cost_amount
                cost_amount_after_fee+=step.cost_amount_after_fee
            if step.system_status == TransactionStatusConstants.PROCESSING:
                #Return if there is still someanother

                return

        #DONE
        # self.transaction.coin_amount_filled = amount_filled
        # self.transaction.total_final_fee = total_fee
        # self.transaction.cost_amount = cost_amount
        # self.transaction.cost_amount_after_fee = cost_amount_after_fee
        # self.transaction.reserved_remainings = self.transaction.reserved_amount - self.transaction.cost_amount
        

 
        
        if float(self.transaction.coin_amount_submitted) == float(self.transaction.coin_amount_filled):
            self.transaction.avg_price_vnd  = self.transaction.cost_amount/self.transaction.coin_amount_filled
            self.transaction.system_status = TransactionStatusConstants.DONE
            self.transaction.display_status = TransactionStatusConstants.DONE
            

            self.transaction.fee_refund = float(self.transaction.fee_reserved) - float(self.transaction.total_final_fee)
            self.transaction.refund_amount = float(self.transaction.reserved_amount) - float(self.transaction.cost_amount)

        elif self.transaction.coin_amount_filled >0 :
            self.transaction.avg_price_vnd  = self.transaction.cost_amount/self.transaction.coin_amount_filled
            self.transaction.system_status = TransactionStatusConstants.OPEN
            self.transaction.display_status = TransactionStatusConstants.PARTIAL

            coin_amount_remainings = float(self.transaction.coin_amount_submitted) - float(self.transaction.coin_amount_filled)
            
            if Exchanger_Utils.get_coin_value(coin_id=self.transaction.coin_id,amount=coin_amount_remainings) < SettingUtils.get_auto_cancel_value():
                #Put Request to cancel because amount left is too low
                self.transaction.display_status = TransactionStatusConstants.REQUEST_CANCEL



        if self.transaction.display_status == TransactionStatusConstants.REQUEST_CANCEL:
            self.transaction.system_status = TransactionStatusConstants.DONE
            self.transaction.display_status = TransactionStatusConstants.CANCELED

            

            self.transaction.refund_amount = float(self.transaction.reserved_amount) - float(self.transaction.cost_amount)
            self.transaction.fee_refund = float(self.transaction.fee_reserved) - float(self.transaction.total_final_fee)


            
        
        self.transaction.updated_at = DatetimeUtils.getCurrentTime()

        self.transaction.save()

        PublishBusiness().publish_transaction(self.transaction)
        
        
        
        


    def _match_broker_order_limit_sell(self):
        print("I am runing _match_broker_order_limit_sell")
        if self.coin_setting is None:
            print("Coin Setting not found")
            return
        try:
            #Maybe there is no processing
            steps = ExchangerTransactionStepLimit.objects.filter(transaction_id=self.transaction.ID,system_status=TransactionStatusConstants.PROCESSING).all()
            if len(steps)==1:
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
                                step.final_btc_price = account_order.avg_price
                                step.final_usd_price = float(bitcoin_price.usd_bid_price)*float(account_order.avg_price)

                            step.coin_amount_filled = min(account_order.fill_quantity,step.coin_amount_submitted)
                            step.coin_amount_remainings = step.coin_amount_submitted - step.coin_amount_filled
                            step.usd_rate_vnd = SettingUtils.get_usd_rate_vnd()

                            step.coin_fee = self.coin_setting['client_sell_profit']
                            step.temp_vnd_price = float(step.final_usd_price) * float(step.usd_rate_vnd) * (100 - float(step.coin_fee))/100
                            step.final_vnd_price = max(self.transaction.submitted_price_vnd,step.temp_vnd_price)

                            step.cost_amount = MoneyUtils.round_money(number=float(step.coin_amount_filled)*float(step.final_vnd_price), currency=CoinConstants.VND)
                            step.total_fee =  MoneyUtils.round_money(number=float(step.cost_amount) * float(self.transaction.fee_percent)/100.0,currency=CoinConstants.VND)
                            step.cost_amount_after_fee = step.cost_amount - step.total_fee
                            step.final_money_added = step.cost_amount_after_fee

                            step.system_status = TransactionStatusConstants.DONE
                            step.save()


                            self.transaction.coin_amount_filled = float(self.transaction.coin_amount_filled) + float(step.coin_amount_filled)
                            self.transaction.cost_amount = float(self.transaction.cost_amount) + float(step.cost_amount)
                            self.transaction.cost_amount_after_fee = float(self.transaction.cost_amount_after_fee) + float(step.cost_amount_after_fee)
                            self.transaction.reserved_remainings = float(self.transaction.reserved_remainings)  - float(self.transaction.coin_amount_filled)
                            self.transaction.total_final_fee = float(self.transaction.total_final_fee)  + float(step.total_fee)

                            self.transaction.save()

                            try:
                                fulfill_limit_step.delay(step_id=step.ID)
                            except Exception as e:
                                capture_exception(e)

  

        except Exception as e:
            print(e)
            capture_exception(e)
            pass

        

        steps = ExchangerTransactionStepLimit.objects.filter(transaction_id=self.transaction.ID).all()
        
        
        amount_filled = 0
        total_fee = 0
        cost_amount =0
        cost_amount_after_fee = 0


        for step in steps:            
            if step.system_status == TransactionStatusConstants.PROCESSING:
                #Return if there is still someanother 
                return

        #DONE
        # self.transaction.coin_amount_filled = amount_filled
        # self.transaction.total_final_fee = total_fee
        # self.transaction.cost_amount = cost_amount
        # self.transaction.cost_amount_after_fee = cost_amount_after_fee
        # self.transaction.reserved_remainings = self.transaction.reserved_amount - self.transaction.coin_amount_filled       
        
        

        if self.transaction.reserved_remainings ==0 :
            self.transaction.avg_price_vnd  = float(self.transaction.cost_amount)/float(self.transaction.coin_amount_filled)
            self.transaction.system_status = TransactionStatusConstants.DONE
            self.transaction.display_status = TransactionStatusConstants.DONE
            self.transaction.fee_refund = 0
            self.transaction.refund_amount = 0
        elif self.transaction.coin_amount_filled >0 : 
            self.transaction.avg_price_vnd  = self.transaction.cost_amount/self.transaction.coin_amount_filled
            self.transaction.system_status = TransactionStatusConstants.OPEN
            self.transaction.display_status = TransactionStatusConstants.PARTIAL
            

            coin_amount_remainings = float(self.transaction.coin_amount_submitted) - float(self.transaction.coin_amount_filled)
            
            if Exchanger_Utils.get_coin_value(coin_id=self.transaction.coin_id,amount=coin_amount_remainings) < SettingUtils.get_auto_cancel_value():
                #Put Request to cancel because amount left is too low
                self.transaction.display_status = TransactionStatusConstants.REQUEST_CANCEL


            

        if self.transaction.display_status == TransactionStatusConstants.REQUEST_CANCEL:
            self.transaction.system_status = TransactionStatusConstants.DONE
            self.transaction.display_status = TransactionStatusConstants.CANCELED

            self.transaction.fee_refund = 0
            self.transaction.refund_amount = float(self.transaction.reserved_amount) - float(self.transaction.coin_amount_filled)


        
        self.transaction.updated_at = DatetimeUtils.getCurrentTime()
        self.transaction.save()

        PublishBusiness().publish_transaction(self.transaction)