from .constants import *
from .cache_utils import CacheUtils
from ...BMExchanger.models import ExchangerCoinSetting,ExchangerCoinPriceModel,ExchangerTransaction,ExchangerAdminSetting
from ...BMBrokers.models import BrokerCoinPriceModel, BrokerMarketPairModel,CoinMarketCapModel
from ...BMUtils.utils.setting_utils import SettingUtils
from datetime import datetime
import pandas as pd

import json



class Exchanger_Utils:
    
    @classmethod
    def generate_uuid(cls,user_id):

        #Y,M,D,H,I,S,mili
        
        now = datetime.now()
        
        data = [Exchanger_Utils._hash(now.year-2000),Exchanger_Utils._hash(now.month),Exchanger_Utils._hash(now.day),Exchanger_Utils._hash(now.hour),Exchanger_Utils._hash(now.minute),Exchanger_Utils._hash(now.second),str(int(now.microsecond))]
        return ''.join(data)

    @classmethod
    def _hash(cls,number):
        number= int(number)
        if number<=9:
            return '{0}'.format(number)
        new_number = number + 55
        if new_number>=91 and new_number <=96:
            new_number = new_number + 6

        return chr(new_number)

    @classmethod
    def get_coin_setting(cls,coin_id):
        cache_key = "{0}_{1}".format(CacheKey.COIN_STATUS_PREFIX,coin_id)

        setting = CacheUtils.get_key(cache_key)

        if not setting:
            coin_settings = list(ExchangerCoinPriceModel.objects.filter(coin_id=coin_id).values())
            if len(coin_settings) != 1 :
                return False
            if coin_settings[0]['status']:
                setting = coin_settings[0]
                CacheUtils.cache_key(cache_key,setting)
        return setting

    @classmethod
    def get_market_pair(cls,broker_id,coin_id):
        
        

        cache_key = "{0}_{1}_{2}".format(CacheKey.BROKER_MARKET_PAIR_PREFIX,broker_id,coin_id)

        coin_pair = CacheUtils.get_key(cache_key)

        if not coin_pair:       
            
            coin_infos = list(BrokerCoinPriceModel.objects.filter(broker_id=broker_id,coin_id=coin_id).values())
            if len(coin_infos) ==1:
                usdt_pair = None
                btc_pair = None
                
                pairs = list(BrokerMarketPairModel.objects.filter(broker_id=broker_id,market_currency=coin_infos[0]['coin_symbol']).values())
                for pair in pairs:
                    if pair['status'] ==1 and pair['base_currency'] == CoinConstants.USDT:
                        usdt_pair = pair
                    if pair['status'] ==1 and pair['base_currency'] == CoinConstants.BITCOIN:
                        btc_pair = pair
                if usdt_pair:
                    coin_pair = usdt_pair
                elif btc_pair: 
                    coin_pair = btc_pair

                CacheUtils.cache_key(key=cache_key,value=coin_pair,ttl=10*60)
        return coin_pair

        

    @classmethod
    def get_coin_price(cls,coin_id):
        try:
            coin_price = ExchangerCoinPriceModel.objects.filter(coin_id=coin_id).get()
            return coin_price
        except Exception as e:
            return None

    @classmethod
    def get_coin_value(cls,coin_id, amount):
        coin_price = cls.get_coin_price(coin_id=coin_id)
        if coin_price:
            return float(amount) * float(coin_price.usd_ask_price)
        return 0

    @classmethod
    def get_bitcoin_price(cls):
        return cls.get_coin_price('bitcoin')

    @classmethod
    def get_open_transaction(cls):
        transactions = ExchangerTransaction.objects.filter(system_status=TransactionStatusConstants.OPEN).values()
        return transactions

    
        
    @classmethod
    def get_cmc_info(cls):     
        cmc_info = CacheUtils.get_key(CacheKey.CMC_INFO_CACHE_KEY)
        if not cmc_info:     
            cmc_info = []
            cmc_coin_list = CoinMarketCapModel.objects.values()
            for cmc_coin in cmc_coin_list:            
                cmc_info.append({
                    'coin_id': cmc_coin['coin_id'],
                    #'name': cmc_coin['name'],
                    #'symbol': cmc_coin['symbol'],
                    'rank': cmc_coin['cmc_rank'],
                    'volume_usd_24h': float(cmc_coin['volume_usd_24h']),
                    'percent_change_1h': float(cmc_coin['percent_change_1h']),
                    'percent_change_24h': float(cmc_coin['percent_change_24h'])

                })        
            CacheUtils.cache_key(CacheKey.CMC_INFO_CACHE_KEY,cmc_info,ttl=5*60)
        return cmc_info


