from ..common.broker_settings import Broker_Setting
from ..models import Broker_Account_Order

class BrokerWithdrawService:
    def __init__(self):
        
        self.brokers = Broker_Setting.BROKERS

    def withdraw(self,broker_id,coin_symbol,to_coin_address,tag,amount,unique_id='',network=''):
        for broker in self.brokers:
            broker_instance = broker()
            if broker_instance.broker_id == broker_id:
                
                return broker_instance.withdraw(coin_symbol=coin_symbol,to_coin_address=to_coin_address,tag=tag,amount=amount,unique_id=unique_id,network=network)
