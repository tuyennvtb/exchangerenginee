from django.conf import settings

from ...BMUtils.utils.constants import *
from ...BMUtils.utils.exchanger_utils import Exchanger_Utils
from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.wallet_utils import WalletUtils
from ...BMUtils.utils.setting_utils import SettingUtils
from ...BMUtils.utils.money_utils import MoneyUtils
from ...BMBrokers.services.broker_trading_service import BrokerTradingService
from ..models import ExchangerTransaction
from .publish_business import PublishBusiness

from sentry_sdk import capture_exception


class ExchangerBusiness:
    
    def __init__(self):
        pass

    def transaction_submit_limit(self,user_id,coin_id,action,amount,price,custom_fee):
        
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR,
            'base_currency': 'VND'
        }

        
        try:

            if user_id <0:
                result['error_code'] = APIErrorCodeConstants.INVALID_USER_ID
                return result

            if amount <=0:
                result['error_code'] = APIErrorCodeConstants.INVALID_AMOUNT
                return result

            if price <=0:
                result['error_code'] = APIErrorCodeConstants.INVALID_PRICE
                return result

            if amount*price < settings.MINIMUM_TRANSACTION_VALUE:
                result['error_code'] = APIErrorCodeConstants.AMOUNT_TOO_SMALL
                return result

            
            coin_setting  = Exchanger_Utils.get_coin_setting(coin_id=coin_id)
            if coin_setting is None:
                result['error_code'] = APIErrorCodeConstants.COIN_IS_NOT_SUPPORTED
                return result
                

            if coin_setting['status'] < 1 : 
                result['error_code'] = APIErrorCodeConstants.COIN_IS_DISABLED
                return result

            if not ExchangerTransactionType.check_valid_transaction_action(action=action):
                result['error_code'] = APIErrorCodeConstants.INVALID_ACTION
                return result

            fee_percent = SettingUtils.get_user_trading_fee(custom_fee=custom_fee)

        
            transaction = None
            if action == ExchangerTransactionType.BUY:
                transaction = self._calculate_buy_transaction_limit(user_id=user_id,coin_setting=coin_setting,amount=amount,price=price,fee_percent=fee_percent)
                transaction.save()
            if action == ExchangerTransactionType.SELL:
                transaction = self._calculate_sell_transaction_limit(user_id=user_id,coin_setting=coin_setting,amount=amount,price=price,fee_percent=fee_percent)
                transaction.save()
            
            if transaction == None:
                return result

            if WalletUtils.create_limit_transaction(transaction=transaction):            
                transaction.system_status = TransactionStatusConstants.OPEN
                transaction.display_status = TransactionStatusConstants.OPEN
                transaction.save()
                result['success'] = True
                result['error_code'] = APIErrorCodeConstants.SUCCESS
                result['data'] = {
                    'id': transaction.ID,
                    'transaction_id': transaction.unique_id,
                    'coin_id': transaction.coin_id,
                    'trade_mode':transaction.trade_mode,
                    'action':transaction.action,
                    'coin_amount_submitted': float(transaction.coin_amount_submitted),
                    'coin_amount_filled': float(transaction.coin_amount_filled) ,
                    'estimate_vnd_amount': float(transaction.estimate_vnd_amount),
                    'submitted_price_vnd':float(transaction.submitted_price_vnd),
                    'reserved_amount': float(transaction.reserved_amount),                    
                    'status': transaction.display_status,
                    'created_at': DatetimeUtils.formatTime(transaction.created_at),
                    'market_total_amount_submitted':float(transaction.market_total_amount_submitted)
                }
                
                print("XXXXXXXXXXXXXXXXXXXxx")

                PublishBusiness().publish_transaction(transaction=transaction)
                
            else:
                transaction.delete()
                result['error_code'] = APIErrorCodeConstants.INSUFFICIENT_FUNDS
                return result
        except Exception as e:
            capture_exception(e)
            pass

        
        return result

    def transaction_submit_market(self,user_id,coin_id,action,total_amount,custom_fee):
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR            
        }

        if user_id <0:
            result['error_code'] = APIErrorCodeConstants.INVALID_USER_ID
            return result

        if total_amount <=0:
            result['error_code'] = APIErrorCodeConstants.INVALID_AMOUNT
            return result
        
        coin_setting  = Exchanger_Utils.get_coin_setting(coin_id=coin_id)
        if coin_setting is None:
            result['error_code'] = APIErrorCodeConstants.COIN_IS_NOT_SUPPORTED
            return result
            

        if coin_setting['status'] < 1 :
            result['error_code'] = APIErrorCodeConstants.COIN_IS_DISABLED
            return result

        if not ExchangerTransactionType.check_valid_transaction_action(action=action):
            result['error_code'] = APIErrorCodeConstants.INVALID_ACTION
            return result


        coin_setting  = Exchanger_Utils.get_coin_setting(coin_id=coin_id)
        if coin_setting is None:
            print("Coin is not enabled")
            return

        

        if action == ExchangerTransactionType.BUY and total_amount < settings.MINIMUM_TRANSACTION_VALUE:
            result['error_code'] = APIErrorCodeConstants.AMOUNT_TOO_SMALL
            return result

        if action == ExchangerTransactionType.SELL and total_amount*float(coin_setting['vnd_bid_price']) < settings.MINIMUM_TRANSACTION_VALUE:
            result['error_code'] = APIErrorCodeConstants.AMOUNT_TOO_SMALL
            return result



        fee_percent = SettingUtils.get_user_trading_fee(custom_fee=custom_fee)

        transaction = None
        if action == ExchangerTransactionType.BUY:
            transaction = self._calculate_buy_transaction_market(user_id=user_id,coin_setting=coin_setting,total_amount=total_amount,fee_percent=fee_percent)
            transaction.save()
        if action == ExchangerTransactionType.SELL:
            transaction = self._calculate_sell_transaction_market(user_id=user_id,coin_setting=coin_setting,total_amount=total_amount,fee_percent=fee_percent)
            transaction.save()

        if transaction == None:
            return result

        if WalletUtils.create_market_transaction(transaction=transaction):
            transaction.system_status = TransactionStatusConstants.OPEN
            transaction.display_status = TransactionStatusConstants.OPEN
            transaction.save()
            result['success'] = True
            result['error_code'] = APIErrorCodeConstants.SUCCESS
            result['data'] = {
                    'id': transaction.ID,
                    'transaction_id': transaction.unique_id,
                    'coin_id': transaction.coin_id,
                    'trade_mode':transaction.trade_mode,
                    'action':transaction.action,
                    'coin_amount_submitted': float(transaction.coin_amount_submitted),
                    'coin_amount_filled': float(transaction.coin_amount_filled) ,
                    'estimate_vnd_amount': float(transaction.estimate_vnd_amount),
                    'submitted_price_vnd':float(transaction.submitted_price_vnd),
                    'reserved_amount': float(transaction.reserved_amount),                    
                    'status': transaction.display_status,
                    'created_at': DatetimeUtils.formatTime(transaction.created_at),
                    'market_total_amount_submitted':float(transaction.market_total_amount_submitted)
                }


            PublishBusiness().publish_transaction(transaction=transaction)

        else:
            transaction.delete()
            result['error_code'] = APIErrorCodeConstants.INSUFFICIENT_FUNDS
            return result

        return result

        
        

    def _calculate_buy_transaction_limit(self,user_id,coin_setting,amount,price,fee_percent):

        transaction = ExchangerTransaction()
        transaction.action = ExchangerTransactionType.BUY
        transaction.user_id=user_id
        transaction.coin_id=coin_setting['coin_id']
        transaction.trade_mode=ExchangerModeConstants.LIMIT
        transaction.unique_id = Exchanger_Utils.generate_uuid(user_id=user_id)
        transaction.base_currency = CoinConstants.VND
        transaction.price_vnd_when_submit = coin_setting['vnd_ask_price']

        transaction.coin_amount_submitted = amount
        transaction.coin_amount_filled = 0
        transaction.submitted_price_vnd = price
        transaction.market_total_amount_submitted = 0
        transaction.market_total_amount_filled = 0
        transaction.fee_percent = fee_percent
        transaction.reserved_amount =  MoneyUtils.round_money(number=amount*price,currency=CoinConstants.VND)
        transaction.fee_reserved  = MoneyUtils.round_money(number=float(transaction.reserved_amount) * float(transaction.fee_percent)/100.0,currency=CoinConstants.VND)
        
        transaction.reserved_remainings = transaction.reserved_amount
        transaction.estimate_vnd_amount = transaction.reserved_amount + transaction.fee_reserved
        transaction.system_status = TransactionStatusConstants.NEW
        transaction.display_status = TransactionStatusConstants.NEW
        transaction.created_at = DatetimeUtils.getCurrentTime()
        transaction.updated_at = DatetimeUtils.getCurrentTime()
        
        return transaction

    def _calculate_sell_transaction_limit(self,user_id,coin_setting,amount,price,fee_percent):
        
        transaction = ExchangerTransaction()
        transaction.action = ExchangerTransactionType.SELL
        transaction.user_id=user_id
        transaction.coin_id=coin_setting['coin_id']
        transaction.trade_mode=ExchangerModeConstants.LIMIT
        transaction.unique_id = Exchanger_Utils.generate_uuid(user_id=user_id)
        transaction.base_currency = CoinConstants.VND
        transaction.price_vnd_when_submit = coin_setting['vnd_bid_price']

        transaction.coin_amount_submitted = amount
        transaction.coin_amount_filled = 0
        transaction.submitted_price_vnd = price
        transaction.market_total_amount_submitted = 0
        transaction.market_total_amount_filled = 0
        transaction.fee_percent = fee_percent
        transaction.reserved_amount = amount
        transaction.fee_reserved  = 0
        
        transaction.reserved_remainings = transaction.reserved_amount
        transaction.estimate_vnd_amount = MoneyUtils.round_money(amount*price*(1-float(transaction.fee_percent)/100.0), CoinConstants.VND)
        transaction.system_status = TransactionStatusConstants.NEW
        transaction.display_status = TransactionStatusConstants.NEW
        transaction.created_at = DatetimeUtils.getCurrentTime()
        transaction.updated_at = DatetimeUtils.getCurrentTime()
        
        return transaction

    def _calculate_buy_transaction_market(self,user_id,coin_setting,total_amount,fee_percent):
        
        transaction = ExchangerTransaction()
        transaction.action = ExchangerTransactionType.BUY
        transaction.user_id=user_id
        transaction.coin_id=coin_setting['coin_id']
        transaction.trade_mode=ExchangerModeConstants.MARKET
        transaction.unique_id = Exchanger_Utils.generate_uuid(user_id=user_id)
        transaction.base_currency = CoinConstants.VND
        transaction.price_vnd_when_submit = coin_setting['vnd_ask_price']
        transaction.coin_amount_submitted = 0
        transaction.coin_amount_filled = 0
        transaction.submitted_price_vnd =0
        transaction.market_total_amount_submitted = MoneyUtils.round_money(number=total_amount, currency=CoinConstants.VND)
        transaction.market_total_amount_filled = 0
        transaction.fee_percent = fee_percent
        transaction.fee_reserved  = MoneyUtils.round_money(number=float(transaction.market_total_amount_submitted) * float(transaction.fee_percent) / 100.0, currency=CoinConstants.VND)
        transaction.reserved_amount = float(transaction.market_total_amount_submitted) - float(transaction.fee_reserved)
        transaction.reserved_remainings = transaction.reserved_amount
        transaction.estimate_vnd_amount = total_amount       
        transaction.system_status = TransactionStatusConstants.NEW
        transaction.display_status = TransactionStatusConstants.NEW
        transaction.created_at = DatetimeUtils.getCurrentTime()
        transaction.updated_at = DatetimeUtils.getCurrentTime()

        
        
        return transaction

    def _calculate_sell_transaction_market(self,user_id,coin_setting,total_amount,fee_percent):
        
        transaction = ExchangerTransaction()
        transaction.action = ExchangerTransactionType.SELL
        transaction.user_id=user_id
        transaction.coin_id=coin_setting['coin_id']
        transaction.trade_mode=ExchangerModeConstants.MARKET
        transaction.unique_id = Exchanger_Utils.generate_uuid(user_id=user_id)
        transaction.base_currency = CoinConstants.VND
        transaction.price_vnd_when_submit = coin_setting['vnd_bid_price']
        transaction.coin_amount_submitted = total_amount
        transaction.coin_amount_filled = 0
        transaction.submitted_price_vnd = 0
        transaction.market_total_amount_submitted = total_amount
        transaction.market_total_amount_filled = 0
        transaction.fee_percent = fee_percent
        transaction.fee_reserved  = 0
        transaction.reserved_amount = total_amount
        transaction.reserved_remainings = transaction.reserved_amount
        transaction.estimate_vnd_amount = 0       
        transaction.system_status = TransactionStatusConstants.NEW
        transaction.display_status = TransactionStatusConstants.NEW
        transaction.created_at = DatetimeUtils.getCurrentTime()
        transaction.updated_at = DatetimeUtils.getCurrentTime()
        
        return transaction

    def user_cancel_transaction(self,user_id,transaction_id):
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR
        }
        try:
            transaction = ExchangerTransaction.objects.filter(unique_id=transaction_id).get()
            if transaction.user_id != user_id or transaction.system_status == TransactionStatusConstants.NEW  :
                result ['error_code'] =  APIErrorCodeConstants.TRANSACTION_NOT_FOUND

                return result

            if transaction.system_status != TransactionStatusConstants.DONE:            
                transaction.display_status = TransactionStatusConstants.REQUEST_CANCEL
                transaction.save()

            result['success'] = True
            result['error_code'] = APIErrorCodeConstants.SUCCESS


        except Exception as e:
            result ['error_code'] =  APIErrorCodeConstants.TRANSACTION_NOT_FOUND
            capture_exception(e)
            
        
        return result

