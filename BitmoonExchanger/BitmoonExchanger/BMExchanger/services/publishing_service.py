from ..business.publish_business import PublishBusiness
import _thread
import time
class PublishingService:
    def __init__(self):
        pass

    def publish_coins(self):
        try:
            _thread.start_new_thread(self.publish_coins_thread,())
        except Exception as e:
            # print(e)
            pass

        # self.publish_coins_thread()
        

    def publish_coins_thread(self):
        try:
            pb = PublishBusiness()
            while (True):         
                 
                pb.publish_coins()
                pb.publish_coin_settings()
                time.sleep(0.5)
        except Exception as e:
            print(e)
        

    def publish_coin_settings(self):
        PublishBusiness().publish_coin_settings()

    def publish_orderbook(self):
        
        PublishBusiness().publish_orderbook()