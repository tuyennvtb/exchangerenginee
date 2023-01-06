from ..business.realtime_business import RealtimeBusiness

class RealtimeService:
    def __init__(self,broker=None):
        self.broker = broker
        self.realtime_business = RealtimeBusiness(broker=broker)

    def process_usd_price(self,df):
        self.realtime_business.process_usd_price(df)