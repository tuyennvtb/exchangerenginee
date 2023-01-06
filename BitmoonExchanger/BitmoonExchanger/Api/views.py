import logging
import json

from django.conf import settings

from django.shortcuts import render
from django.http import HttpResponse

import json
from django.views.decorators.csrf import csrf_exempt
from ..BMExchanger.services.exchanger_service import ExchangerService
from ..BMExchanger.services.withdraw_service import WithdrawService
from ..BMUtils.utils.exchanger_logger import ExchangerLogger
import jwt
from ..BMUtils.utils.constants import *
import hashlib 


def index(request):
    # test Service Provider
    return HttpResponse("This is an Index of API")

def validate_jwt(encoded_jwt, user_id):
    raw = jwt.decode(encoded_jwt, settings.BACKEND_JWT_SECRET_KEY, algorithms=["HS256"])

    if raw['id'] == user_id:
        return True
    return False

def validate_sig(request,user_id):
    X_Api_Key=request.headers['X-Api-Key'] 
    verified_key = hashlib.md5("{0}_{1}".format(user_id,settings.BACKEND_EXCHANGER_SECRET_KEY).encode()).hexdigest()

    if verified_key == X_Api_Key:
        return True
    return False


@csrf_exempt
def transaction_limit(request):    
    json_data = json.loads(request.body.decode('utf-8'))

    result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR
            
        }

    
    if not validate_jwt(encoded_jwt=json_data['jwt'],user_id=json_data['user_id']) or not validate_sig(request=request,user_id=json_data['user_id']):
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.INVALID_SIG
            
        }
    else:

        result  = ExchangerService().user_submit_limit_transaction(user_id=json_data['user_id'],coin_id=json_data['coin_id'],action=json_data['action'],amount=json_data['amount'],price=json_data['price'],custom_fee=json_data['custom_fee'])
    
    #Log Request
    ExchangerLogger.log_incoming_request(url=request.build_absolute_uri(),payload=json_data,response=result)

    return HttpResponse(json.dumps(result))

@csrf_exempt
def transaction_market(request):
    json_data = json.loads(request.body.decode('utf-8'))

    result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR
            
        }

    
    if not validate_jwt(encoded_jwt=json_data['jwt'],user_id=json_data['user_id']) or not validate_sig(request=request,user_id=json_data['user_id']):
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.INVALID_SIG
            
        }
    else:
        result = ExchangerService().user_submit_market_transaction(user_id=json_data['user_id'],coin_id=json_data['coin_id'],action=json_data['action'],total_amount=json_data['total_amount'],custom_fee=json_data['custom_fee'])

    #Log Request
    ExchangerLogger.log_incoming_request(url=request.build_absolute_uri(),payload=json_data,response=result)

    return HttpResponse(json.dumps(result))


@csrf_exempt
def transaction_cancel(request):
    json_data = json.loads(request.body.decode('utf-8'))

    result = {
            'success': False,
            'error_code': APIErrorCodeConstants.UNKNOWN_ERROR            
        }
    
    if not validate_jwt(encoded_jwt=json_data['jwt'],user_id=json_data['user_id']) or not validate_sig(request=request,user_id=json_data['user_id']):
        result = {
            'success': False,
            'error_code': APIErrorCodeConstants.INVALID_SIG
            
        }
    else:
        result = ExchangerService().user_cancel_transaction(user_id=json_data['user_id'],transaction_id=json_data['transaction_id'])

    #Log Request
    ExchangerLogger.log_incoming_request(url=request.build_absolute_uri(),payload=json_data,response=result)

    return HttpResponse(json.dumps(result))

# @csrf_exempt
# def withdraw_request(request):
#     json_data = json.loads(request.body.decode('utf-8'))
#     network = None
#     if 'network' in json_data:
#         network = json_data['network']

#     result = WithdrawService().submit_request(coin_id=json_data['coin_id'],network=network,to_coin_address=json_data['to_coin_address'],tag=json_data['tag'],amount=json_data['amount'],unique_id=json_data['unique_id'],signature=json_data['signature'])
    
#     ExchangerLogger.log_incoming_request(url=request.build_absolute_uri(),payload=json_data,response=result)

#     return HttpResponse(json.dumps(result))
    
