from ....BMUtils.utils.constants import *
from ....BMUtils.utils.wallet_utils import WalletUtils
from ....BMUtils.utils.cache_utils import CacheUtils

from ...models import ExchangerTransactionStepLimit,ExchangerTransactionStepTrading

from django.db import transaction as django_transaction



class TransactionWalletProcessor:
    def __init__(self,transaction):
        self.transaction = transaction

    def call_to_update_wallet(self):
        if self.transaction.trade_mode == ExchangerModeConstants.LIMIT:
            self.call_to_update_wallet_limit()
        elif self.transaction.trade_mode == ExchangerModeConstants.MARKET:
            self.call_to_update_wallet_market()

    def call_to_update_wallet_limit(self):
        #{"user_id": 1, "transaction_id": "KBRLXc959", "unique_step": "KBRLXc959_234", "coin_traded_amount": 41.0, "actual_price": 12689.6198, "trade_fee": 782.0, "final_money_added": 41.0}
        
        with django_transaction.atomic():
            steps = ExchangerTransactionStepLimit.objects.select_for_update().filter(transaction_id=self.transaction.ID).all()

            wallet_fail_steps = 0
            for step in steps:
                if step.wallet_status <1 and step.wallet_request_count<10 and step.system_status == TransactionStatusConstants.DONE:
                    if step.final_money_added ==0 : 
                        step.wallet_status = 1
                        step.wallet_payload = 'Not submit because filled = 0'
                        step.save()
                    else:
                        status,payload, response = WalletUtils.complete_limit_transaction_step(transaction=self.transaction,transaction_step=step)
                        step.wallet_status = status
                        step.wallet_payload = payload
                        step.wallet_response = response
                        step.wallet_request_count+=1
                        step.save()
                        
                
                if  step.wallet_status <1 and step.system_status == TransactionStatusConstants.DONE:
                    wallet_fail_steps+= 1

        #Check for Trading BUY Transaction
        if self.transaction.action == ExchangerTransactionType.BUY:
            with django_transaction.atomic():
                steps = ExchangerTransactionStepTrading.objects.select_for_update().filter(buy_id=self.transaction.ID).all()
                for step in steps:
                    if step.wallet_buy_status <1 and step.wallet_buy_request_count < 10 and step.system_status == TransactionStatusConstants.DONE:
                        status,payload, response = WalletUtils.complete_limit_transaction_trading_buy_step(transaction=self.transaction,transaction_step=step)
                        step.wallet_buy_status = status
                        step.wallet_buy_payload = payload
                        step.wallet_buy_response = response
                        step.wallet_buy_request_count+=1
                        step.save()

                    if step.wallet_buy_status <1:
                        wallet_fail_steps+= 1


                pass
        else:
            with django_transaction.atomic():
                steps = ExchangerTransactionStepTrading.objects.select_for_update().filter(sell_id=self.transaction.ID).all()
                for step in steps:
                    if step.wallet_sell_status <1 and step.wallet_sell_request_count<10 and step.system_status == TransactionStatusConstants.DONE:
                        status,payload, response = WalletUtils.complete_limit_transaction_trading_sell_step(transaction=self.transaction,transaction_step=step)
                        step.wallet_sell_status = status
                        step.wallet_sell_payload = payload
                        step.wallet_sell_response = response
                        step.wallet_sell_request_count+=1
                        step.save()

                    if step.wallet_sell_status <1 and step.system_status == TransactionStatusConstants.DONE:
                        wallet_fail_steps+= 1

        

        if self.transaction.system_status == TransactionStatusConstants.DONE and wallet_fail_steps == 0:
            
            status,payload, response = WalletUtils.close_limit_transaction(transaction=self.transaction)
            self.transaction.wallet_status = status
            self.transaction.wallet_payload = payload
            self.transaction.wallet_response = response
            self.transaction.wallet_request_count+=1
            self.transaction.save()



    

    def call_to_update_wallet_market(self):
        cacheKey = "{0}_{1}".format(CacheKey.TRANSACTION_WALLET_CALL_LOCKING,self.transaction.unique_id)
        if self.transaction.system_status == TransactionStatusConstants.DONE and self.transaction.wallet_status <1:
            is_locked = CacheUtils.get_key(cacheKey)
            
            if CacheUtils.get_key(cacheKey):
                #Another call has already called in the last 1 minute
                pass

            CacheUtils.cache_key(key=cacheKey,value=123,ttl=60)

            status,payload,response = WalletUtils.close_market_transaction(transaction=self.transaction)
            self.transaction.wallet_status = status
            self.transaction.wallet_payload = payload
            self.transaction.wallet_response = response
            self.transaction.wallet_request_count+=1
            self.transaction.save()

            

                