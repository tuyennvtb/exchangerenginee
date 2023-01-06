from ..business.exchanger_business import ExchangerBusiness
from ..tasks_publishing import publish_orderbook

class ExchangerService:
    def __init__(self):
        pass

    def user_submit_limit_transaction(self,user_id,coin_id,action,amount,price,custom_fee):
        data =  ExchangerBusiness().transaction_submit_limit(user_id=user_id,coin_id=coin_id.lower(),action=action.upper(),amount=amount,price=price,custom_fee=custom_fee)
        publish_orderbook.delay()
        return data
    

    def user_submit_market_transaction(self,user_id,coin_id,action,total_amount,custom_fee):
        data = ExchangerBusiness().transaction_submit_market(user_id=user_id,coin_id=coin_id.lower(),action=action.upper(),total_amount=total_amount,custom_fee=custom_fee)
        publish_orderbook.delay()
        return data
        
    def user_cancel_transaction(self,user_id,transaction_id):
        data =  ExchangerBusiness().user_cancel_transaction(user_id=user_id,transaction_id=transaction_id)
        publish_orderbook.delay()
        return data