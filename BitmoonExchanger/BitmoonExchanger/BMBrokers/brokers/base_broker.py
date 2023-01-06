
import pandas as pd
import json
from ..models import Broker_Account_Balance,BrokerCoinPriceModel, Broker_Account_Deposit_History, Broker_Account_Deposit_Address,Broker_Coin_Info,Broker_Network_Info
from ...BMUtils.utils.database_utils import DatabaseUtils
from ...BMUtils.utils.datetime_utils import DatetimeUtils

from sentry_sdk import capture_exception

import time

class BaseBroker():
    def __init__(self,broker_id):
        self.broker_id=broker_id
        
        self.ws_last_updated_time = time.time()
        

        # Balance
        # History
        # Submit Market Order
        # Submit Limit Order
        # Submit 

    
    def fetch_markets(self):
        print("Not implemented fetch_markets")
    

    def set_ws_updated_time(self):
        self.ws_last_updated_time = time.time()

    def get_ws_updated_time(self):
        return self.ws_last_updated_time


    def start_websocket(self):
        print("Not implemented")

        
    # Balance
    def fetch_balance(self):
        balances = self._do_fetch_balance()
        if not balances:
            return

        df = pd.read_json(json.dumps(balances),orient='records')

        df['coin_symbol'] = df.asset
        df['free_balance'] = df.free
        df['locked_balance'] = df.locked
        df['total_balance'] = df.locked_balance + df.free_balance            
        df['broker_id'] = self.broker_id
        df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
        df = df.drop(columns=['asset','free','locked'],axis=1)

        coin_price = BrokerCoinPriceModel.objects.filter(broker_id=self.broker_id).values("coin_symbol","usd_last_price")
        coin_price_df = pd.DataFrame(coin_price)

        

        df = df.set_index("coin_symbol")
        coin_price_df = coin_price_df.set_index("coin_symbol")

        df['total_balance_in_usd'] = df.total_balance.astype(float) * coin_price_df.usd_last_price.astype(float)

        df['total_balance_in_usd'] = df.total_balance_in_usd.fillna(-1)

        df=df.reset_index()

        DatabaseUtils.bulk_upsert(model=Broker_Account_Balance,df=df)

    def _do_fetch_balance(self):
        pass

    def fetch_history(self):
        pass

    def fetch_deposit_history(self):
        deposit_list = self._do_fetch_deposit_history()
        if deposit_list: 
            df = pd.read_json(json.dumps(deposit_list),orient='records')

            df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

            DatabaseUtils.bulk_upsert(model=Broker_Account_Deposit_History,df=df)


    def _do_fetch_deposit_history(self):
        pass

    def fetch_deposit_address(self):
        
        deposit_address = self._do_fetch_deposit_address()

        pass

    def _do_fetch_deposit_address(self):
        pass

    def fetch_coin_info(self):
        coin_info = self._do_fetch_coin_info()
        if not coin_info:
            return

        df = pd.read_json(json.dumps(coin_info),orient='records')
        
        DatabaseUtils.bulk_upsert(model=Broker_Coin_Info,df=df)

    def fetch_coin_network(self):

        try:

            coin_network_info = self._do_fetch_coin_network()

            if coin_network_info: 
                df = pd.read_json(json.dumps(coin_network_info),orient='records')

                Broker_Network_Info.objects.filter(broker_id = self.broker_id).update(is_default=False,withdraw_enable=False,deposit_enable=False)
                DatabaseUtils.bulk_upsert(model=Broker_Network_Info,df=df)
                
        except Exception as e:
            capture_exception(e)

        

    def _do_fetch_coin_network(self):
        print("Not implemented _do_fetch_coin_network")
        pass

    def _do_fetch_coin_info(self):
        pass

    def submit_order_limit(self,action,pair,amount,price):
        try:
            order = self._do_submit_order_limit(action,pair,amount,price)
            return order
        except Exception as e:
            
            capture_exception(e)
        return None

    def submit_order_market(self,action,pair,total_amount,by='default'):
        try:
            order = self._do_submit_order_market(action,pair,total_amount,by=by)
            
            return order
        except Exception as e:
            print(e)
            capture_exception(e)
        
        return None
    
    def _do_submit_order_limit(self,action,pair,amount,price):
        print("Not implemented _do_submit_order")
    
    def _do_submit_order_market(self,action,pair,total_amount,by):
        print("Not implemented _do_submit_order")
        
    
    def withdraw(self,coin_symbol,to_coin_address,tag,amount,unique_id='',network=''):
        return self._do_withdraw(coin_symbol=coin_symbol,to_coin_address=to_coin_address,tag=tag,amount=amount,unique_id=unique_id,network=network)

    def _do_withdraw(self,coin_symbol,to_coin_address,tag,amount,unique_id='',network=''):
        print("Not implemented _do_submit_order")

    def fetch_withdraw_history(self):
        self._do_fetch_withdraw_history()
        
        # for withdraw in withdrawHistory['withdrawList']:
        #     print(withdraw)

    def _do_fetch_withdraw_history(self):
        pass