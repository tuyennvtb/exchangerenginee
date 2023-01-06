from .base_broker import BaseBroker

from ...BMUtils.utils.constants import CoinConstants,BrokerOrderStatus,ExchangerModeConstants
import threading

from ..models import BrokerAccount,Broker_Account_Order,Broker_Account_Order_Fill,Broker_Account_Balance,BrokerCoinPriceModel,Broker_Account_Deposit_Address,Broker_Withdraw_History

from ...BMUtils.utils.exchanger_logger import  ExchangerLogger

import requests
import json
import pandas as pd
from sentry_sdk import capture_exception
import time


import time
import requests
import hmac
import hashlib
from urllib import parse


from ...BMUtils.utils.encryption_utils import EncryptionUtils


class BrokerMXC(BaseBroker):    
    def __init__(self):
        super(BrokerMXC, self).__init__(broker_id='mxc')

        self.tickers = None

        self.ROOT_URL = 'https://www.mxc.com'
        

    def start_websocket(self):
        
        x = threading.Thread(target=self.fake_ws, args=())
        x.start()
        print("start_websocket MXC")

    def fake_ws(self):
        while True:
            time.sleep(2)
            print("MXC Fake WS")
            try:
                r = requests.get("https://www.mxc.com/open/api/v2/market/ticker")
                
                response = r.json()
                # print(response)
                self.tickers  = response['data']

                self.set_ws_updated_time()

            except Exception as e:
                print(e)
                pass

    def get_markets(self):
        
        r = requests.get("https://www.mxc.com/open/api/v2/market/ticker")
        
        response = r.json()
        tickers = response['data']


        markets = []

        for pair in tickers:
            
            if pair['symbol'].endswith(CoinConstants.USDT):
                markets.append(
                    {
                    'market_pair': pair['symbol'],
                    'base_currency': CoinConstants.USDT,
                    'market_currency': pair['symbol'][0:-5],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                    }
                )
            
            if pair['symbol'].endswith(CoinConstants.BITCOIN):
                markets.append(
                    {
                    'market_pair': pair['symbol'],
                    'base_currency': CoinConstants.BITCOIN,
                    'market_currency': pair['symbol'][0:-4],
                    'broker_id': self.broker_id,                    
                    'status' : 1
                    }
                )         

        return markets


    def get_bitcoin_ticker(self):

        if self.tickers is None:
            return None
        
        for pair in self.tickers:
            if pair['symbol'] == "BTC_USDT":
                return {
                        'market_pair': 'BTC_USDT',
                        'base_currency': CoinConstants.USDT,
                        'market_currency': CoinConstants.BITCOIN,
                        'broker_id': self.broker_id,
                        'last_price' : float(pair['last']),
                        'bid_price' : float(pair['bid']),
                        'ask_price' : float(pair['ask']),
                        'status' : 1
                    }
        return None

    def get_tickers(self):
        if self.tickers is None:
            return pd.DataFrame([])
        
        df  = pd.DataFrame(self.tickers)
        df['symbol_short'] = df.symbol.str.replace("_","")
        df=df[(df.symbol.str.endswith(CoinConstants.USDT))|(df.symbol.str.endswith(CoinConstants.BITCOIN))]

        
        df['base_currency'] = [ CoinConstants.USDT if market_name.endswith(CoinConstants.USDT) else CoinConstants.BITCOIN  for market_name in df.symbol_short]
        df['market_currency'] = [ market_name.replace(CoinConstants.USDT,"") if market_name.endswith(CoinConstants.USDT) else market_name.replace(CoinConstants.BITCOIN,"")  for market_name in df.symbol_short]
        df['market_pair'] = df.symbol

        df['broker_id'] = self.broker_id
        df['last_price'] = df['last']
        df['bid_price'] = df.bid           
        df['ask_price'] = df.ask
        df['status'] = 1
        df = df.drop(columns=['symbol','volume','high','low','bid','ask','open','last','time','change_rate','symbol_short'],axis=1)
        return df

    
        
    def _load_authenticated_client(self):
        accounts = list(BrokerAccount.objects.filter(broker_id=self.broker_id,status=1).values())
        account = None
        if len(accounts)>=1:
            account = accounts[0]
            
            return account
        else:
            pass
        return None

        
    
    def _get_server_time(self):
        return int(time.time())
    
    def _sign(self,method, path, original_params=None):
        account = self._load_authenticated_client()
        if account is None:
            return None
        params = {
            'api_key': account['api_key'],
            'req_time': self._get_server_time(),
        }
        if original_params is not None:
            params.update(original_params)
        params_str = '&'.join('{}={}'.format(k, params[k]) for k in sorted(params))
        to_sign = '\n'.join([method, path, params_str])
        params.update({'sign': hmac.new(EncryptionUtils().decrypt(account['api_secret']).encode(), to_sign.encode(), hashlib.sha256).hexdigest()})
        return params


    def _query_order_single(self,order_id):
        """query order"""
        origin_trade_no = order_id
        if isinstance(order_id, list):
            origin_trade_no = parse.quote(','.join(order_id))
        method = 'GET'
        path = '/open/api/v2/order/query'
        url = '{}{}'.format(self.ROOT_URL, path)
        original_params = {
            'order_ids': origin_trade_no,
        }
        params = self._sign(method, path, original_params=original_params)
        if isinstance(order_id, list):
            params['order_ids'] = ','.join(order_id)
        response = requests.request(method, url, params=params)
        response_json = response.json()

        print(response_json)
        
        if response_json['code'] == 200 and len(response_json['data'])==1:
            
            return response_json['data'][0]
        return None


    def _do_submit_order_limit(self,action,pair,amount,price):

        """place order"""

        
        try:

            trade_type='BID'
            if action=='SELL':
                trade_type='ASK'

            method = 'POST'
            path = '/open/api/v2/order/place'
            url = '{}{}'.format(self.ROOT_URL, path)
            params = self._sign(method, path)
            data = {
                'symbol': pair,
                'price': '{:.20f}'.format(price),
                'quantity': '{:.20f}'.format(amount),
                'trade_type': trade_type,
                'order_type': 'IMMEDIATE_OR_CANCEL',
            }
            response = requests.request(method, url, params=params, json=data)
            # print(response.json())
            response_json = response.json()
            print(response_json)

            ExchangerLogger.log_broker(self.broker_id,json.dumps(response_json))

            
            
            if response_json['code'] == 200:
                order_id = response_json['data']

                order_info = self._query_order_single(order_id=order_id)

                # print(order_info)
                account_order = Broker_Account_Order()
                account_order.broker_id = self.broker_id
                account_order.orderId=order_info['id']
                account_order.market_pair = order_info['symbol']
                account_order.mode = ExchangerModeConstants.LIMIT
                account_order.action = action
                account_order.total_amount = float(order_info['deal_amount'])
                status = BrokerOrderStatus.SUBMITTED

                

                if order_info['state'] == 'FILLED':
                    status = BrokerOrderStatus.FILLED


                account_order.status = status
                account_order.quantity = float(order_info['quantity'])
                account_order.fill_quantity = float(order_info['deal_quantity'])                

                if account_order.fill_quantity ==0 :
                    account_order.status = BrokerOrderStatus.CANCELED
                    account_order.avg_price = 0
                else:
                    account_order.avg_price = account_order.total_amount / account_order.fill_quantity

                account_order.save()

                


                
                return order_info['id']

            
            else:
                return None
                

        except Exception as e:
            capture_exception(e)
            print(e)
            


    def _do_fetch_balance(self):

        balances = []
        try:

            method = 'GET'
            path = '/open/api/v2/account/info'
            url = '{}{}'.format(self.ROOT_URL, path)
            params = self._sign(method, path)
            response = requests.request(method, url, params=params)
            response_json = response.json()
            if response_json['code'] == 200:
                data = response_json['data']                
                for asset in data:
                    
                    info = data[asset]
                    balances.append({
                        'asset': asset,
                        'free': info['available'],
                        'locked': info['frozen']
                    })            
        except Exception as e:
            print(e)
            capture_exception(e)

        
        return balances

    def _do_fetch_deposit_address(self):
        account = self._load_authenticated_client()
        if account is None:
            return None

        coins =  BrokerCoinPriceModel.objects.filter(broker_id=self.broker_id).all()

        count =0
        for coin in coins:
            addresses = Broker_Account_Deposit_Address.objects.filter(broker_id=self.broker_id,coin_symbol=coin.coin_symbol,account_id=account['ID']).all()
            if len(addresses) >0:
                continue

            count=count+1

            time.sleep(0.3)
            chains = self.__get_deposit_address(currency=coin.coin_symbol)
            for chain in chains:
                coin_chain = chain['chain']
                coin_address = chain['address']
                coin_address_tag = ""
                if ":" in coin_address:
                    coin_address_parts = coin_address.split(":")
                    coin_address = coin_address_parts[0]
                    coin_address_tag = coin_address_parts[1]
                
                coin_deposit_address = Broker_Account_Deposit_Address()  
                coin_deposit_address.broker_id = self.broker_id
                coin_deposit_address.coin_symbol = coin.coin_symbol
                
                coin_deposit_address.crypto_address = coin_address
                coin_deposit_address.crypto_address_tag = coin_address_tag
                

                coin_deposit_address.chain = coin_chain.lower()
                coin_deposit_address.account_id = account['ID']
                
                coin_deposit_address.save()

            

    def __get_deposit_address(self,currency):

        
        try:
            method = 'GET'
            path = '/open/api/v2/asset/deposit/address/list'
            url = '{}{}'.format(self.ROOT_URL, path)
            original_params = {
                'currency': currency     
            }
            params = self._sign(method, path,original_params=original_params)

            

            response = requests.request(method, url, params=params)
            response_json = response.json()
            
            if response_json['code'] == 200:
                
                return response_json['data']['chains']
        except Exception as e:
            print(e)
            capture_exception(e)

        return []



        

    def _do_fetch_deposit_history(self):

        account = self._load_authenticated_client()
        if account is None:
            return None

            

        deposit_list = []

        try:
            method = 'GET'
            path = '/open/api/v2/asset/deposit/list'
            url = '{}{}'.format(self.ROOT_URL, path)            
            params = self._sign(method, path)

            
            original_params = {
                'page_size':   50
            }
            params = self._sign(method, path,original_params=original_params)
            response = requests.request(method, url, params=params)
            response_json = response.json()

            
            if response_json['code'] == 200:

                result_list = response_json['data']['result_list']
                # print(result_list)
                for record in result_list:
                    state = 0
                    if record['state'] =="SUCCESS":
                        state=1
                    deposit_list.append({
                    'broker_id': self.broker_id,
                    'coin_symbol': record['currency'],
                    'account_id':account['ID'],
                    'broker_history_id': record['tx_id'],
                    'amount': record['amount'],
                    'confirmations': record['confirmations'],
                    'txid': record['tx_id'],
                    'crypto_address': record['address'],
                    'crypto_address_tag': ''
                })
        


                
                pass
        except Exception as e:
            print(e)
            capture_exception(e)

        return deposit_list

