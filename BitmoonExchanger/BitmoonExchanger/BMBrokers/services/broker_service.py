
from ..common.broker_settings import Broker_Setting
from ..business.cmc_business import CoinMarketcapBusiness
from ..business.broker_business import BrokerBusiness
from ..business.realtime_business import RealtimeBusiness


from ...BMExchanger.services.realtime_service import RealtimeService as ExchangerRealtimeService

class BrokerService:
    def __init__(self):
        
        self.brokers = Broker_Setting.BROKERS
    
    def get_brokers(self):
        return self.brokers


    def start_websocket(self):
        for broker in self.brokers:
            broker_instance = broker()
            broker_instance.start_websocket()
            
            
            exchanger = ExchangerRealtimeService(broker=broker_instance)
            RealtimeBusiness(broker=broker_instance,exchanger_realtime_service=exchanger).start()

