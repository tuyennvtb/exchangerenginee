from sentry_sdk.api import capture_exception
from ..common.broker_settings import Broker_Setting
from ..models import Broker_Account_Order

class BrokerTradingService:
    def __init__(self):
        
        self.brokers = Broker_Setting.BROKERS

    def submit_transaction_limit(self,broker_id,action,pair,amount,price):
        for broker in self.brokers:
            try:
                broker_instance = broker()
                if broker_instance.broker_id == broker_id:
                    print("Submitting to {0}".format(broker_id))
                    return broker_instance.submit_order_limit(action,pair,amount,price)
            except Exception as e:
                capture_exception(e)


    def submit_transaction_market(self,broker_id,action,pair,total_amount,by='default'):
        for broker in self.brokers:
            broker_instance = broker()
            if broker_instance.broker_id == broker_id:
                print("Submitting to {0}".format(broker_id))
                return broker_instance.submit_order_market(action,pair,total_amount,by)


    def find_account_order(self,broker_id,order_id):
        
        return Broker_Account_Order.objects.filter(broker_id=broker_id,orderId=order_id).get()
                

        