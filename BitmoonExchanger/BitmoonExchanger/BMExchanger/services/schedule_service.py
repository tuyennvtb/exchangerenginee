from ...BMBrokers.models import BrokerCoinPriceModel
from ...BMUtils.utils.constants import BrokerConstants,TransactionStatusConstants
import pandas as pd

from ..models import ExchangerCoinSetting,ExchangerCoinPriceModel, ExchangerTransaction

from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.database_utils import DatabaseUtils
from ..business.transaction_business import TransactionBusiness
from datetime import timedelta

class ScheduleService:
    
    def __init__(self):
        pass

    def setup_coins(self):

       


        coins = BrokerCoinPriceModel.objects.values("coin_id","coin_name","coin_symbol","broker_id","status")

        if len(coins) == 0: 
            return


        df = pd.DataFrame(coins)
        df = df.dropna()

        df = df.sort_values(by=['status']).drop_duplicates(subset=['coin_id'],keep='last')

        
        df['created_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
        df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

        ExchangerCoinSetting.objects.bulk_create([
            ExchangerCoinSetting(
                coin_id=row['coin_id'],
                coin_name=row['coin_name'],
                coin_symbol = row['coin_symbol'],
                broker_id = row['broker_id'],
                status = row['status'],
                created_at = row['created_at'],
                updated_at = row['updated_at']


            )
            for index,row in df.iterrows()

        ],ignore_conflicts=True)

        ExchangerCoinPriceModel.objects.bulk_create([
            ExchangerCoinPriceModel(
                coin_id=row['coin_id'],
                coin_name=row['coin_name'],
                coin_symbol = row['coin_symbol'],
                broker_id = row['broker_id'],
                status = row['status'],
                created_at = row['created_at'],
                updated_at = row['updated_at']


            )
            for index,row in df.iterrows()

        ],ignore_conflicts=True)

    def retry_wallet(self):

        Now = DatetimeUtils.getCurrentTime()
        Yesterday = Now - timedelta(days=10)

        transactions = ExchangerTransaction.objects.filter(wallet_status__lte=0,wallet_request_count__lte=10,system_status=TransactionStatusConstants.DONE).all()
        for transaction in transactions:

            if transaction.updated_at < Yesterday:
                transaction.wallet_response="Close because failed to call update wallet for 1 day"
                transaction.wallet_request_count=100
                transaction.save()
            else:              
                TransactionBusiness(unique_id=transaction.unique_id).call_to_update_wallet()
            
            
            

    