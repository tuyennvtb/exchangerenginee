from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.database_utils import DatabaseUtils

from ..models import CoinMarketCapModel,CoinMarketCapPairModel,BrokerCoinPriceModel,BrokerMarketPairModel, BrokerCoinMappingModel
from ...BMUtils.utils.constants import *
import pandas as pd

from sentry_sdk import capture_exception

class BrokerBusiness:
    def __init__(self,broker=None):
        self.broker = broker
        pass


    def get_markets(self):
        

        #Update to Market Table
        data = self.broker.get_markets()
        #Auto update All pair to 0
        
        df = pd.DataFrame(data)
        df['created_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
        df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

        #Update the pair again to 1
        df['status'] = 1
        BrokerMarketPairModel.objects.filter(broker_id=self.broker.broker_id).update(status=0)

        DatabaseUtils.bulk_upsert(BrokerMarketPairModel,df)


        coin_list_df = df.drop_duplicates(subset=['broker_id','market_currency'],keep='first')
        coin_list_df['coin_symbol'] = coin_list_df.market_currency
        coin_list_df = coin_list_df.drop(['market_pair','base_currency','market_currency','status','created_at','updated_at'],axis=1)
        
        BrokerCoinPriceModel.objects.filter(broker_id=self.broker.broker_id).update(status=0)

        DatabaseUtils.bulk_upsert(BrokerCoinPriceModel,coin_list_df)

        
        

        

    #Map coin using coin pairs in CMC
    def cmc_auto_mapping(self):

        pairs = CoinMarketCapPairModel.objects.values("broker_id","market_currency","market_currency_id")
        coins = CoinMarketCapModel.objects.values("currency_id","coin_id","name")

        df = pd.DataFrame(pairs)
        coin_df = pd.DataFrame(coins)

        coin_df = coin_df.set_index('currency_id')

        for broker_id in df.broker_id.unique():
            broker_df = df[df.broker_id == broker_id]
            broker_df = broker_df.drop_duplicates(subset='market_currency_id',keep='first').set_index('market_currency_id') 
            
            broker_df = broker_df.join(coin_df)

            broker_df['coin_name'] = broker_df.name
            broker_df['coin_symbol'] = broker_df.market_currency
            broker_df['status'] = 0

            broker_df['created_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
            broker_df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

            broker_df = broker_df.drop(columns=['name','market_currency'],axis=1)

            broker_df = broker_df.dropna()

            

            # DatabaseUtils.bulk_upsert(BrokerCoinPriceModel,broker_df)

            BrokerCoinMappingModel.objects.bulk_create([
                BrokerCoinMappingModel(
                    broker_id=row['broker_id'],
                    status = 1,
                    coin_id = row['coin_id'],
                    coin_name = row['coin_name'],
                    coin_symbol = row['coin_symbol'],
                    created_at = DatetimeUtils.getCurrentTime(),
                    updated_at = DatetimeUtils.getCurrentTime(),
                    description='Auto Mapping using CMC Market Pair'
                )
                for index, row in broker_df.iterrows()

            ],ignore_conflicts=True
            )



    
    #Automap if CMC has only one symbol
    def broker_auto_mapping(self):

        coins = CoinMarketCapModel.objects.values("currency_id","coin_id","symbol","name")

        market_pairs = BrokerMarketPairModel.objects.filter(broker_id=self.broker.broker_id).values("market_currency")

        coins_df = pd.DataFrame(coins)
        market_pair_df = pd.DataFrame(market_pairs)

        for idx, row in market_pair_df.iterrows(): 
            coin_filter = coins_df[coins_df.symbol == row['market_currency']].reset_index()
            if len(coin_filter)==1:                
                market_pair_df.loc[idx,'coin_id'] = coin_filter.loc[0,'coin_id']
                market_pair_df.loc[idx,'coin_name'] = coin_filter.loc[0,'name']
                


        market_pair_df = market_pair_df.dropna()

        broker_coin_price_df = market_pair_df.copy()
        broker_coin_price_df['coin_symbol'] = broker_coin_price_df.market_currency
        broker_coin_price_df['broker_id'] = self.broker.broker_id
        broker_coin_price_df['status'] = 1

        broker_coin_price_df = broker_coin_price_df.drop(columns=['market_currency'],axis=1)

        BrokerCoinMappingModel.objects.bulk_create([
                BrokerCoinMappingModel(
                    broker_id=row['broker_id'],
                    status = 1,
                    coin_id = row['coin_id'],
                    coin_name = row['coin_name'],
                    coin_symbol = row['coin_symbol'],
                    created_at = DatetimeUtils.getCurrentTime(),
                    updated_at = DatetimeUtils.getCurrentTime(),
                    description='Auto Mapping using CMC Market Single Pair'
                )
                for index, row in broker_coin_price_df.iterrows()

            ],ignore_conflicts=True
        )
        
    def update_coin_id_to_broker_price(self):
        mappings = BrokerCoinMappingModel.objects.values("broker_id","coin_id","coin_name","coin_symbol")
        mapping_df = pd.DataFrame(mappings)
        mapping_df = mapping_df.dropna()
        #Set to 0 because it will be set to 1 after 1 second
        mapping_df['status'] =0 
        DatabaseUtils.bulk_upsert(BrokerCoinPriceModel,mapping_df)

    def update_base_currency(self):        
        try:
            market_pairs_data = BrokerMarketPairModel.objects.values()
            market_pair_df = pd.DataFrame(market_pairs_data)
        
            
            market_pair_df['direct'] = 1
            #Find BTC coins , Set direct = 0
            market_pair_df.loc[market_pair_df.base_currency == CoinConstants.BITCOIN,'direct']  = 0
            

            market_pair_df = market_pair_df.sort_values(by='direct')
            market_pair_df = market_pair_df.drop_duplicates(subset=['broker_id','market_currency'],keep='last')

            market_pair_df = market_pair_df.set_index(['broker_id','market_currency'])
            
            
            coin_price_list = BrokerCoinPriceModel.objects.values("broker_id","coin_symbol","coin_id","base_currency")
            coin_price_list_df = pd.DataFrame(coin_price_list)

            coin_price_list_df=coin_price_list_df.set_index(['broker_id','coin_symbol'])
            
            coin_price_list_df.base_currency = market_pair_df.base_currency
            coin_price_list_df = coin_price_list_df.reset_index()
            # coin_price_list_df = coin_price_list_df?
            coin_price_list_df = coin_price_list_df.dropna()

            DatabaseUtils.bulk_upsert(model=BrokerCoinPriceModel,df=coin_price_list_df)
        except Exception as e:
            capture_exception(e)

        
        
            
                
