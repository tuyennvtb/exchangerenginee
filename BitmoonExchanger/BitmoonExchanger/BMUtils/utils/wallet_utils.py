from django.conf import settings
import hashlib
from .constants import *
from .exchanger_utils import Exchanger_Utils
from .exchanger_logger import ExchangerLogger

import requests
import json

import logging
logger = logging.getLogger(__name__)

from sentry_sdk import capture_exception


class WalletUtils:
    @classmethod
    def create_limit_transaction(cls,transaction):
        url ="{0}/wallet/exchange/limit/create".format(settings.WALLET_URL)

        if transaction.user_id==0:
            return True
        

        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()

        payload =  {
            "user_id":transaction.user_id,
            "transaction_id":transaction.unique_id,
            "coin_id": transaction.coin_id,
            "action":transaction.action.upper(),
            "request_price": float(transaction.submitted_price_vnd or 0),
            "reserved_amount_for_trading": float(transaction.reserved_amount or 0),
            "request_quantity": float(transaction.coin_amount_submitted or 0),
            "trade_fee_percent": float(transaction.fee_percent or 0),
            "trade_fee_reserved": float(transaction.fee_reserved or 0),
            "reserved_amount":  float(transaction.reserved_amount + transaction.fee_reserved) # reserved_amount_for_trading  + trade_fee_reserved
        }      

        

        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)
        return status


    @classmethod
    def complete_limit_transaction_step(cls,transaction,transaction_step):
        url ="{0}/wallet/exchange/limit/partialcomplete".format(settings.WALLET_URL)

        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()

        
        payload = {
                "user_id" : transaction_step.user_id,
                "transaction_id" : transaction.unique_id,
                "unique_step": "{0}_{1}".format(transaction.unique_id,transaction_step.ID),
                "coin_traded_amount": float(transaction_step.coin_amount_filled or 0),
                "actual_price":float(transaction_step.final_vnd_price or 0),
                "trade_fee": float(transaction_step.total_fee or 0),
                "final_money_added": float(transaction_step.final_money_added or 0)  # This column changed the name
        }
        
        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)

        

        return status,json.dumps(payload),text

    @classmethod
    def complete_limit_transaction_trading_buy_step(cls,transaction,transaction_step):
        url ="{0}/wallet/exchange/limit/partialcomplete".format(settings.WALLET_URL)

        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()
        
        payload = {
                "user_id":transaction_step.buy_user_id,
                "transaction_id":transaction.unique_id,
                "unique_step": transaction_step.unique_id,
                "coin_traded_amount": float(transaction_step.coin_amount or 0),
                "actual_price":float(transaction_step.final_vnd_price or 0),
                "trade_fee": float(transaction_step.buy_fee or 0),
                "final_money_added": float(transaction_step.final_money_added_buy or 0)  # This column changed the name
        }
        
        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)

        

        return status,json.dumps(payload),text

    @classmethod
    def complete_limit_transaction_trading_sell_step(cls,transaction,transaction_step):
        url ="{0}/wallet/exchange/limit/partialcomplete".format(settings.WALLET_URL)
        
        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()

        payload = {
                "user_id":transaction.user_id,
                "transaction_id":transaction.unique_id,
                "unique_step": transaction_step.unique_id,
                "coin_traded_amount": float(transaction_step.coin_amount or 0),
                "actual_price":float(transaction_step.final_vnd_price or 0),
                "trade_fee": float(transaction_step.sell_fee or 0),
                "final_money_added": float(transaction_step.final_money_added_sell or 0)  # This column changed the name
        }
        
        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)

        

        return status,json.dumps(payload),text
        


    @classmethod
    def close_limit_transaction(cls,transaction):
        url ="{0}/wallet/exchange/limit/close".format(settings.WALLET_URL)
        payload = {
            "user_id":transaction.user_id,
            "transaction_id":transaction.unique_id,
            "status": transaction.system_status,
            "fee_refund": float(transaction.fee_refund or 0),
            "refunded_unspent":float(transaction.refund_amount or 0),
            "refunded_amount": float(transaction.refund_amount or 0) + float(transaction.fee_refund or 0), #// = fee_refund + refunded_unspent
        }

        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()

        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)
        return status,json.dumps(payload),text

    @classmethod
    def create_market_transaction(cls,transaction):
        if transaction.user_id==0:
            return True
        
        url ="{0}/wallet/exchange/market/create".format(settings.WALLET_URL)
        payload =  {
        "user_id":transaction.user_id,
        "base_currency":'VND',
        "transaction_id":transaction.unique_id,
        "coin_id": transaction.coin_id,
        "action":transaction.action.upper(),
        "total_amount": float(transaction.market_total_amount_submitted or 0),
        "curent_price": float(transaction.price_vnd_when_submit or 0)
        }


        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()
        

        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)
        return status


    @classmethod
    def close_market_transaction(cls,transaction):
        url = "{0}/wallet/exchange/market/close".format(settings.WALLET_URL)

        payload  = {
            "user_id":transaction.user_id,
            "transaction_id":transaction.unique_id,
            "status":transaction.system_status,
            "total_amount": float(transaction.market_total_amount_filled or 0),
            "total_fee": float(transaction.total_final_fee or 0),
            "final_price": float(transaction.avg_price_vnd or 0),
            "final_money_added":  float(transaction.final_money_added or 0),
            "refund_amount": float(transaction.refund_amount or 0)+ float(transaction.fee_refund or 0), #// = fee_refund + refunded_unspent
        }
        
        verified_key = hashlib.md5("{0}_{1}_{2}".format(transaction.unique_id,transaction.user_id,settings.EXCHANGER_WALLET_SECRET_KEY).encode()).hexdigest()

        status,text = cls._make_request(url=url,payload=payload,X_Api_Key=verified_key)
        return status,json.dumps(payload),text


    @classmethod
    def _make_request(cls,url,payload, X_Api_Key):
        
        status = False
        response = 'Unknown'
        
        try:
            headers = {'content-type': 'application/json', 'X-Api-Key': X_Api_Key}

            r = requests.post(url=url,data=payload)
            response_data = r.json()
            response = r.text
            if r.status_code == 200 and response_data['success']:
                status = True            
        except Exception as e:
            capture_exception(e)            
            response = str(e)

        ExchangerLogger.log_outgoing_request(url=url,payload=payload,response_text=response)        
        return status,response


    @classmethod
    def withdraw_status_update_success(cls,unique_id,status,txid):
        params = {
            'transaction_id': unique_id,
            'confirmation_number': 1,
            'status': 'VALIDATED',
            'trans_txid': txid
        }

        url = "{0}/withdraw/update".format(settings.WITHDRAW_API_URL)

        status, response = cls._make_request(url=url,payload=params)
        return status
    
    @classmethod
    def withdraw_status_update_fail(cls,unique_id):
        params = {
            'transaction_id': unique_id,
            'confirmation_number': 0,
            'status': 'FAILED'
        }

        url = "{0}/withdraw/update".format(settings.WITHDRAW_API_URL)
        status, response = cls._make_request(url=url,payload=params)
        return status