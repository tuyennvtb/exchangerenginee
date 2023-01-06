from ..business.withdraw_business import WithdrawBusiness
class WithdrawService:
    def __init__(self):
        pass

    def submit_request(self,coin_id,network,to_coin_address,tag,amount,unique_id,signature):
        return WithdrawBusiness().submit_request(coin_id=coin_id,network=network,to_coin_address=to_coin_address,tag=tag,amount=amount,unique_id=unique_id,signature=signature)

    def do_withdraw(self):
        WithdrawBusiness().do_withdraw()

    def update_withdraw_status(self):
        pass