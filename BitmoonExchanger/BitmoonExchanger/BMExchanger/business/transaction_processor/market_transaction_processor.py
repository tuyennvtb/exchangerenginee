from ....BMUtils.utils.constants import *
from ....BMUtils.utils.exchanger_utils import Exchanger_Utils
from ....BMUtils.utils.setting_utils import SettingUtils
from ....BMUtils.utils.money_utils import MoneyUtils

from ...models import ExchangerTransactionStepMarket
from ....BMBrokers.services.broker_trading_service import BrokerTradingService

from ....BMUtils.utils.exchanger_logger import ExchangerLogger


class MarketTransactionProcessor:
    def __init__(self,transaction,coin_setting,market_pair):
        self.transaction =transaction
        self.coin_setting = coin_setting
        self.market_pair = market_pair

    def process(self):
        print("I am running MarketTransactionProcessor")

        ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Start Transaction Processor")
        if self.transaction.action==ExchangerTransactionType.BUY:
            self._process_market_buy()
        else:
            self._process_market_sell()

    def _process_market_buy(self):
        #We have VND, Calculate Fee -> Convert to USD ->
        if self.coin_setting is None:
            print("Coin Setting not found")
            ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Coin Setting not found. Exit")
            return


        transaction_step = ExchangerTransactionStepMarket()
        transaction_step.transaction_id = self.transaction.ID
        transaction_step.user_id = self.transaction.user_id
        transaction_step.action = self.transaction.action
        transaction_step.trade_mode = self.transaction.trade_mode
        transaction_step.broker_id = self.coin_setting['broker_id']
        transaction_step.market_pair = self.market_pair['market_pair']

        
        transaction_step.coin_fee = self.coin_setting['client_buy_profit']
        #Get VND value from transaction
        transaction_step.temp_cost_amount =  self.transaction.reserved_amount
        #Calculate Fee
        transaction_step.temp_fee_amount = MoneyUtils.round_money(number= float(transaction_step.temp_cost_amount) * float(transaction_step.coin_fee)/100, currency=CoinConstants.VND)
        #Calculate Remaning Cost amount
        transaction_step.temp_cost_amount_after_fee = float(transaction_step.temp_cost_amount) - float(transaction_step.temp_fee_amount)

        usd_remanings = float(transaction_step.temp_cost_amount_after_fee) / float(SettingUtils.get_usd_rate_vnd())
        if transaction_step.market_pair.endswith(CoinConstants.USDT):
            transaction_step.market_total_amount_submitted = usd_remanings
        else:
            btc_price = Exchanger_Utils.get_bitcoin_price()
            btc_remainings  = float(usd_remanings) / float(btc_price.usd_ask_price)

            transaction_step.market_total_amount_submitted = btc_remainings

        transaction_step.coin_amount_submitted = 0
        transaction_step.vnd_match_price =  Exchanger_Utils.get_coin_price(self.transaction.coin_id).usd_rate_vnd
        transaction_step.system_status = TransactionStatusConstants.PROCESSING

        transaction_step.save()

        self.transaction.system_status  = TransactionStatusConstants.PROCESSING
        self.transaction.save()


        ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market Buy Transaction, Amount: {0}".format(transaction_step.market_total_amount_submitted))
        order_id = BrokerTradingService().submit_transaction_market(broker_id=transaction_step.broker_id,action=transaction_step.action,pair=transaction_step.market_pair,total_amount=transaction_step.market_total_amount_submitted)
        
        
        if order_id:
            transaction_step.broker_unique_id = order_id        
            transaction_step.save()
            #Successfull

            ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market Buy Transaction Success, Order ID : {0}".format(order_id))
            return True
        else:
            transaction_step.system_status = TransactionStatusConstants.ERROR
            transaction_step.save()
            self.transaction.system_status  = TransactionStatusConstants.ERROR
            self.transaction.save()

            ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market Buy Transaction Error")

            return False

    def _process_market_sell(self):

        transaction_step = ExchangerTransactionStepMarket()
        transaction_step.transaction_id = self.transaction.ID
        transaction_step.user_id = self.transaction.user_id
        transaction_step.action = self.transaction.action
        transaction_step.trade_mode = self.transaction.trade_mode
        transaction_step.broker_id = self.coin_setting['broker_id']
        transaction_step.market_pair = self.market_pair['market_pair']
        transaction_step.market_total_amount_submitted = self.transaction.market_total_amount_submitted
        transaction_step.coin_amount_submitted = transaction_step.market_total_amount_submitted
        transaction_step.vnd_match_price =  Exchanger_Utils.get_coin_price(self.transaction.coin_id).usd_rate_vnd
        transaction_step.system_status = TransactionStatusConstants.PROCESSING

        transaction_step.save()

        self.transaction.system_status  = TransactionStatusConstants.PROCESSING
        self.transaction.save()


        ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market SELL Transaction, Amount: {0}".format(transaction_step.market_total_amount_submitted))

        order_id = BrokerTradingService().submit_transaction_market(broker_id=transaction_step.broker_id,action=transaction_step.action,pair=transaction_step.market_pair,total_amount=transaction_step.market_total_amount_submitted)

        if order_id:
            transaction_step.broker_unique_id = order_id    
            transaction_step.save()

            ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market SELL Transaction Success, Order ID : {0}".format(order_id))

        else:
            transaction_step.system_status = TransactionStatusConstants.ERROR
            transaction_step.save()
            self.transaction.system_status  = TransactionStatusConstants.ERROR
            self.transaction.save()

            ExchangerLogger.log_transaction(transaction_id=self.transaction.unique_id,description="Submit Market SELL Transaction Error")

        
