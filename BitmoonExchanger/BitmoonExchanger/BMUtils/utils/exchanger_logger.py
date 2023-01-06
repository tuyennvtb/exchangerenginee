from ..models import Logger_Incoming_Request, Logger_Outgoing_Request, Logger_Transaction, Logger_Broker
from .datetime_utils import DatetimeUtils
import json
from sentry_sdk import capture_exception

class ExchangerLogger:
    @classmethod
    def log_incoming_request(cls,url, payload, response):
        try:
            r = Logger_Incoming_Request()
            r.url = url
            r.payload= json.dumps(payload)
            r.response = json.dumps(response)
            r.timestamp = DatetimeUtils.getCurrentTime()
            r.save()
        except Exception as e:
            capture_exception(e)
            pass

    @classmethod
    def log_outgoing_request(cls,url,payload,response_text):
        try:
            r = Logger_Outgoing_Request()
            r.url = url
            r.payload=json.dumps(payload)
            #Text
            r.response=response_text
            r.timestamp = DatetimeUtils.getCurrentTime()
            r.save()
        except Exception as e:
            capture_exception(e)
            

    @classmethod
    def log_transaction(cls,transaction_id,description):
        try:
            t = Logger_Transaction()
            t.transaction_id =transaction_id
            t.description = description
            t.timestamp = DatetimeUtils.getCurrentTime()
            t.save()
        except Exception as e:
            capture_exception(e)

    @classmethod
    def log_broker(cls,broker_id,message):
        try:
            b = Logger_Broker()
            b.broker_id = broker_id
            b.message = message
            b.timestamp = DatetimeUtils.getCurrentTime()
            b.save()
        except Exception as e:
            capture_exception(e)
            
        
