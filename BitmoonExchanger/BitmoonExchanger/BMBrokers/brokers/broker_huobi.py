from .base_broker import BaseBroker

from ...BMUtils.utils.constants import CoinConstants
from huobi.client.market import MarketClient
#from huobi.connection.subscribe_client import SubscribeClient
from huobi.client.trade import TradeClient
from huobi.client.account import AccountClient
from huobi.client.generic import GenericClient
from huobi.client.wallet import WalletClient


from ..models import BrokerAccount,Broker_Account_Order,Broker_Account_Order_Fill,Broker_Account_Deposit_Address, BrokerCoinPriceModel
from huobi.utils import *
from huobi.constant import *

from ...BMUtils.utils.constants import *
from ...BMUtils.utils.cache_utils import CacheUtils
from ...BMUtils.utils.encryption_utils import EncryptionUtils
import pandas as pd

import websocket
import json
import gzip
from threading import Thread
import time

from sentry_sdk import capture_exception


class BrokerHuobi(BaseBroker):    

    STREAM_BTCUSDT = "market.btcusdt.bbo"

    def __init__(self):
        super(BrokerHuobi, self).__init__(broker_id='huobi-global')
        self.client=MarketClient()

        self.streams_dict = {}
        self.btcusdt = None

        self.ws = None

        self.pong_message = None

        self.account = None
        
    
    def _get_active_account(self):
        accounts = list(BrokerAccount.objects.filter(broker_id=self.broker_id,status=1).values())
        if len(accounts)>=1:
            self.account = accounts[0]
            return accounts[0]
        else:
            return None



    def _load_trade_authenticated_client(self):
        account = self._get_active_account()
        if account:            
            client = TradeClient(api_key=account['api_key'],secret_key=EncryptionUtils().decrypt(account['api_secret']))
            return client

        return None

    def _load_account_authenticated_client(self):
        account = self._get_active_account()

        if account:  
            
            client = AccountClient(api_key=account['api_key'],secret_key=EncryptionUtils().decrypt(account['api_secret']))
            return client

        return None

    def _load_wallet_authenticated_client(self):
        account = self._get_active_account()
        if account:  
            
            client = WalletClient(api_key=account['api_key'],secret_key=EncryptionUtils().decrypt(account['api_secret']))
            return client

        return None

    def start_websocket(self):
        #streams = self.stream_list()
        #self.client.sub_pricedepth_bbo(','.join(streams), self.process_m_message)

        self._initialize_ws()

        print("_initialize_ws DONE")

    def _initialize_ws(self):
        


        def run(*args):

            print("INIT WS")

            try:
                self.ws = websocket.WebSocketApp("wss://api-aws.huobi.pro/ws",on_close=self.on_close, on_error=self.on_error,on_message=self.on_message,on_open=self.on_open)


                self.ws.run_forever()
                #ws.op
            except Exception as e:
                capture_exception(e)
                print(e)

        Thread(target=run).start()




        


    def on_open(self,ws=None):
        
        #streams = self.stream_list()
        print("Socket open")
        
        
        def run(*args):
            print("Thread Starts...")
            try:
                last_pong_message = None
                last_pong_time = 0
                while True:
                    # send the message, then wait
                    # so thread doesn't exit and socket
                    # isn't closed

                    

                    if self.pong_message and self.ws :
                        current_time = time.time()
                        if last_pong_message != self.pong_message or last_pong_time + 10 < current_time:
                            last_pong_message = self.pong_message   
                            last_pong_time = current_time

                            
                        
                            self.ws.send(json.dumps(last_pong_message))
                    
                    time.sleep(1)

            except Exception as e:
                print(e)
            #ws.close()
            print("Thread terminating...")
        
        Thread(target=run).start()

        self._subscribe_bbo()
        

    def _subscribe_bbo(self):
        streams = self.stream_list()
        print(streams)
        for stream in streams:
            try:
                message = {
                    'sub': 'market.{0}.bbo'.format(stream),
                    'id': 'market.{0}.bbo'.format(stream)
                }

                if self.ws:                                   
                    self.ws.send(json.dumps(message))

                time.sleep(0.1)
            except Exception as e:
                print(e)
            
        
    def on_message(self,ws,msg):
        dict_data = json.loads(gzip.decompress(msg).decode("utf-8"))

        
        

        
        
        if 'ping' in dict_data:
            
            self._on_ping(dict_data=dict_data)
        else:

            self.set_ws_updated_time()
            self.process_m_message(dict_data)
            # pass


    
    def _on_ping(self,dict_data):
        pong_message = {
            'pong': dict_data['ping']
        }
        
        self.pong_message = pong_message

        
    
    def on_error(self,ws,error):
        capture_exception(error)
        print("WS Error")
    def on_close(self,ws,x,y):
        
        time.sleep(10)
        self._initialize_ws()

        
    def process_m_message(self,msg):
        
        
        try:

            if 'ch' not in msg:
                return

            
        
            if msg['ch'] == BrokerHuobi.STREAM_BTCUSDT:            
                self.btcusdt = msg

            
            if msg['ch'].startswith("market") and msg['ch'].endswith("bbo"):
                # pass
                self.streams_dict[msg['ch']] = msg
        except Exception as e:
            # print(msg)
            print(e)
            capture_exception(e)
            pass
            


    def get_tickers(self):
        # if len(self.streams_dict)==0:
        #     return pd.DataFrame([])
        # df  = pd.DataFrame(self.streams_dict.values())
        # df['base_currency'] = [ CoinConstants.USDT if market_name.endswith(CoinConstants.USDT) else CoinConstants.BITCOIN  for market_name in df.s]
        # df['market_currency'] = [ market_name.replace(CoinConstants.USDT,"") if market_name.endswith(CoinConstants.USDT) else market_name.replace(CoinConstants.BITCOIN,"")  for market_name in df.s]
        # df['market_pair'] = df.s
        # df['broker_id'] = self.broker_id
        # df['last_price'] = df.c
        # df['bid_price'] = df.b            
        # df['ask_price'] = df.a
        # df['status'] = 1
        # df = df.drop(columns=['e','E','s','p','P','w','x','c','n','Q','b','B','a','A','o','h','l','v','q','O','C','F','L'],axis=1)
        
        markets = []
        
        for channel,market in self.streams_dict.items():
            channel_parts = channel.split('.')
            market_name = channel_parts[1].upper()

            if market_name.endswith(CoinConstants.USDT):

                market_currency = market_name[0:-4]
                try:

                    markets.append(
                        {   
                            'broker_id': self.broker_id,
                            'market_pair':market_name,
                            'base_currency': CoinConstants.USDT,
                            'market_currency': market_currency,
                            'last_price': (float(market['tick']['bid']) + float(market['tick']['ask']))/2,
                            'bid_price': float(market['tick']['bid']),
                            'ask_price': float(market['tick']['ask']),
                            'status': 1
                        }

                    )
                except:
                    pass

            if market_name.endswith(CoinConstants.BITCOIN):
                market_currency = market_name[0:-3]

                try:

                    markets.append({   
                            'broker_id': self.broker_id,
                            'market_pair':market_name,
                            'base_currency': CoinConstants.BITCOIN,
                            'market_currency': market_currency,
                            'last_price': (float(market['tick']['bid']) + float(market['tick']['ask']))/2,
                            'bid_price': float(market['tick']['bid']),
                            'ask_price': float(market['tick']['ask']),
                            'status': 1
                    })
                except:
                    pass


        df  = pd.DataFrame(markets)

        
        

        return df

    def get_bitcoin_ticker(self):

        if self.btcusdt is None:
            return None
        return {
                'market_pair': 'BTCUSDT',
                'base_currency': CoinConstants.USDT,
                'market_currency': CoinConstants.BITCOIN,
                'broker_id': self.broker_id,
                'last_price' : (float(self.btcusdt['tick']['bid']) + float(self.btcusdt['tick']['bid']) ) /2, 
                'bid_price' : float(self.btcusdt['tick']['bid']),
                'ask_price' : float(self.btcusdt['tick']['ask']),
                'status' : 1
            }

    def stream_list(self):
        list_markets = self.get_markets()

        symbol_list = []
        for market in list_markets:
            symbol_list.append(market['market_pair'].lower())

        return symbol_list



    def get_markets(self):
        markets = []

        list_markets = self.client.get_market_tickers()
        
        
        for market in list_markets:
            symbol = market.symbol.upper()

            

            if symbol.endswith(CoinConstants.USDT):
                markets.append(
                    {
                    'market_pair': symbol,
                    'base_currency': CoinConstants.USDT,
                    'market_currency': symbol[0:-4],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                })


            elif symbol.endswith(CoinConstants.BITCOIN):
                markets.append(
                    {
                    'market_pair': symbol,
                    'base_currency': CoinConstants.BITCOIN,
                    'market_currency': symbol[0:-3],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                })
        return markets

    def _get_spot_account(self):
        account_client = self._load_account_authenticated_client()
        accounts =[]
        if account_client != None:
            accounts = account_client.get_accounts()
        account_id = None
        for account in accounts:
            if account.type=='spot':
                account_id =  account.id
        return account_id

    
    def order_detail_callback(self,order_detail):

        
        order_detail.print_object()

        order_type="BUY"
        mode="LIMIT"
        if 'sell' in order_detail.type: 
            order_type='SELL'

        if 'market' in order_detail.type:
            mode = "MARKET"

        account_order = Broker_Account_Order()
        account_order.broker_id = self.broker_id
        account_order.orderId=order_detail.id
        account_order.market_pair = order_detail.symbol.upper()
        account_order.mode = mode
        account_order.action = order_type
        account_order.status =  BrokerOrderStatus.SUBMITTED
        account_order.total_amount = order_detail.filled_cash_amount

        if order_detail.state == OrderState.FILLED:
            account_order.status = BrokerOrderStatus.FILLED
            account_order.quantity = order_detail.amount
            account_order.fill_quantity = order_detail.filled_amount
            account_order.avg_price = float(order_detail.filled_cash_amount)/float(order_detail.filled_amount)
        elif order_detail.state == OrderState.CANCELED:
            account_order.status = BrokerOrderStatus.CANCELED
            account_order.quantity = order_detail.amount
            account_order.fill_quantity = 0
            account_order.avg_price = 0
        account_order.save()

        return account_order


    def _do_submit_order_limit(self,action,pair,amount,price):
        trade_client = self._load_trade_authenticated_client()

        pair =pair.lower()
 
        

        if not trade_client:
            print("Not found")
            return None

        account_id = self._get_spot_account()
        if account_id == None:
            return None

        order = None

        amount = self._round_amount(pair=pair,amount=amount)
        price = self._round_price(pair=pair,price=price)

        

        
        if action == 'BUY':
            try:
                
            
                order = trade_client.create_order(
                    symbol=pair,
                    order_type=OrderType.BUY_IOC,
                    source=OrderSource.API,                    
                    amount=amount,
                    price=price,
                    account_id=account_id
                )

                

                order_detail = trade_client.get_order(order_id=order)
                time.sleep(0.5)
                order_info = self.order_detail_callback(order_detail=order_detail)
                if order_info.status != BrokerOrderStatus.FILLED :
                    return None
                
                return order

                

            except Exception as e:
                capture_exception(e)
                print(e)
                return None


        else:
            #SELL
            

            try:            
                order = trade_client.create_order(
                    symbol=pair,
                    order_type=OrderType.SELL_IOC,
                    source=OrderSource.API,                    
                    amount=amount,
                    price=price,
                    account_id=account_id
                )

                order_detail = trade_client.get_order(order_id=order)
                time.sleep(0.5)
                order_info = self.order_detail_callback(order_detail=order_detail)
                if order_info.status != BrokerOrderStatus.FILLED :
                    return None

                return order
            except Exception as e:

                capture_exception(e)
                
                return None
        
    def _do_submit_order_market(self,action,pair,total_amount,by='default'):

        trade_client = self._load_trade_authenticated_client()

        pair = pair.lower()

        if not trade_client:
            return None

        account_id = self._get_spot_account()
        if account_id == None:
            return None

        order = None


        if action == 'BUY':
            try:

                
                total_amount  = self._round_market_amount(pair=pair,amount=total_amount)

                order = trade_client.create_order(
                    symbol=pair,
                    order_type=OrderType.BUY_MARKET,
                    source=OrderSource.API,                    
                    amount=total_amount,
                    price=None,
                    account_id=account_id
                )


                order_detail = trade_client.get_order(order_id=order)
                time.sleep(0.5)
                order_info = self.order_detail_callback(order_detail=order_detail)
                if order_info.status != BrokerOrderStatus.FILLED :
                    return None
                return order
            except Exception as e:
                capture_exception(e)
                print(e)
                return None
                pass

        else :
            #SELL

            
            total_amount  = self._round_amount(pair=pair,amount=total_amount)

            try:            
                order = trade_client.create_order(
                    symbol=pair,
                    order_type=OrderType.SELL_MARKET,
                    source=OrderSource.API,                    
                    amount=total_amount,
                    price=None,
                    account_id=account_id
                )

                
                

                order_detail = trade_client.get_order(order_id=order)
                time.sleep(0.5)
                
                order_info = self.order_detail_callback(order_detail=order_detail)
                if order_info.status != BrokerOrderStatus.FILLED :
                    return None                

                return order
            except Exception as e:
                capture_exception(e)                
                return None


        


    def _round_number(self,number,decimal_points ):
        return format(number,"19.{0}f".format(decimal_points)).strip()
    
    def _round_price(self,pair,price):
        symbol_info = self._get_symbol_info(symbol=pair)

        if not symbol_info:
            return price

        return self._round_number(number=price,decimal_points=symbol_info['price_precision'])

        
        

    def _round_amount(self,pair,amount):
        symbol_info = self._get_symbol_info(symbol=pair)
        
        if not symbol_info:
            return amount

        return self._round_number(number=amount,decimal_points=symbol_info['amount_precision'])

    def _round_market_amount(self,pair,amount):
        symbol_info = self._get_symbol_info(symbol=pair)
        
        if not symbol_info:
            return amount

        return self._round_number(number=amount,decimal_points=symbol_info['value_precision'])
        

    def _get_symbol_info(self,symbol):
        symbol = symbol.lower()
        cache_key = "{0}_{1}".format(CacheKey.HUOBI_PAIR_INFO_PREFIX,symbol)
        info = CacheUtils.get_key(cache_key)


        if not info:
            print("Get from API")
            generic_client = GenericClient()
            list_obj = generic_client.get_exchange_symbols()
            if len(list_obj):
                for idx, row in enumerate(list_obj):
                    # LogInfo.output("------- number " + str(idx) + " -------")
                    # row.print_object()

                    cache_key_symbol = "{0}_{1}".format(CacheKey.HUOBI_PAIR_INFO_PREFIX,row.symbol)
                    
                    symbol_info = {
                        "price_precision": row.price_precision,
                        "amount_precision": row.amount_precision,
                        "value_precision": row.value_precision,
                        "min_order_amt": row.min_order_amt,
                        "max_order_amt": row.max_order_amt,
                        "min_order_value": row.min_order_value
                    }

                    CacheUtils.cache_key(cache_key_symbol,symbol_info,ttl=24*60*60)
                    
                    if symbol == row.symbol:
                        info = symbol_info
                            

        return info

    def _do_fetch_balance(self):
        
        account = self._load_account_authenticated_client()
        if account is None:
            return None
        accounts = account.get_account_balance() 
        for account in accounts:
            # print(coin_balance.asset)
            # coin_balance.print_object()
            if account.type == 'spot':
                # balances = account.subtype
                list_coins = {}
                # print(account.list)
                for coin_balance in account.list:
                    if coin_balance.type == 'trade':
                        if coin_balance.currency.upper() in list_coins:
                            list_coins[coin_balance.currency.upper()]['free'] = coin_balance.balance
                        else:
                            list_coins[coin_balance.currency.upper()] = {
                                'asset': coin_balance.currency.upper(),
                                'free': coin_balance.balance,
                                'locked': 0
                            }


                    if coin_balance.type =='frozen':
                        if coin_balance.currency.upper() in list_coins:
                            list_coins[coin_balance.currency.upper()]['locked'] = coin_balance.balance
                        else:
                            list_coins[coin_balance.currency.upper()] = {
                                'asset': coin_balance.currency.upper(),
                                'free': 0,
                                'locked': coin_balance.balance
                            }
                    
                    
                return list(list_coins.values())

        return None

    def _do_fetch_deposit_history(self):
        wallet_account = self._load_wallet_authenticated_client()

        if wallet_account is None:
            return None

        spot_account = self._get_spot_account() or 'Unknown'

      
        account_deposit_list = wallet_account.get_deposit_withdraw(op_type='deposit')
        

        deposit_list = []

        for deposit in account_deposit_list:
            
            deposit_list.append({
                'broker_id': self.broker_id,
                'account_id':spot_account,
                'coin_symbol': deposit.currency.upper(),
                'broker_history_id': deposit.id,
                'amount': float(deposit.amount),
                'confirmations': 1000,
                'txid': deposit.tx_hash,
                'crypto_address': deposit.address,
                'crypto_address_tag': deposit.address_tag
            })


        return deposit_list

    def _do_fetch_deposit_address(self):
        wallet_account = self._load_wallet_authenticated_client()
        if wallet_account is None:
            return

        count = 0
        coins =  BrokerCoinPriceModel.objects.filter(broker_id=self.broker_id).all()
        account_id = self.account['ID']
        for coin in coins:
            addresses = Broker_Account_Deposit_Address.objects.filter(broker_id=self.broker_id,coin_symbol=coin.coin_symbol, account_id=account_id).all()
            if len(addresses) >0:
                continue

            
            count = count+1
            time.sleep(1)
            
            try:
                address_infos = wallet_account.get_account_deposit_address(currency=coin.coin_symbol.lower())
                if address_infos:              
                    for address_info in address_infos:                        
                        coin_address = Broker_Account_Deposit_Address()
                        coin_address.broker_id = self.broker_id
                        coin_address.coin_symbol = coin.coin_symbol
                        coin_address.crypto_address = address_info.address
                        coin_address.crypto_address_tag = address_info.addressTag
                        coin_address.chain = address_info.chain
                        coin_address.account_id = account_id
                        coin_address.save()
            except Exception as e:
                print(e)


            if count>30:
                return
        pass
    def _do_fetch_coin_info(self):
        client = GenericClient()
        currencies = client.get_reference_currencies()
        coin_lists = []
        for currency_info in currencies:
            if currency_info.instStatus =='delisted':
                coin_lists.append({
                    'broker_id': self.broker_id,
                    'coin_symbol': currency_info.currency.upper(),
                    'withdraw_fee_type': 'unknown',
                    'min_transact_fee_withdraw': 0,
                    'max_transact_fee_withdraw': 0,
                    'deposit_status': 0,
                    'withdraw_status': 0,
                    'min_withdraw_amount': 0
                })
            elif currency_info.instStatus =='normal':
                if len(currency_info.chains) ==0 : 
                    coin_lists.append({
                        'broker_id': self.broker_id,
                        'coin_symbol': currency_info.currency.upper(),
                        'withdraw_fee_type': 'unknown',
                        'min_transact_fee_withdraw': 0,
                        'max_transact_fee_withdraw': 0,
                        'deposit_status': 0,
                        'withdraw_status': 0,
                        'min_withdraw_amount': 0
                    })
                else:
                    chain = currency_info.chains[0]
                    
                    coin_lists.append({
                        'broker_id': self.broker_id,
                        'coin_symbol': currency_info.currency.upper(),
                        'withdraw_fee_type': chain.withdrawFeeType,
                        'min_transact_fee_withdraw': chain.minTransactFeeWithdraw,
                        'max_transact_fee_withdraw': chain.maxTransactFeeWithdraw,
                        'deposit_status': 1 if chain.depositStatus =='allowed' else 0,
                        'withdraw_status': 1 if chain.withdrawStatus =='allowed' else 0,
                        'min_withdraw_amount': chain.minWithdrawAmt
                    })

                


            # return
        return coin_lists

    def _do_withdraw(self,coin_symbol,to_coin_address,tag,amount,unique_id='',network=''): 
        
        return
