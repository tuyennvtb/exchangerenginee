import redis
from django.conf import settings
from ..models import ExchangerCoinPriceModel,ExchangerCoinSetting,ExchangerTransaction
from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.setting_utils import SettingUtils
from ...BMUtils.utils.cache_utils import CacheUtils
import json
import pandas as pd
import time
from sentry_sdk import capture_exception
from ...BMBrokers.common.broker_settings import Broker_Setting
from ...BMUtils.utils.exchanger_utils import Exchanger_Utils
from django.db.models import Min, Max


from ...BMUtils.utils.constants import *
class PublishBusiness:
    def __init__(self):
        self.redis = None
        self._init_redis_connection()

        self.cmc_last_update = 0
        self.cmc_df = None

        self._update_cmc_df()
        
    def _init_redis_connection(self):
        self.redis = redis.from_url(url=settings.REDIS_URL)

    def _update_cmc_df(self):
        now = time.time()
        if self.cmc_df is None or self.cmc_last_update + 5*60 > now:
            cmc = Exchanger_Utils.get_cmc_info()
            cmc_df = pd.DataFrame(cmc)
            cmc_df = cmc_df.set_index('coin_id')

            self.cmc_last_update = now
            self.cmc_df = cmc_df

        return self.cmc_df
        
    def publish_coin(self,broker_id,coin_price_df):
        
        self._update_cmc_df()

        coin_price_df = coin_price_df.set_index('coin_id')
        
        merged_coin_price_df = coin_price_df.join(self.cmc_df)

        merged_coin_price_df= merged_coin_price_df.reset_index()
        
        
        Now = DatetimeUtils.getUnixTime()
        data = merged_coin_price_df.to_json(orient="records")

        self.redis.set('exchange_coin_price_broker_v2/{0}'.format(broker_id),data)
        data = json.loads(data)
        #{"time": 1608407793.4281962, "data": {"coin_id": "zencash", "coin_name": "Horizen", "client_buy_profit": 1.0, "client_sell_profit": 1.0, "broker_id": "binance", "created_at": "2020-12-19 19:56:32", "updated_at": "2020-12-19 19:56:32", "coin_symbol": "ZEN", "usd_bid_price": "12.19100000", "usd_ask_price": "12.21300000", "status": 1.0, "usd_rate_vnd": 23000.0, "vnd_ask_price": 283707.99, "vnd_bid_price": 277589.07}}
       
        for row in data:
            try:            
                message = json.dumps({
                    'time': Now,
                    'data':row
                })

                self.redis.set('exchange_coin_price_v2/{0}'.format(row['coin_id']),message)
                self.redis.publish('exchange_coin_price_channel_v2/{0}'.format(row['coin_id']),message)
            except Exception as e:
                capture_exception(e)
                self._init_redis_connection()

        if broker_id == 'binance':
            self.publish_coin_bm()

    def publish_coin_bm(self):

        #pass
        try:

            now = time.time()
            
            bid_coins = ExchangerTransaction.objects.filter(coin_id__in=['tether','hakka-finance'],system_status=TransactionStatusConstants.OPEN, trade_mode=ExchangerModeConstants.LIMIT, action=ExchangerTransactionType.BUY).values("coin_id").annotate(vnd_bid_price=Max('submitted_price_vnd'))
            ask_coins = ExchangerTransaction.objects.filter(coin_id__in=['tether','hakka-finance'],system_status=TransactionStatusConstants.OPEN, trade_mode=ExchangerModeConstants.LIMIT, action=ExchangerTransactionType.SELL).values("coin_id").annotate(vnd_ask_price=Min('submitted_price_vnd'))
            
            tether_bid_price = 10000
            tether_ask_price = 30000

            hakka_bid_price = 10000
            hakka_ask_price = 30000

            bm_coins = []

            for coin in bid_coins:
                # print(tether[1]['vnd_ask_price'])
                
                if coin['coin_id'] == 'tether':
                    tether_bid_price = float(coin['vnd_bid_price'])

                if coin['coin_id'] == 'hakka-finance':
                    hakka_bid_price = float(coin['vnd_bid_price'])
            
            for coin in ask_coins:
                # print(tether[1]['vnd_ask_price'])
                
                if coin['coin_id'] == 'tether':
                    tether_ask_price = float(coin['vnd_ask_price'])

                if coin['coin_id'] == 'hakka-finance':
                    hakka_ask_price = float(coin['vnd_ask_price'])
        except Exception as e:
            capture_exception(e)

        
       
        try:

            data = {
                        "coin_id": "tether",
                        "coin_name": "Tether",
                        "client_buy_profit": 0,
                        "client_sell_profit": 0,
                        "broker_id": "Bitmoon",
                        "created_at": "2020-12-19 19:56:32",
                        "updated_at": "2020-12-19 19:56:32",
                        "coin_symbol": "USDT", 
                        "usd_bid_price": 1,
                        "usd_ask_price": 1,
                        "status": 1, 
                        "usd_rate_vnd": 23000.0, 
                        "vnd_ask_price": tether_ask_price,
                        "vnd_bid_price": tether_bid_price,
                        "rank":1000,
                        "volume_usd_24h":76897654343,
                        "percent_change_1h":3.68,
                        "percent_change_24h": 2.86
                        }
                

            bm_coins.append(data)
            message=json.dumps( {
                "time":now,
                "data": data
                    
                })
          

            
            self.redis.set('exchange_coin_price_v2/{0}'.format('tether'),message)
            self.redis.publish('exchange_coin_price_channel_v2/{0}'.format('tether'),message)

        except Exception as e:
            capture_exception(e)

        
        try:
            data = {
                    "coin_id": "hakka-finance",
                    "coin_name": "Hakka Finance",
                    "client_buy_profit": 1,
                    "client_sell_profit": 1,
                    "broker_id": "Bitmoon",
                    "created_at": "2020-12-19 19:56:32",
                    "updated_at": "2020-12-19 19:56:32",
                    "coin_symbol": "HAKKA", 
                    "usd_bid_price": 1,
                    "usd_ask_price": 1,
                    "status": 1, 
                    "usd_rate_vnd": 23000.0, 
                    "vnd_ask_price": hakka_ask_price,
                    "vnd_bid_price": hakka_bid_price,
                    "rank":1000,
                    "volume_usd_24h":800000000,
                    "percent_change_1h":2.55,
                    "percent_change_24h": 1.55


                }
            
           
            
            bm_coins.append(data)

            message=json.dumps({
                "time":now,
                "data": data
                
                    
                } )

            
            


            self.redis.set('exchange_coin_price_v2/{0}'.format('hakka-finance'),message)
            self.redis.publish('exchange_coin_price_channel_v2/{0}'.format('hakka-finance'),message)

        except Exception as e:
            capture_exception(e)

        
        self.redis.set('exchange_coin_price_broker_v2/{0}'.format('Bitmoon'),json.dumps(bm_coins))

    def publish_coins(self):

        try:
            data = []
            for broker in Broker_Setting.BROKERS:
                broker_instance = broker()
                broker_data= self.redis.get('exchange_coin_price_broker_v2/{0}'.format(broker_instance.broker_id))
                try:
                    if broker_data is not None:
                        broker_data = json.loads(broker_data)
                        data  = data + broker_data
                except:
                    pass

            bm_data = self.redis.get('exchange_coin_price_broker_v2/{0}'.format('Bitmoon'))
            if bm_data is not None:
                bm_data = json.loads(bm_data)
                data  = data + bm_data
            
                            
            message = json.dumps({
                'time': DatetimeUtils.getUnixTime(),
                'data': data
            })       

            self.redis.set('exchange_coin_price_v2',message)
            self.redis.publish('exchange_coin_price_channel_v2',message)            

        except Exception as e:
            
            capture_exception(e)
            self._init_redis_connection()

            
    def publish_transaction(self,transaction):
        data = {
            'id': transaction.ID,
            'transaction_id': transaction.unique_id,
            'user_id': int(transaction.user_id),
            'unique_id': transaction.unique_id,
            'base_currency': transaction.base_currency,
            'coin_id': transaction.coin_id,
            'trade_mode':transaction.trade_mode,
            'action':transaction.action,
            'coin_amount_submitted': float(transaction.coin_amount_submitted),
            'reserved_amount': float(transaction.reserved_amount or 0),
            'submitted_price_vnd':float(transaction.submitted_price_vnd or 0),
            'estimate_vnd_amount': float(transaction.estimate_vnd_amount or 0),
            'fee_reserved': float(transaction.fee_reserved or 0),
            'coin_amount_filled': float(transaction.coin_amount_filled or 0) ,
            'avg_price_vnd': float(transaction.avg_price_vnd or 0),
            'total_final_fee': float(transaction.total_final_fee or 0),
            'cost_amount': float(transaction.cost_amount or 0),
            'cost_amount_after_fee': float(transaction.cost_amount_after_fee or 0),
            'market_total_amount_submitted':float(transaction.market_total_amount_submitted or 0),
            'market_total_amount_filled':float(transaction.market_total_amount_filled or 0),           
            'final_money_added': float(transaction.final_money_added or 0),
            'refund_amount': float(transaction.refund_amount or 0),            
            'status': transaction.display_status,
            'created_at': DatetimeUtils.formatTime(transaction.created_at),
            
        }

        message = json.dumps({
            'time': DatetimeUtils.getUnixTime(),
            'data': data
        })

        

        try:
            self.redis.set('exchange_transaction_user/{0}'.format(transaction.user_id),message)
            self.redis.publish('exchange_transaction/{0}'.format(transaction.user_id),message)            

        except Exception as e:
            capture_exception(e)
            self._init_redis_connection()


    def publish_coin_settings(self):
        Now = DatetimeUtils.getUnixTime()
        expire_time = Now + 600

        usd_baseprice = SettingUtils.get_usd_rate_vnd()

        list_settings = []
        coins = list(ExchangerCoinSetting.objects.all())
        for coin in coins:
            
            market_pair = Exchanger_Utils.get_market_pair(broker_id=coin.broker_id,coin_id=coin.coin_id)

            
            
            if market_pair:
                list_settings.append({
                    'pub_time': Now,
                    'enable_trade': 1,
                    'expire_time':expire_time,
                    'coin_id': coin.coin_id,
                    'coin': coin.coin_symbol,
                    'buy_profit' : float(coin.client_buy_profit),
                    'sell_profit': float(coin.client_sell_profit),
                    'broker_code': coin.broker_id,
                    'enabled': coin.status,
                    'usd_baseprice': float(usd_baseprice),
                    'base_currency':market_pair['base_currency'],
                    'is_allow_market_trade':coin.is_allow_market_trade,
                    'is_allow_limit_trade':coin.is_allow_limit_trade
                })

                

        list_settings.append({
                    'pub_time': Now,
                    'enable_trade': 1,
                    'expire_time':expire_time,
                    'coin_id': 'tether',
                    'coin': 'USDT',
                    'buy_profit' : 0,
                    'sell_profit': 0,
                    'broker_code': 'Bitmoon',
                    'enabled': 1,
                    'usd_baseprice': float(usd_baseprice),
                    'base_currency': 'USDT',
                    'is_allow_market_trade':0,
                    'is_allow_limit_trade':1
        })

        list_settings.append({
                    'pub_time': Now,
                    'enable_trade': 1,
                    'expire_time':expire_time,
                    'coin_id': 'hakka-finance',
                    'coin': 'USDT',
                    'buy_profit' : 1,
                    'sell_profit': 1,
                    'broker_code': 'Bitmoon',
                    'enabled': 1,
                    'usd_baseprice': float(usd_baseprice),
                    'base_currency': 'USDT',
                    'is_allow_market_trade':0,
                    'is_allow_limit_trade':1

        })

        # print(list_settings)
        #Publish:
        try:
            
            for coin_setting in list_settings:            
                self.redis.set("exchange_publisher_v2:{0}".format(coin_setting['coin_id']),json.dumps(coin_setting))
                self.redis.set("exchange_publisher_coin_v2:{0}".format(coin_setting['coin']).lower(),json.dumps(coin_setting))
        except Exception as e:
            capture_exception(e)
            self._init_redis_connection()

        try:
                self.redis.set("exchange_publisher_list_v2",json.dumps(list_settings))
        except Exception as e:
            capture_exception(e)
            self._init_redis_connection()
        
        

    def publish_orderbook(self):
        self.publish_orderbook_buy()
        self.publish_orderbook_sell()


        
    def publish_orderbook_buy(self):

        transactions = ExchangerTransaction.objects.filter(display_status=TransactionStatusConstants.OPEN, trade_mode=ExchangerModeConstants.LIMIT).values("action","coin_id","submitted_price_vnd","coin_amount_submitted","coin_amount_filled","user_id")
        if len(transactions) == 0:
            return
        transaction_df = pd.DataFrame(transactions)
        transaction_df['Quantity'] = transaction_df.coin_amount_submitted - transaction_df.coin_amount_filled
        transaction_df['Rate'] = transaction_df.submitted_price_vnd
        
        transaction_df=transaction_df.drop(['coin_amount_submitted','coin_amount_filled','submitted_price_vnd'],axis=1)
        transaction_df['user_id'] = transaction_df.user_id.astype(str)

        transaction_df_buy = transaction_df[transaction_df.action ==ExchangerTransactionType.BUY]
        if len(transaction_df_buy) == 0:
            return

        transaction_df_buy_user = transaction_df_buy.groupby(['coin_id','Rate'])['user_id'].apply(','.join).reset_index().set_index(['coin_id','Rate'])
        transaction_df_buy_quantity = transaction_df_buy.groupby(['coin_id','Rate'])['Quantity'].agg('sum').reset_index().set_index(['coin_id','Rate'])


        transaction_df_buy_agg = transaction_df_buy_user.join(transaction_df_buy_quantity).reset_index()
        #print(transaction_df_buy_agg)        
        publish_data = transaction_df_buy_agg.to_json(orient="records")
        publish_data = json.loads(publish_data)

        buy_orderbook = {

        }

        
        new_list = []

        for coin_data in publish_data:
            coin_info = {
                    'Rate': coin_data['Rate'],
                    'Quantity':  coin_data['Quantity'],
                    'users_id': coin_data['user_id']

                }
            if coin_data['coin_id'] not in buy_orderbook:
                buy_orderbook[coin_data['coin_id']] = [coin_info]
            else:
                buy_orderbook[coin_data['coin_id']].append(coin_info)

            new_list.append(coin_data['coin_id'])

        
        for coin_id in buy_orderbook:           
            self.redis.set("orderbook_{0}_buy_data".format(coin_id),json.dumps(buy_orderbook[coin_id]),60)
            self.redis.publish("orderbook_{0}_buy".format(coin_id),json.dumps(buy_orderbook[coin_id]))

        cache_key = "orderbook_buy_data_list"
        old_list = CacheUtils.get_key(cache_key)
        if old_list:
            diff_list = list(set(old_list) - set(new_list))
            for coin_id in diff_list:
                self.redis.set("orderbook_{0}_buy_data".format(coin_id),json.dumps([]),60)
                self.redis.publish("orderbook_{0}_buy".format(coin_id),json.dumps([]))

        CacheUtils.cache_key(key=cache_key,value=new_list)



    def publish_orderbook_sell(self):

        transactions = ExchangerTransaction.objects.filter(display_status=TransactionStatusConstants.OPEN, trade_mode=ExchangerModeConstants.LIMIT).values("action","coin_id","submitted_price_vnd","coin_amount_submitted","coin_amount_filled","user_id")

        if len(transactions) == 0:
            return
        transaction_df = pd.DataFrame(transactions)
        transaction_df['Quantity'] = transaction_df.coin_amount_submitted - transaction_df.coin_amount_filled
        transaction_df['Rate'] = transaction_df.submitted_price_vnd
        
        transaction_df=transaction_df.drop(['coin_amount_submitted','coin_amount_filled','submitted_price_vnd'],axis=1)
        transaction_df['user_id'] = transaction_df.user_id.astype(str)

        transaction_df_sell = transaction_df[transaction_df.action ==ExchangerTransactionType.SELL]

        if len(transaction_df_sell) == 0:
            return

        transaction_df_sell_user = transaction_df_sell.groupby(['coin_id','Rate'])['user_id'].apply(','.join).reset_index().set_index(['coin_id','Rate'])
        transaction_df_sell_quantity = transaction_df_sell.groupby(['coin_id','Rate'])['Quantity'].agg('sum').reset_index().set_index(['coin_id','Rate'])


        transaction_df_sell_agg = transaction_df_sell_user.join(transaction_df_sell_quantity).reset_index()
        #print(transaction_df_buy_agg)        
        publish_data = transaction_df_sell_agg.to_json(orient="records")
        publish_data = json.loads(publish_data)

        sell_orderbook = {

        }

        new_list = []

        for coin_data in publish_data:
            coin_info = {
                    'Rate': coin_data['Rate'],
                    'Quantity':  coin_data['Quantity'],
                    'users_id': coin_data['user_id']

                }
            if coin_data['coin_id'] not in sell_orderbook:
                sell_orderbook[coin_data['coin_id']] = [coin_info]
            else:
                sell_orderbook[coin_data['coin_id']].append(coin_info)

            
            new_list.append(coin_data['coin_id'])

        
        for coin_id in sell_orderbook:           
            self.redis.set("orderbook_{0}_sell_data".format(coin_id),json.dumps(sell_orderbook[coin_id]),60)
            self.redis.publish("orderbook_{0}_sell".format(coin_id),json.dumps(sell_orderbook[coin_id]))

        cache_key = "orderbook_sell_data_list"
        old_list = CacheUtils.get_key(cache_key)
        if old_list:
            diff_list = list(set(old_list) - set(new_list))
            for coin_id in diff_list:
                self.redis.set("orderbook_{0}_sell_data".format(coin_id),json.dumps([]),60)
                self.redis.publish("orderbook_{0}_sell".format(coin_id),json.dumps([]))

        CacheUtils.cache_key(key=cache_key,value=new_list)



