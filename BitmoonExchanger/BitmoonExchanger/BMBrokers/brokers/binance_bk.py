from .base_broker import BaseBroker
from binance.client import Client
from binance.exceptions import BinanceAPIException

import threading

from binance import BinanceSocketManager,ThreadedWebsocketManager
import time
import pandas as pd
import json
import math
from ..business.realtime_business import RealtimeBusiness
from ..business.broker_business import BrokerBusiness

from ...BMUtils.utils.constants import CoinConstants

from ..models import BrokerAccount,Broker_Account_Order,Broker_Account_Order_Fill,Broker_Account_Balance,BrokerCoinPriceModel,Broker_Account_Deposit_Address,Broker_Withdraw_History

from binance import enums

from ...BMUtils.utils.cache_utils import CacheUtils
from ...BMUtils.utils.constants import CacheKey
from ...BMUtils.utils.constants import *
from ...BMUtils.utils.exchanger_logger import ExchangerLogger
from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.database_utils import DatabaseUtils
from ...BMUtils.utils.encryption_utils import EncryptionUtils

from sentry_sdk import capture_exception



class BrokerBinance(BaseBroker):
    
    STREAM_BTCUSDT = "btcusdt@ticker"

    
    def __init__(self):

        super(BrokerBinance, self).__init__(broker_id='binance')        
        self.client = Client()
        self.btcusdt = None

        self.streams_dict = {}

        self.account = None

    
    def start_websocket_thread(self):

        while True:
            try:
                streams = self.stream_list()        
                twm = ThreadedWebsocketManager()
                twm.start()
                twm.start_multiplex_socket(callback=self.process_m_message, streams=streams)            
                twm.join()
            except Exception as e:
                capture_exception(e)


    def start_websocket(self):

        

        # bm = BinanceSocketManager(self.client)
        

        
        # pass a list of stream names
        # conn_key = bm.multiplex_socket(streams, self.process_m_message)
        # bm.start()

        

        x = threading.Thread(target=self.start_websocket_thread, )
        x.start()

        
        # # twm.start()

        # print("22222222222222222")
        
        # self.price_calculator()

    # {
    # "e": "24hrTicker",  // Event type
    # "E": 123456789,     // Event time
    # "s": "BNBBTC",      // Symbol
    # "p": "0.0015",      // Price change
    # "P": "250.00",      // Price change percent
    # "w": "0.0018",      // Weighted average price
    # "x": "0.0009",      // First trade(F)-1 price (first trade before the 24hr rolling window)
    # "c": "0.0025",      // Last price
    # "Q": "10",          // Last quantity
    # "b": "0.0024",      // Best bid price
    # "B": "10",          // Best bid quantity
    # "a": "0.0026",      // Best ask price
    # "A": "100",         // Best ask quantity
    # "o": "0.0010",      // Open price
    # "h": "0.0025",      // High price
    # "l": "0.0010",      // Low price
    # "v": "10000",       // Total traded base asset volume
    # "q": "18",          // Total traded quote asset volume
    # "O": 0,             // Statistics open time
    # "C": 86400000,      // Statistics close time
    # "F": 0,             // First trade ID
    # "L": 18150,         // Last trade Id
    # "n": 18151          // Total number of trades
    # }


    def get_tickers(self):
        if len(self.streams_dict)==0:
            return pd.DataFrame([])
        df  = pd.DataFrame(self.streams_dict.values())
        df['base_currency'] = [ CoinConstants.USDT if market_name.endswith(CoinConstants.USDT) else CoinConstants.BITCOIN  for market_name in df.s]
        df['market_currency'] = [ market_name.replace(CoinConstants.USDT,"") if market_name.endswith(CoinConstants.USDT) else market_name.replace(CoinConstants.BITCOIN,"")  for market_name in df.s]
        df['market_pair'] = df.s
        df['broker_id'] = self.broker_id
        df['last_price'] = df.c
        df['bid_price'] = df.b            
        df['ask_price'] = df.a
        df['status'] = 1
        df = df.drop(columns=['e','E','s','p','P','w','x','c','n','Q','b','B','a','A','o','h','l','v','q','O','C','F','L'],axis=1)
        return df

    def get_bitcoin_ticker(self):

        if self.btcusdt is None:
            return None
        return {
                'market_pair': 'BTCUSDT',
                'base_currency': CoinConstants.USDT,
                'market_currency': CoinConstants.BITCOIN,
                'broker_id': self.broker_id,
                'last_price' : float(self.btcusdt['c']),
                'bid_price' : float(self.btcusdt['b']),
                'ask_price' : float(self.btcusdt['a']),
                'status' : 1
            }




    def price_calculator(self):
        for i in range(1,10):
            time.sleep( 5 )
            df  = pd.DataFrame(self.streams_dict.values())
            df['base_currency'] = [ CoinConstants.USDT if market_name.endswith(CoinConstants.USDT) else CoinConstants.BITCOIN  for market_name in df.s]
            df['market_currency'] = [ market_name.replace(CoinConstants.USDT,"") if market_name.endswith(CoinConstants.USDT) else market_name.replace(CoinConstants.BITCOIN,"")  for market_name in df.s]
            df['market_pair'] = df.s
            df['broker_id'] = self.broker_id
            df['last_price'] = df.c
            df['bid_price'] = df.b            
            df['ask_price'] = df.a
            df['status'] = 1
            df = df.drop(columns=['e','E','s','p','P','w','x','c','n','Q','b','B','a','A','o','h','l','v','q','O','C','F','L'],axis=1)
            
            bitcoin = {
                'market_pair': 'BTCUSDT',
                'base_currency': CoinConstants.USDT,
                'market_currency': CoinConstants.BITCOIN,
                'broker_id': self.broker_id,
                'last_price' : float(self.btcusdt['c']),
                'bid_price' : float(self.btcusdt['b']),
                'ask_price' : float(self.btcusdt['a']),
                'status' : 1
            }

            RealtimeBusiness(self).process_market_data(df=df,bitcoin=bitcoin)
            


    def process_m_message(self,msg):
        print(msg)
        try:
            if msg['stream'] == BrokerBinance.STREAM_BTCUSDT:            
                self.btcusdt = msg['data']
                print(msg)

            #Handle Ticker
            if msg['stream'].endswith("@ticker"):

                self.set_ws_updated_time()
                self.streams_dict[msg['stream']] = msg['data']
        except Exception as e:
            print(e)
            capture_exception(e)
        
        

    def stream_list(self):
        markets = self.get_markets()
        streams = []
        for market in markets:
            streams.append('{0}@ticker'.format(market['market_pair'].lower()))
        return streams

    def get_markets(self):
        
        prices = self.client.get_all_tickers()
        
        markets = []

        for price in prices:
            if price['symbol'].endswith(CoinConstants.USDT):
                markets.append(
                    {
                    'market_pair': price['symbol'],
                    'base_currency': CoinConstants.USDT,
                    'market_currency': price['symbol'][0:-4],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                    }
                )
            if price['symbol'].endswith(CoinConstants.BITCOIN):
                markets.append(
                    {
                    'market_pair': price['symbol'],
                    'base_currency': CoinConstants.BITCOIN,
                    'market_currency': price['symbol'][0:-3],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                    }
                )

        return markets



    def _load_authenticated_client(self):
        accounts = list(BrokerAccount.objects.filter(broker_id=self.broker_id,status=1).values())
        account = None
        if len(accounts)>=1:
            account = accounts[0]
            client = Client(api_key=account['api_key'],api_secret=EncryptionUtils().decrypt(account['api_secret']))

            self.account = account
            return client
        else:
            ExchangerLogger.log_broker(broker_id=self.broker_id,message="API Key not found")
        return None


    def _do_fetch_balance(self):

        account_client = self._load_authenticated_client()
        try:
            res = account_client.get_account()

            if "balances" in res:
                return res['balances']
        except Exception as e:
            capture_exception(e)
        
        return []
            
        # print(x)
        # x=account_client.get_asset_balance(asset='BTC')
        # print(x)

        # x=account_client.get_asset_balance(asset='BTG')
        # print(x)

        # x=account_client.get_asset_balance(asset='USDT')
        # print(x)

    def _round_number(self,number,tick_size ):
        x = tick_size*(10**8)
        dec = math.log10(x)
        decimal_points = 8 - int(dec)
        return self._round_number_by_decimal_points(number=number,decimal_points=decimal_points)


    def _round_number_by_decimal_points(self,number,decimal_points):
        return format(number,"19.{0}f".format(decimal_points)).strip()
    
    def _round_price(self,pair,price):
        symbol_info = self._get_symbol_info(symbol=pair)
        if not symbol_info:
            return price

        for condition_filter in symbol_info['filters']:
            if condition_filter['filterType'] == "PRICE_FILTER":
                return self._round_number(number=price,tick_size=float(condition_filter['tickSize']))

        
        #If not match during the filters, return the same value
        return price
 
    

    def _round_amount(self,pair,amount):
        symbol_info = self._get_symbol_info(symbol=pair)
        if not symbol_info:
            return self._round_number_by_decimal_points(number=amount,decimal_points=8)

        
        for condition_filter in symbol_info['filters']:
            if condition_filter['filterType'] == "LOT_SIZE":
                return self._round_number(number=amount,tick_size=float(condition_filter['stepSize']))
    
        return self._round_number_by_decimal_points(number=amount,decimal_points=int(symbol_info['baseAssetPrecision']))

    
    def _round_market_amount(self,pair,amount):
        symbol_info = self._get_symbol_info(symbol=pair)

        
        if not symbol_info:
            return self._round_number_by_decimal_points(number=amount,decimal_points=8)
        
        # print(symbol_info)

        for condition_filter in symbol_info['filters']:
            if condition_filter['filterType'] == "PRICE_FILTER":
                return self._round_number(number=amount,tick_size=float(condition_filter['tickSize']))
    
        return self._round_number_by_decimal_points(number=amount,decimal_points=int(symbol_info['baseAssetPrecision']))

        



    def _get_symbol_info(self,symbol):
        cache_key = "{0}_{1}".format(CacheKey.BINANCE_PAIR_INFO_PREFIX,symbol)
        info = CacheUtils.get_key(cache_key)
        
        if not info:
            info = self.client.get_symbol_info(symbol)
            CacheUtils.cache_key(cache_key,info,ttl=24*60*60)

        return info


        
    def _do_submit_order_limit(self,action,pair,amount,price):
        binance_client = self._load_authenticated_client()       



        if not binance_client:
            return None

        order = None

        #Round using USDT or BTC
        amount = self._round_amount(pair=pair,amount=amount)
        price = self._round_price(pair=pair,price=price)

        if action == enums.SIDE_BUY:
            try:
                
                order = binance_client.create_order(
                    symbol=pair,
                    side=enums.SIDE_BUY,
                    type=enums.ORDER_TYPE_LIMIT,
                    timeInForce=enums.TIME_IN_FORCE_IOC,
                    quantity=amount,
                    price=price
                )

                

                
            except Exception as e:
                print(e)
                ExchangerLogger.log_broker(broker_id=self.broker_id, message=str(e))
                capture_exception(e)
                return None
                pass


        else:
           
            try:            
                order = binance_client.create_order(
                    symbol=pair,
                    side=enums.SIDE_SELL,
                    type=enums.ORDER_TYPE_LIMIT,
                    timeInForce=enums.TIME_IN_FORCE_IOC,
                    quantity=amount,
                    price=price
                )
            except Exception as e:
                capture_exception(e)
                return None
        
        if order is not None:

            print(order)


            account_order = Broker_Account_Order()
            account_order.broker_id = self.broker_id
            account_order.orderId=order['orderId']
            account_order.market_pair = order['symbol']
            account_order.mode = order['type']
            account_order.action = order['side']
            account_order.total_amount = float(order['cummulativeQuoteQty'])
            status = BrokerOrderStatus.SUBMITTED
            fills = []
            qty = 0
            total = 0
            avg = 0
            if order['status'] == 'FILLED':
                status = BrokerOrderStatus.FILLED
                for order_fill in order['fills']:
                    qty =  qty + float(order_fill['qty'])
                    total = total + float(order_fill['qty'])*float(order_fill['price'])

                    fill = Broker_Account_Order_Fill()
                    fill.price  = float(order_fill['price'])
                    fill.qty  = float(order_fill['qty'])
                    fill.trade_id = order_fill['tradeId']

                    fills.append(fill)

            if order['status'] == 'EXPIRED':
                status = BrokerOrderStatus.FILLED     

                
                
            if qty > 0 :
                avg = total/qty

                
            account_order.status = status
            account_order.quantity = qty
            account_order.fill_quantity = qty
            account_order.avg_price = avg

            if account_order.fill_quantity ==0 :
                account_order.status = BrokerOrderStatus.CANCELED

            account_order.save()
            

            for fill in fills:
                fill.broker_id = account_order.broker_id
                fill.market_pair = account_order.market_pair
                fill.action = account_order.action
                fill.orderId = account_order.ID
                fill.save()

            if account_order.fill_quantity ==0:
                return None 

            return order['orderId']


    def _do_submit_order_market(self,action,pair,total_amount,by='default'):

        binance_client = self._load_authenticated_client()

        if not binance_client:
            return None

        order = None

        

        if action == enums.SIDE_BUY:
            if by =='default' or by == 'total_amount':
                try:                
                    
                    total_amount = self._round_market_amount(pair=pair,amount=total_amount)             
                    
                    order = binance_client.create_order(
                        symbol=pair,
                        side=enums.SIDE_BUY,
                        type=enums.ORDER_TYPE_MARKET,
                        quoteOrderQty=total_amount
                    )
                except Exception as e:
                    print(e)
                    capture_exception(e)
                    return None

            elif by == 'quantity':
                try:                

                    
                    total_amount = self._round_amount(pair=pair,amount=total_amount)             
                    

                    order = binance_client.create_order(
                        symbol=pair,
                        side=enums.SIDE_BUY,
                        type=enums.ORDER_TYPE_MARKET,
                        quantity=total_amount
                    )
                except Exception as e:
                    print(e)
                    capture_exception(e)
                    return None


        else :
            #SELL       

            if by =='default' or by == 'quantity':

                try:     

                    total_amount = self._round_amount(pair=pair,amount=total_amount)
                    
                    
                    order = binance_client.create_order(
                        symbol=pair,
                        side=enums.SIDE_SELL,
                        type=enums.ORDER_TYPE_MARKET,
                        quantity=total_amount
                    )
                except Exception as e:
                    print(e)
                    capture_exception(e)
                    return None
            elif by == 'total_amount':

                try:     

                    total_amount = self._round_market_amount(pair=pair,amount=total_amount)
                    
                    order = binance_client.create_order(
                        symbol=pair,
                        side=enums.SIDE_SELL,
                        type=enums.ORDER_TYPE_MARKET,
                        quoteOrderQty=total_amount
                    )
                except Exception as e:
                    print(e)
                    capture_exception(e)
                    return None



        if order is not None:

            account_order = Broker_Account_Order()
            account_order.broker_id = self.broker_id
            account_order.orderId=order['orderId']
            account_order.market_pair = order['symbol']
            account_order.mode = order['type']
            account_order.action = order['side']
            status = BrokerOrderStatus.SUBMITTED
            fills = []
            qty = 0
            total = 0
            if order['status'] == 'FILLED':
                status = BrokerOrderStatus.FILLED
                for order_fill in order['fills']:
                    qty =  qty + float(order_fill['qty'])
                    total = total + float(order_fill['qty'])*float(order_fill['price'])

                    fill = Broker_Account_Order_Fill()
                    fill.price  = float(order_fill['price'])
                    fill.qty  = float(order_fill['qty'])
                    fill.trade_id = order_fill['tradeId']

                    fills.append(fill)
                avg = total/qty

                
            account_order.status = status
            account_order.total_amount = float(order['cummulativeQuoteQty'])
            account_order.quantity = float(order['origQty'])
            account_order.fill_quantity = float(order['executedQty'])
            account_order.avg_price = account_order.total_amount/account_order.fill_quantity

            account_order.save()

            for fill in fills:
                fill.broker_id = account_order.broker_id
                fill.market_pair = account_order.market_pair
                fill.action = account_order.action
                fill.orderId = account_order.ID
                fill.save()

            return order['orderId']

    def _do_fetch_deposit_history(self):
        binance_client = self._load_authenticated_client()
        start_time = (int(time.time()) - 2*24*60*60)*1000
        params = {
            'startTime': start_time
        }
        deposit_history = binance_client.get_deposit_history(startTime=start_time)     

        print(deposit_history)
        
        deposit_list = []
        for deposit_info in deposit_history:
            # print(deposit_info)
            deposit_list.append({
                'broker_id': self.broker_id,
                'coin_symbol': deposit_info['asset'],
                'account_id':'Unknown',
                'broker_history_id': deposit_info['insertTime'],
                'amount': deposit_info['amount'],
                'confirmations': deposit_info['status'],
                'txid': deposit_info['txId'],
                'crypto_address': deposit_info['address'],
                'crypto_address_tag': deposit_info['addressTag']
            })
        

        return deposit_list

    def _do_fetch_deposit_address(self):
        account = self._load_authenticated_client()
        account_id = self.account['ID']

        count = 0
        #coins = Broker_Account_Deposit_Address.objects.filter(broker_id=self.broker_id).all()
        coins =  BrokerCoinPriceModel.objects.filter(broker_id=self.broker_id).all()
        for coin in coins:
            addresses = Broker_Account_Deposit_Address.objects.filter(broker_id=self.broker_id,coin_symbol=coin.coin_symbol,account_id=account_id).all()
            if len(addresses) >0:
                continue

            count=count+1
            time.sleep(1)
            try:
                address_info = account.get_deposit_address(asset=coin.coin_symbol)        

                if address_info:
                    
                    coin_address = Broker_Account_Deposit_Address()  
                    coin_address.broker_id = self.broker_id
                    coin_address.coin_symbol = coin.coin_symbol
                    if 'address' in address_info:
                        coin_address.crypto_address = address_info['address']
                        coin_address.crypto_address_tag = address_info['addressTag']
                    else:
                        coin_address.crypto_address = 'N/A'

                    coin_address.chain = coin_address.coin_symbol.lower()
                    coin_address.account_id = account_id
                    
                    coin_address.save()
            except Exception as e:
                print(e)
                pass
                
                


            
            if count>30:
                return


    def _do_fetch_coin_info(self):
        client = self._load_authenticated_client()
        asset_info = client.get_asset_details()

        coin_lists = []
        if asset_info['success']:
            for coin_symbol in asset_info['assetDetail']:
                asset_detail = asset_info['assetDetail'][coin_symbol]
                coin_lists.append({
                    'broker_id': self.broker_id,
                    'coin_symbol': coin_symbol,
                    'withdraw_fee_type': 'fixed',
                    'min_transact_fee_withdraw': asset_detail['withdrawFee'],
                    'max_transact_fee_withdraw': asset_detail['withdrawFee'],
                    'deposit_status': asset_detail['depositStatus'],
                    'withdraw_status': asset_detail['withdrawStatus'],
                    'min_withdraw_amount': asset_detail['minWithdrawAmount']
                })
        
        return coin_lists

    def _do_withdraw(self,coin_symbol,to_coin_address,tag,amount,unique_id=''): 
        

        params = {
            'asset': coin_symbol,
            'address': to_coin_address,
            'addressTag': tag,
            'amount': float(amount),
            'name':unique_id
        }

        client = self._load_authenticated_client()


        result_id = None
        
        

        try:
            
            
            if tag and len(tag)>0:
                result = client.withdraw(
                    coin= coin_symbol,
                    address= to_coin_address,
                    amount=float(amount),
                    addressTag = tag
                )

                result_id = result['id']
                
            else:
                result = client.withdraw(
                    coin= coin_symbol,
                    address= to_coin_address,
                    amount=float(amount)
                )


                result_id = result['id']


          
            return result_id



        except Exception as e:
            print(e)
            capture_exception(e)
            result_id = None

        else:
            print("YEAH")

        return result_id

    def _do_fetch_withdraw_history(self):

        client = self._load_authenticated_client()
        withdrawHistory = client.get_withdraw_history()
        withdrawList = withdrawHistory['withdrawList']
        for withdraw in withdrawList:

            try:
            
            
                history = Broker_Withdraw_History()
                history.coin_symbol = withdraw['asset']
                history.network = withdraw['network']
                history.address = withdraw['address']
                history.unique_id = withdraw['id']
                history.txId = withdraw['txId']
                history.amount = withdraw['amount']
                history.fee = withdraw['transactionFee']

                history.save()
            except :
                pass