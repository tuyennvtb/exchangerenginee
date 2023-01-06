from ...BMUtils.utils.setting_utils import SettingUtils
from ..models import ExchangerWithdrawRequest, ExchangerCoinSetting
from ...BMBrokers.models import BrokerCoinPriceModel,Broker_Withdraw_History
from ...BMUtils.utils.constants import *
import hashlib 

from django.db import transaction as django_transaction

from ...BMUtils.utils.exchanger_utils import Exchanger_Utils
#from
from ...BMBrokers.services.broker_withdraw_service import BrokerWithdrawService

from ...BMUtils.utils.wallet_utils import WalletUtils


from sentry_sdk import capture_exception


class WithdrawBusiness:
    def __init__(self):
        pass

    def submit_request(self,coin_id,network,to_coin_address,tag,amount,unique_id,signature):
        verified_signature = hashlib.md5(("{coin_id}{to_coin_address}{unique_id}AwesomeBitmoon".format(coin_id=coin_id.lower(),to_coin_address=to_coin_address.lower(),unique_id=str(unique_id).lower())).encode()).hexdigest()

        print(verified_signature)
        
        result = {
                'success': False,
                'error_code': APIErrorCodeConstants.UNKNOWN_ERROR,
        }

        if SettingUtils.enable_withdraw() and signature == verified_signature:
            
            try:
                withdraw_request = ExchangerWithdrawRequest()
                withdraw_request.coin_id =coin_id
                withdraw_request.to_coin_address = to_coin_address
                withdraw_request.tag=tag
                withdraw_request.amount=amount
                withdraw_request.unique_id=unique_id
                withdraw_request.network = network
                withdraw_request.status= WithdrawRequestStatusConstants.OPEN
                withdraw_request.save()
                
                result = {
                    'success': True,
                    'error_code': APIErrorCodeConstants.SUCCESS,
                    'data': {
                        'id': withdraw_request.ID
                    }
                }
            except:
                pass

        return result

    def do_withdraw(self):

        withdraw_requests = ExchangerWithdrawRequest.objects.filter(status=WithdrawRequestStatusConstants.OPEN).all()
        for rq in withdraw_requests:
            try:
                with django_transaction.atomic():

                    withdraw_request = ExchangerWithdrawRequest.objects.filter(ID=rq.ID).get()
                    if withdraw_request.status != WithdrawRequestStatusConstants.OPEN:
                        return

                    coin_info = Exchanger_Utils.get_coin_price(coin_id=withdraw_request.coin_id)

                    
                    
                    broker_coin_info = BrokerCoinPriceModel.objects.filter(broker_id=coin_info.broker_id, coin_id=withdraw_request.coin_id).get()

                    network = withdraw_request.network
                    if network is None:
                        coin_setting = ExchangerCoinSetting.objects.filter(coin_id=withdraw_request.coin_id).first()
                        network=coin_setting.default_withdraw_network

                    request_id = BrokerWithdrawService().withdraw(broker_id=coin_info.broker_id, coin_symbol=broker_coin_info.coin_symbol,to_coin_address=withdraw_request.to_coin_address,tag=withdraw_request.tag,amount=withdraw_request.amount,unique_id=withdraw_request.unique_id,network=network)

                    withdraw_request.broker_reference_id = request_id
                    withdraw_request.status  = WithdrawRequestStatusConstants.SUBMITTED
                    if request_id is None:
                        withdraw_request.status  = WithdrawRequestStatusConstants.ERROR
                    
                    withdraw_request.save()

            except Exception as e:
                print(e)
                capture_exception(e)
        


    def match_withdraw(self):
        withdraw_requests = ExchangerWithdrawRequest.objects.filter(status=WithdrawRequestStatusConstants.SUBMITTED).all()
        for withdraw_request in withdraw_requests:
            print(withdraw_request.unique_id)
            try:
                withdraw_history = Broker_Withdraw_History.objects.filter(unique_id=withdraw_request.broker_reference_id).get()
                withdraw_request.txid =  withdraw_history.txId
                withdraw_request.status = WithdrawRequestStatusConstants.DONE
                withdraw_request.save()
                
            except Exception as e :
                pass


    def notify_withdraw(self):
        withdraw_requests = ExchangerWithdrawRequest.objects.filter(status=WithdrawRequestStatusConstants.DONE,wallet_status__lt=1,wallet_request_count__lt=10).all()
        for withdraw_request in withdraw_requests:
            
            status = WalletUtils.withdraw_status_update_success(unique_id=withdraw_request.unique_id,status=withdraw_request.status,txid=withdraw_request.txid)
            if status:
                withdraw_request.wallet_status = 1
            else:
                withdraw_request.wallet_status = 0
                withdraw_request.wallet_request_count = withdraw_request.wallet_request_count + 1

            withdraw_request.save()

        withdraw_requests = ExchangerWithdrawRequest.objects.filter(status=WithdrawRequestStatusConstants.ERROR,wallet_status__lt=1,wallet_request_count__lt=10).all()
        for withdraw_request in withdraw_requests:
            
            status = WalletUtils.withdraw_status_update_fail(unique_id=withdraw_request.unique_id)
            if status:
                withdraw_request.wallet_status = 1
            else:
                withdraw_request.wallet_status = 0
                withdraw_request.wallet_request_count = withdraw_request.wallet_request_count + 1

            withdraw_request.save()

