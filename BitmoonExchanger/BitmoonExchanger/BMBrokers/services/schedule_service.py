from .broker_service import BrokerService
from ..business.broker_business import BrokerBusiness
from ..business.cmc_business import CoinMarketcapBusiness

from sentry_sdk import capture_exception

class ScheduleService:
    def __init__(self):
        
        self.brokers = BrokerService().get_brokers()

    def setup_markets(self):
        
        
        #Get data from CMC
        CoinMarketcapBusiness(brokers=BrokerService().get_brokers()).setup()
        
        #Map CMC coins
        # BrokerBusiness().cmc_auto_mapping()

        #Map Coins by Market
        for broker in self.brokers:
            broker_instance = broker()
            #Automatically Mapping Coins        
            BrokerBusiness(broker=broker_instance).get_markets()
            # BrokerBusiness(broker=broker_instance).broker_auto_mapping()
            

        # BrokerBusiness().update_coin_id_to_broker_price()
        BrokerBusiness().update_base_currency()

    def fetch_balance(self):
        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_balance()
            except Exception as e: 
                capture_exception(e)

    def fetch_deposit_history(self):
        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_deposit_history()
            except Exception as e: 
                capture_exception(e)

    def fetch_deposit_address(self):

        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_deposit_address()
            except Exception as e: 
                capture_exception(e)
    
    def fetch_coin_info(self):        
        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_coin_info()
            except Exception as e: 
                capture_exception(e)

    def fetch_coin_network(self):        
        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_coin_network()
            except Exception as e: 
                capture_exception(e)
    
    def fetch_withdraw_history(self):
        for broker in self.brokers:
            try:
                broker_instance = broker()
                broker_instance.fetch_withdraw_history()
            except Exception as e: 
                capture_exception(e)
                
    
