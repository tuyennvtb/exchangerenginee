from ..models import ExchangerCoinSetting,ExchangerCoinPriceModel,ExchangerTransaction
import pandas as pd
import numpy as np
import time
from ...BMUtils.utils.constants import *
from ...BMUtils.utils.database_utils import DatabaseUtils
from ...BMUtils.utils.cache_utils import CacheUtils
from ...BMUtils.utils.exchanger_utils import Exchanger_Utils
from ...BMUtils.utils.setting_utils import SettingUtils
from ...BMUtils.utils.exchanger_logger import ExchangerLogger

import pandas as pd
import time
from ..tasks import process_transaction,process_trade_transaction
from django.db import transaction as django_transaction

from ..business.transaction_business import TransactionBusiness
from ..business.publish_business import PublishBusiness

from sentry_sdk import capture_exception


class RealtimeBusiness:
    def __init__(self,broker):
        self.broker = broker
        self.coin_setting_expire_time = 0

        self.publisher = PublishBusiness()

        self.coin_price_update_time = 0



    def process_usd_price(self,df):
        usd_rate_vnd = SettingUtils.get_usd_rate_vnd()

        setting_df = self.get_coin_setting_df()
        print(setting_df)
        coin_price_df = setting_df.join(df)
        coin_price_df = coin_price_df.dropna()
        coin_price_df['usd_rate_vnd'] = usd_rate_vnd

        coin_price_df['vnd_ask_price'] = coin_price_df.usd_ask_price.astype(float)*coin_price_df.usd_rate_vnd*(100.0+coin_price_df.client_buy_profit)/100.0
        coin_price_df['vnd_bid_price'] = coin_price_df.usd_bid_price.astype(float)*coin_price_df.usd_rate_vnd*(100.0-coin_price_df.client_sell_profit)/100.0

        coin_price_df=coin_price_df.drop(columns=['btc_last_price','btc_bid_price','btc_bid_price','btc_ask_price','usd_last_price'],axis=1)
        
        

        current_time = time.time()
        if current_time - self.coin_price_update_time > 9:
            print(coin_price_df)
            DatabaseUtils.bulk_upsert(ExchangerCoinPriceModel,coin_price_df)
            self.coin_price_update_time = current_time

        self.match_coin_price(coin_price_df=coin_price_df)
        
        self.publisher.publish_coin(broker_id=self.broker.broker_id,coin_price_df=coin_price_df)



    def get_coin_setting_df(self):
        current_time  = time.time()
        if self.coin_setting_expire_time < current_time or self.settings_df is None: 
            settings = ExchangerCoinSetting.objects.values("broker_id","coin_id","coin_name","coin_symbol","client_buy_profit","client_sell_profit","is_allow_limit_trade","is_allow_market_trade")
            settings_df = pd.DataFrame(settings)
            settings_df = settings_df[settings_df.broker_id == self.broker.broker_id]
            settings_df = settings_df.drop(columns=['broker_id'],axis=1).set_index("coin_symbol")
            settings_df['client_buy_profit'] = settings_df.client_buy_profit.astype(float)
            settings_df['client_sell_profit'] = settings_df.client_sell_profit.astype(float)

            self.coin_setting_expire_time = current_time + 15
            self.settings_df = settings_df

        return self.settings_df

    def match_coin_price(self,coin_price_df):
        try:
            transactions_df = self.get_transactions()
            if len(transactions_df) ==0 :
                return
            transactions_df = transactions_df[transactions_df.system_status == TransactionStatusConstants.OPEN]

            if len(transactions_df) ==0 :
                return 
            else:
                transactions_df=transactions_df.set_index('coin_id')
            coin_price_df = coin_price_df.set_index('coin_id')
            coin_price_df=coin_price_df.drop(columns=['created_at','updated_at'],axis=1)
            

            
            

            
            
            #HANDLE BUY LIMIT
            limit_transactions = transactions_df[transactions_df.trade_mode == ExchangerModeConstants.LIMIT]
            
            limit_buy_transactions_all  = limit_transactions[limit_transactions.action == ExchangerTransactionType.BUY]
            limit_sell_transactions_all  = limit_transactions[limit_transactions.action == ExchangerTransactionType.SELL]

            
            #Cross join buy and Sell
            trade_transactions = pd.merge(limit_buy_transactions_all.reset_index(), limit_sell_transactions_all.reset_index(), on ='coin_id',suffixes=['_buy','_sell'])
            #print(trade_transactions)
            # Filter by Price

            

            
            trade_transactions = trade_transactions[trade_transactions.submitted_price_vnd_buy >= trade_transactions.submitted_price_vnd_sell]
            #Get First matching by Buy
            trade_transactions = trade_transactions.sort_values(by=['submitted_price_vnd_buy','submitted_price_vnd_sell'],ascending=[False,True])
            #Filter only single ID. The output is single transaction
            # trade_transactions = trade_transactions.drop_duplicates(subset=['coin_amount_submitted_sell'],keep='first')
            
            
            
            if len(trade_transactions)>=1:
                for idx,trade_transaction in trade_transactions.iterrows():
                    self.submit_trade_transaction(buy_unique_id=trade_transaction['unique_id_buy'],sell_unique_id=trade_transaction['unique_id_sell'])

                    
                    #Submit one transaction at a time
                    return
                
                #Stop Processing if a trade transaction match because we only process one at a time
                return

            
            merged = coin_price_df.join(transactions_df)
            #merged['valid'] = merged['unique_id'].notna()
            merged = merged[merged.unique_id.notna()]
            merged = merged.reset_index().set_index('ID')


            #HANDLE BUY MARKET
            market_transactions = merged[merged.trade_mode == ExchangerModeConstants.MARKET]
            for idx,row in market_transactions.iterrows():
                self.submit_transaction(unique_id=row['unique_id'])



            #HANDLE BUY LIMIT
            limit_transactions = merged[merged.trade_mode == ExchangerModeConstants.LIMIT]
            
            limit_buy_transactions_all  = limit_transactions[limit_transactions.action == ExchangerTransactionType.BUY]
            limit_sell_transactions_all  = limit_transactions[limit_transactions.action == ExchangerTransactionType.SELL]


            #Handle Transaction Buy
            limit_buy_transactions = pd.DataFrame()
            if len(limit_buy_transactions_all) > 0:
                
                limit_buy_transactions  = limit_buy_transactions_all[limit_buy_transactions_all.submitted_price_vnd >= limit_buy_transactions_all.vnd_ask_price]
                
                for idx,row in limit_buy_transactions.iterrows():
                    self.submit_transaction(unique_id=row['unique_id'])

            
            #Handle Transaction Sell
            limit_sell_transactions = pd.DataFrame()
            if len(limit_sell_transactions_all) > 0:
                limit_sell_transactions  = limit_sell_transactions_all[limit_sell_transactions_all.submitted_price_vnd <= limit_sell_transactions_all.vnd_bid_price]
                for idx,row in limit_sell_transactions.iterrows():         
                    self.submit_transaction(unique_id=row['unique_id'])






        except Exception as e:
            capture_exception(e)
            

    def submit_transaction(self,unique_id):

        print("Sumitting Transaction : {0}".format(unique_id) )
        
        cachekey = '{0}_{1}'.format(CacheKey.TRANSACTION_SUBMIT_LOCKING,unique_id)
        if not CacheUtils.get_key(cachekey):
            CacheUtils.cache_key(cachekey,value=True,ttl=30)
            #ExchangerLogger.log_transaction(transaction_id=unique_id,description="Transaction is started type Exchanger by Realtime Engine")

            process_transaction.delay(unique_id=unique_id)

    def submit_trade_transaction(self,buy_unique_id,sell_unique_id):

        print("Sumitting Trade Transaction : {0}, {1}".format(buy_unique_id,sell_unique_id) )
        
        cachekey_buy = '{0}_{1}'.format(CacheKey.TRANSACTION_SUBMIT_LOCKING,buy_unique_id)
        cachekey_sell = '{0}_{1}'.format(CacheKey.TRANSACTION_SUBMIT_LOCKING,sell_unique_id)

        cache_buy_status = CacheUtils.get_key(cachekey_buy)
        cache_sell_status = CacheUtils.get_key(cachekey_sell)
        
        
        if not CacheUtils.get_key(cachekey_buy) and not CacheUtils.get_key(cachekey_sell):
            
            CacheUtils.cache_key(cachekey_buy,value=True,ttl=30)
            CacheUtils.cache_key(cachekey_sell,value=True,ttl=30)

            #ExchangerLogger.log_transaction(transaction_id=buy_unique_id,description="Transaction is started type Trade by Realtime Engine")
            #ExchangerLogger.log_transaction(transaction_id=sell_unique_id,description="Transaction is started type Trade by Realtime Engine")
            process_trade_transaction.delay(buy_unique_id=buy_unique_id,sell_unique_id=sell_unique_id)

    def get_transactions(self):
        transactions = ExchangerTransaction.objects.filter(system_status__in=[TransactionStatusConstants.OPEN,TransactionStatusConstants.ERROR]).values()
        transactions_df = pd.DataFrame(transactions)
        if len(transactions_df)>0:

            transaction_to_cancel_df = transactions_df[transactions_df.display_status == TransactionStatusConstants.REQUEST_CANCEL]
            self.handle_transactions_cancel(transactions_df=transaction_to_cancel_df)
            transaction_to_process_df = transactions_df[transactions_df.display_status != TransactionStatusConstants.REQUEST_CANCEL]

            return transaction_to_process_df

        
        return transactions_df
        

    def handle_transactions_cancel(self,transactions_df):
        if len(transactions_df) == 0:
            return
        for idx,row in transactions_df.iterrows():

            try:

                with django_transaction.atomic():                
                    transaction = ExchangerTransaction.objects.filter(unique_id=row['unique_id']).get()
                    if transaction.system_status == TransactionStatusConstants.OPEN or transaction.system_status == TransactionStatusConstants.ERROR  or transaction.system_status== TransactionStatusConstants.DONE:
                        

                        if transaction.action == ExchangerTransactionType.BUY:
                            transaction.fee_refund = float(transaction.fee_reserved) - float(transaction.total_final_fee)
                            transaction.refund_amount = float(transaction.reserved_amount) - float(transaction.cost_amount)  
                        else:
                            transaction.fee_refund = 0
                            transaction.refund_amount = float(transaction.reserved_amount)  - float(transaction.coin_amount_filled)

                        if transaction.coin_amount_filled >0 :
                            transaction.avg_price_vnd = float(transaction.cost_amount) / float(transaction.coin_amount_filled )

                        

                        transaction.system_status=TransactionStatusConstants.DONE
                        transaction.display_status = TransactionStatusConstants.CANCELED
                        transaction.save()

                        
                        self.publisher.publish_transaction(transaction)

                        TransactionBusiness(unique_id=row['unique_id']).call_to_update_wallet()
            except Exception as  e:
                capture_exception(e)
        

        
