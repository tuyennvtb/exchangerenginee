from django.core.management.base import BaseCommand, CommandError



from binance.client import Client

from ....BMBrokers.brokers.broker_binance import BrokerBinance

from ....BMBrokers.services.broker_service import BrokerService
from ....BMBrokers.business.cmc_business import CoinMarketcapBusiness
from ....BMBrokers.business.broker_business import BrokerBusiness
from ....BMExchanger.services.exchanger_service import ExchangerService
from ....BMExchanger.services.transaction_service import TransactionService
from ....BMExchanger.services.publishing_service import PublishingService
from ....BMExchanger.services.schedule_service import ScheduleService as ExchangerScheduleService
from ....BMExchanger.services.withdraw_service import WithdrawService
from ...services.schedule_service import Schedule_Service as CentralScheduleService
from ....BMExchanger.business.publish_business import PublishBusiness
from ....BMUtils.utils.exchanger_utils import Exchanger_Utils
from ....BMUtils.utils.encryption_utils import EncryptionUtils
import datetime
import pandas as pd
import time

from ....BMBrokers.brokers.broker_huobi import BrokerHuobi
from ....BMBrokers.brokers.broker_mxc import BrokerMXC
from ....BMExchanger.business.fulfillment_business import Fulfillment

import jwt

class Command(BaseCommand):

    def handle(self, *args, **options):
        
        # self.setup_markets()

        # encoded_jwt="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NTI2LCJuYW1lIjoiTkdVWUVOIEggTkhBVCBUSEFOSCIsInN1cm5hbWUiOm51bGwsInVzZXJuYW1lIjpudWxsLCJlbWFpbCI6InRlc3R4cnAxQHlvcG1haWwuY29tIiwiaXNfYWN0aXZhdGVkIjoxLCJjb3VudHJ5X2NvZGUiOiJWTiIsIm1vYmlsZSI6Iis4NC04NS0xNDMzLTk2IiwiaWF0IjoxNjMzNzIxNDg0LCJleHAiOjE2MzczMjE0ODR9.2anFMJyN0N2z2Hwk1T1-xTqFdo3ry2WAdfa9MVJWn_4"
        # secret = "q%k%ZD37@*U98b7#jbe@378%u"

        # raw = jwt.decode(encoded_jwt, secret, algorithms=["HS256"])
        # print(raw)

        # self.huobi_deposit_address()
        # self.binance_deposit_address()
        
        #self.websocket()

        #self.exchanger_limit()
        #self.exchanger_market()

        #self.process_transaction()
        #self.match_broker_order()
        #self.call_to_update_wallet()
        #self.test()
        #self.cancel_transaction()
        #self.trade_transaction()
        #self.call_to_update_wallet()

        #self.publish_coins()
        # self.publish_coin_settings()

        #self.setup_markets()

        # self.huobi_order()
        # self.binance_order()
        # self.fulfullment()

        # self.binance_balance()
        
        # self.binance_withdraw_history()
        # self.huobi_deposit()
        # self.binance_deposit()

        self.encryption()

        # self.binance_withdraw_network()

        # self.withdraw()
        
        # self.binance()
        # self.binance_balance()

        # PublishingService().publish_orderbook()

        # self.binance_deposit_address()
        # self.huobi_deposit_address()

        # self.publish_coin_settings()

        # self.binance_coin_info()
        # self.huobi_coin_info()
        # self.fulfullment()

        # self.withdraw_history()
        # self.mxc_order()   
        # self.mxc_balance()  
        # self.mxc_deposit()


    def websocket(self):
        service = BrokerService()
        service.start_websocket()


    def binance(self):
        # client = Client('', '')
        # depth = client.get_order_book(symbol='BNBBTC')
        # print(depth)

        binance = BrokerBinance()
        #BrokerBusiness(broker=binance).broker_auto_mapping()
        binance.submit_order_market(action='BUY',pair='LTCUSDT',total_amount=0.2,by='quantity')


    def exchanger_limit(self):
        result = ExchangerService().user_submit_limit_transaction(user_id=1,coin_id='ripple',action='buy',amount=41,price=11000,custom_fee=0.15)
        

    def exchanger_market(self):
        result = ExchangerService().user_submit_market_transaction(user_id=1,coin_id='ripple',action='sell',total_amount=30.5,custom_fee=0.15)
        


    def process_transaction(self):
        TransactionService().process_transaction(unique_id='KBSGGk457880')

    def match_broker_order(self):
        TransactionService().match_broker_order(unique_id='KBSGGk457880')

    def call_to_update_wallet(self):
        ExchangerScheduleService().retry_wallet()
        



    def setup_markets(self):
        CentralScheduleService().setup()
        print("DONE")


    
    def huobi(self):
        hb = BrokerHuobi()
        hb.start_websocket()
    

    def cancel_transaction(self):
        result = ExchangerService().user_cancel_transaction(user_id=1, transaction_id='KBSGpp493846')
        print(result)

    def trade_transaction(self):
        TransactionService().process_trade_transaction(buy_unique_id='KBTFRN434935',sell_unique_id='KBSGjK872430')

    def publish_coins(self):
        
        # print(now.second)
        ExchangerScheduleService().publish_coins()

        #cmc = Exchanger_Utils.get_cmc_info()

    def publish_coin_settings(self):
        PublishBusiness().publish_coin_bm()


    def huobi_order(self):

        hb = BrokerHuobi()
        #hb.submit_order_market(action='SELL',pair='HTUSDT',total_amount=2.631000000)
        hb.submit_order_limit(action='BUY',pair='HTUSDT',amount=3,price=5.154737000)
        pass

    def mxc_order(self):
        mxc = BrokerMXC()
        mxc.submit_order_limit(action='SELL',pair='LTC_USDT',amount=0.2,price=150)

    def mxc_balance(self):
        mxc = BrokerMXC()
        mxc.fetch_balance()

    def mxc_deposit(self):
        mxc = BrokerMXC()
        mxc.fetch_deposit_history()
        

    def binance_order(self):
        bn = BrokerBinance()
        # bn.submit_order_market(action="SELL",pair="ADAUSDT",total_amount=10)
        bn.submit_order_limit(action='BUY',pair="ADAUSDT",amount=10,price=2.6)

    def fulfullment(self):
        Fulfillment().process_limit_step(step_id=62)
        # Fulfillment().process_market_step(step_id=10)

    def binance_balance(self):
        bn = BrokerBinance()
        bn.fetch_balance()

    
        
    def huobi_balance(self):
        hb = BrokerHuobi()
        hb.fetch_balance()

    def binance_deposit(self):
        bn = BrokerBinance()
        bn.fetch_deposit_history()

    def huobi_deposit(self):
        hb = BrokerHuobi()
        hb.fetch_deposit_history()

    def binance_deposit_address(self):
        bn = BrokerBinance()
        bn.fetch_deposit_address()

    def binance_withdraw_network(self):
        bn = BrokerBinance()
        bn.fetch_coin_network()

    def huobi_deposit_address(self):
        hb = BrokerHuobi()
        hb.fetch_deposit_address()

    def binance_withdraw_history(self):
        bn = BrokerBinance()
        bn.fetch_withdraw_history()

    def binance_coin_info(self):
        bn = BrokerBinance()
        bn.fetch_coin_info()

    def huobi_coin_info(self):
        hb = BrokerHuobi()
        hb.fetch_coin_info()

    def withdraw(self):
        WithdrawService().do_withdraw()

    def withdraw_history(self):
        pass

    def encryption(self):
        x = EncryptionUtils().encrypt("nGiksFzddg7BKughs89RgbRC0ZNkLiOgYo4IbK0QJzN2z1A9tYDM8nIeATAJfykH")
        print(x)
        # dK5sCYZwmLnwAfUO9MNcQdosj3S26apmKTuquJDhBmxHJuw54ACNbvMdCtp2wNKf
        # kWjo40DVT7sr4cDskfb9m9VBQgoWeDnFphtbrca8GTyzTm7KrYucuqyC4a6BM0Ak




        y= EncryptionUtils().decrypt("h/TeF4VL76NEE24EwvRZuPhFWLByUPEsk6HLnM9Uxd94rRioD7AitZGzhr6YCg7+FiR+6pdPbMtfLv6Wxpqu3g==")
        print(y)