from ..models import ExchangerTransaction,ExchangerTransactionStepTrading

from ...BMUtils.utils.money_utils import MoneyUtils
from ...BMUtils.utils.cache_utils import CacheUtils
from ...BMUtils.utils.constants import *
from django.db import transaction as django_transaction

from .transaction_processor.transaction_wallet_processor import TransactionWalletProcessor
from .publish_business import PublishBusiness

from ..tasks_publishing import publish_orderbook


class TradeTransactionBusiness:
    def __init__(self,buy_unique_id,sell_unique_id):
        self.buy_unique_id = buy_unique_id
        self.sell_unique_id = sell_unique_id

    def process(self):

        with django_transaction.atomic():

            buy_transaction = ExchangerTransaction.objects.filter(unique_id=self.buy_unique_id).get()            
            sell_transaction = ExchangerTransaction.objects.filter(unique_id=self.sell_unique_id).get()

            if buy_transaction.system_status != TransactionStatusConstants.OPEN or sell_transaction.system_status != TransactionStatusConstants.OPEN:
                return 


            


            
        
            buy_transaction.system_status = TransactionStatusConstants.PROCESSING
            sell_transaction.system_status = TransactionStatusConstants.PROCESSING

            buy_transaction.save()
            sell_transaction.save()

            
            leading_action = 'BUY'
            final_vnd_price = buy_transaction.submitted_price_vnd
            if sell_transaction.ID < buy_transaction.ID:
                leading_action = 'SELL'
                final_vnd_price = sell_transaction.submitted_price_vnd

            buy_amount_remanings = buy_transaction.coin_amount_submitted - buy_transaction.coin_amount_filled
            sell_amount_remanings = sell_transaction.coin_amount_submitted - sell_transaction.coin_amount_filled

            coin_amount = min(sell_amount_remanings,buy_amount_remanings)

            



            trading_step = ExchangerTransactionStepTrading()
            trading_step.coin_id = buy_transaction.coin_id
            trading_step.unique_id ="{0}_{1}".format(buy_transaction.unique_id,sell_transaction.unique_id)
            trading_step.leading_action = leading_action
            trading_step.coin_amount = coin_amount
            trading_step.final_vnd_price = final_vnd_price
            trading_step.cost_amount = MoneyUtils.round_money(number=float(trading_step.coin_amount) * float(trading_step.final_vnd_price),currency=CoinConstants.VND)


            
            trading_step.buy_id = buy_transaction.ID
            trading_step.buy_user_id = buy_transaction.user_id
            trading_step.buy_fee_percent = buy_transaction.fee_percent


            trading_step.buy_fee = MoneyUtils.round_money(number=float(trading_step.cost_amount) * float(trading_step.buy_fee_percent)/100.0,currency=CoinConstants.VND)
            trading_step.cost_amount_after_fee_buy = trading_step.cost_amount + trading_step.buy_fee
            trading_step.final_money_added_buy = trading_step.coin_amount

            

            trading_step.sell_id = sell_transaction.ID
            trading_step.sell_user_id = sell_transaction.user_id
            trading_step.sell_fee_percent = sell_transaction.fee_percent
            trading_step.sell_fee = MoneyUtils.round_money(number=float(trading_step.cost_amount) * float(trading_step.sell_fee_percent)/100.0,currency=CoinConstants.VND)
            trading_step.cost_amount_after_fee_sell = trading_step.cost_amount - trading_step.sell_fee
            trading_step.final_money_added_sell = trading_step.cost_amount_after_fee_sell

            trading_step.exchanger_total_fee = trading_step.buy_fee + trading_step.sell_fee
            trading_step.system_status = TransactionStatusConstants.DONE
            trading_step.save()
            

            buy_transaction.coin_amount_filled = buy_transaction.coin_amount_filled + trading_step.coin_amount
            buy_transaction.cost_amount = float(buy_transaction.cost_amount) + float(trading_step.cost_amount)
            buy_transaction.cost_amount_after_fee = float(buy_transaction.cost_amount_after_fee) + float(trading_step.cost_amount_after_fee_buy)
            buy_transaction.reserved_remainings = float(buy_transaction.reserved_amount) - float(buy_transaction.cost_amount)
            buy_transaction.total_final_fee = float(buy_transaction.total_final_fee) + float(trading_step.buy_fee)
            
            
            sell_transaction.coin_amount_filled = float(sell_transaction.coin_amount_filled) + float(trading_step.coin_amount)
            sell_transaction.cost_amount = float(sell_transaction.cost_amount) + float(trading_step.cost_amount)
            sell_transaction.cost_amount_after_fee = float(sell_transaction.cost_amount_after_fee) + float(trading_step.cost_amount_after_fee_sell)
            sell_transaction.reserved_remainings = float(sell_transaction.reserved_amount) - float(sell_transaction.coin_amount_filled)
            sell_transaction.total_final_fee = float(sell_transaction.total_final_fee) + float(trading_step.sell_fee)
            



            print("Compare Buy: {0}, {1} ".format(buy_transaction.coin_amount_filled,buy_transaction.coin_amount_submitted))

            print("Compare SELL: {0}, {1} ".format(sell_transaction.coin_amount_filled,sell_transaction.coin_amount_submitted))
            if float(buy_transaction.coin_amount_filled) == float(buy_transaction.coin_amount_submitted):
                buy_transaction.system_status = TransactionStatusConstants.DONE
                buy_transaction.display_status = TransactionStatusConstants.DONE
            elif buy_transaction.display_status == TransactionStatusConstants.REQUEST_CANCEL:
                buy_transaction.system_status = TransactionStatusConstants.DONE
                buy_transaction.display_status = TransactionStatusConstants.CANCELED
            else:
                buy_transaction.system_status = TransactionStatusConstants.OPEN
            
            if float(sell_transaction.coin_amount_filled) == float(sell_transaction.coin_amount_submitted):
                sell_transaction.system_status = TransactionStatusConstants.DONE
                sell_transaction.display_status = TransactionStatusConstants.DONE

            elif sell_transaction.display_status == TransactionStatusConstants.REQUEST_CANCEL:
                sell_transaction.system_status = TransactionStatusConstants.DONE
                sell_transaction.display_status = TransactionStatusConstants.CANCELED
            else:
                sell_transaction.system_status = TransactionStatusConstants.OPEN


            if buy_transaction.system_status == TransactionStatusConstants.DONE:
                buy_transaction.avg_price_vnd = float(buy_transaction.cost_amount)/float(buy_transaction.coin_amount_filled)
                buy_transaction.refund_amount = float(buy_transaction.reserved_amount) - float(buy_transaction.cost_amount)
                buy_transaction.fee_refund = float(buy_transaction.fee_reserved) - float(buy_transaction.total_final_fee)

            if sell_transaction.system_status == TransactionStatusConstants.DONE:
                sell_transaction.avg_price_vnd = float(sell_transaction.cost_amount)/float(sell_transaction.coin_amount_filled)
                sell_transaction.refund_amount = float(sell_transaction.reserved_amount) - float(sell_transaction.coin_amount_filled)
                sell_transaction.fee_refund = 0

            


            buy_transaction.save()
            sell_transaction.save()

            PublishBusiness().publish_transaction(transaction=buy_transaction)
            PublishBusiness().publish_transaction(transaction=sell_transaction)


            cachekey_buy = '{0}_{1}'.format(CacheKey.TRANSACTION_SUBMIT_LOCKING,self.buy_unique_id)
            cachekey_sell = '{0}_{1}'.format(CacheKey.TRANSACTION_SUBMIT_LOCKING,self.sell_unique_id)

            CacheUtils.remove_key(cachekey_buy)
            CacheUtils.remove_key(cachekey_sell)

            django_transaction.on_commit(self.call_to_update_wallet)

        publish_orderbook.delay()
        
    def call_to_update_wallet(self):
        with django_transaction.atomic():
            transaction = ExchangerTransaction.objects.filter(unique_id=self.buy_unique_id).get()
            if transaction.wallet_status <=0 and transaction.wallet_request_count < 10:
                TransactionWalletProcessor(transaction=transaction).call_to_update_wallet()

        
        with django_transaction.atomic():
            transaction = ExchangerTransaction.objects.filter(unique_id=self.sell_unique_id).get()
            if transaction.wallet_status <=0 and transaction.wallet_request_count < 10:
                TransactionWalletProcessor(transaction=transaction).call_to_update_wallet()