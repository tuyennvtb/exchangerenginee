from ...BMUtils.utils.database_utils import DatabaseUtils
from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.constants import CoinConstants

from ..models import BrokerMarketPairModel, BrokerCoinPriceModel
import threading
import time
import sys

import os
import psutil


from sentry_sdk import capture_exception


class RealtimeBusiness:
    def __init__(self,broker,exchanger_realtime_service):
        self.broker = broker
        self.exchanger_realtime_service = exchanger_realtime_service

        self.market_price_last_updated_time = 0
        self.broker_coin__price_last_updated_time = 0

        
        
    
    def start(self):
        print("Starting Thread")
        # _thread.start_new_thread(self.run,()) 
        x = threading.Thread(target=self.run, args=())
        x.start()
        print("Starting Thread Done" )

    def run(self):
        
        while(True):
            time.sleep(0.5)
            # print("Run now Realtime Business for : {0}".format(self.broker.broker_id))

            tickers = self.broker.get_tickers()
            
            bitcoin_ticker = self.broker.get_bitcoin_ticker()

            
            if len(tickers)==0 or bitcoin_ticker is None:
                continue

            print(self.broker.broker_id, self.broker.get_ws_updated_time())
            if time.time() > self.broker.get_ws_updated_time() + 2*60:
                
                self.kill_myself()
                # It is too late, exit


            try:
                
                self.process_market_data(tickers,bitcoin_ticker)
            except:
                pass

    def kill_myself(self):

        current_system_pid = os.getpid()

        print(current_system_pid)

        print("I AM KILLING MYSELF")

        ThisSystem = psutil.Process(current_system_pid)
        ThisSystem.terminate()
        

        pass
    
    def process_market_data(self,df,bitcoin):

        #Fix : (1062, "Duplicate entry 'binance-XTZUPUSDT' for key 'broker_market_pair_broker_id_market_pair_8655da97_uniq'")

        # df = df.drop_duplicates(subset=['broker_id','market_pair'],keep='last')

        
        self._save_market_price(df=df)
        
        usd_coin_price_df = self.calculate_price(df,bitcoin)
        

        self.exchanger_realtime_service.process_usd_price(df=usd_coin_price_df)
        

    def _save_market_price(self,df):
        try:
            Now = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
            df['created_at'] =  Now
            df['updated_at'] =  Now
            DatabaseUtils.bulk_upsert(BrokerMarketPairModel,df)
        except Exception as e:
            capture_exception(e)
            

        
        current_time = time.time()     

        #Skip if updated less than 10 seconds ago
        if current_time - self.market_price_last_updated_time < 10:    
             
            return

        self.market_price_last_updated_time = current_time

          



        
        

        
        df=df.dropna()      

        
        
        DatabaseUtils.bulk_upsert(BrokerMarketPairModel,df)

    def calculate_price(self,df,bitcoin):
        
        direct_coins_df = df[df.base_currency == CoinConstants.USDT]
        direct_coins_df['coin_symbol'] = direct_coins_df['market_currency']
        direct_coins_df['usd_last_price'] = direct_coins_df['last_price']
        direct_coins_df['usd_bid_price'] = direct_coins_df['bid_price']
        direct_coins_df['usd_ask_price'] = direct_coins_df['ask_price']

        direct_coins_df['btc_last_price'] = direct_coins_df['last_price'].astype(float) / bitcoin['last_price']
        direct_coins_df['btc_bid_price'] = direct_coins_df['bid_price'].astype(float) / bitcoin['bid_price']
        direct_coins_df['btc_ask_price'] = direct_coins_df['ask_price'].astype(float) /  bitcoin['ask_price']

        direct_coins_df = direct_coins_df.set_index('market_currency')
        direct_coins_df = direct_coins_df.drop(columns=['base_currency','last_price','bid_price','ask_price','market_pair','status'],axis=1)

        direct_coins_df['status'] = 1


        direct_coin_lists = list(direct_coins_df.index)

        

        two_ways_coins_df = df[df.base_currency == CoinConstants.BITCOIN]
        two_ways_coins_df['direct'] = [True if market_currency in direct_coin_lists else False for market_currency in two_ways_coins_df.market_currency]
        two_ways_coins_df = two_ways_coins_df[two_ways_coins_df.direct == False]


        two_ways_coins_df['coin_symbol'] = two_ways_coins_df.market_currency    

        two_ways_coins_df['btc_last_price'] = two_ways_coins_df.last_price
        two_ways_coins_df['btc_bid_price'] = two_ways_coins_df.bid_price
        two_ways_coins_df['btc_ask_price'] = two_ways_coins_df.ask_price

        two_ways_coins_df['usd_last_price'] = two_ways_coins_df.btc_last_price.astype(float) * bitcoin['last_price']
        two_ways_coins_df['usd_bid_price'] = two_ways_coins_df.btc_bid_price.astype(float) * bitcoin['bid_price']
        two_ways_coins_df['usd_ask_price'] = two_ways_coins_df.btc_ask_price.astype(float) * bitcoin['ask_price']
        


        two_ways_coins_df = two_ways_coins_df.set_index('market_currency')
        two_ways_coins_df = two_ways_coins_df.drop(columns=['base_currency','last_price','bid_price','ask_price','market_pair','status','direct'],axis=1)
        two_ways_coins_df['status'] = 1

        all_coins_df = direct_coins_df.append(two_ways_coins_df)
        all_coins_df=all_coins_df.dropna()


        current_time = time.time()
        if current_time - self.broker_coin__price_last_updated_time > 8:
            DatabaseUtils.bulk_upsert(BrokerCoinPriceModel,all_coins_df)
            self.broker_coin__price_last_updated_time = current_time


        return all_coins_df
