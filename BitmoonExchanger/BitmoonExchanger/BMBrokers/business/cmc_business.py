from ..brokers.coinmarketcap import CoinMarketCap
from ...BMUtils.utils.datetime_utils import DatetimeUtils
from ...BMUtils.utils.database_utils import DatabaseUtils

from ..models import CoinMarketCapModel,CoinMarketCapPairModel,BrokerCoinPriceModel


import pandas as pd
from sentry_sdk import capture_exception


class CoinMarketcapBusiness:
    def __init__(self,brokers=[]):
        self.brokers = brokers


    def setup(self):
        
        self.coin_listing()
        
        self.market_listing()
        
    def coin_listing(self):
        try:
            coinmarketcap = CoinMarketCap()
            listings = coinmarketcap.coin_listing()

            #print(listings)

            if listings and 'data' in listings:
                data = listings['data']

                # print(data)
                df = pd.DataFrame(data)

                df['name'] = df.name.str.decode('utf-8')
                df['symbol'] = df.symbol.str.decode('utf-8')


                

                #df = df.set_index('id')

                #{'USD': {'price': 9558.55163723, 'volume_24h': 13728947008.2722, 'percent_change_1h': -0.127291, 'percent_change_24h': 0.328918, 'percent_change_7d': -8.00576, 'market_cap': 171155540318.86005, 'last_updated': '2019-08-30T18:51:28.000Z'}}
                #Drop Unrelated columns
                
                df['coin_id'] = df.slug            
                df['cmc_date_added'] = [DatetimeUtils.formatTime(DatetimeUtils.parseDate(dt)) for dt in df.date_added]
                df['cmc_last_updated'] = [DatetimeUtils.formatTime(DatetimeUtils.parseDate(dt)) for dt in df.last_updated]

                df['coin_id'] = df.slug            
                df['currency_id'] = df.id
                df['cmc_rank'] = df.cmc_rank
                df['price_usd'] = [ quote['USD']['price'] for quote in df.quote]
                df['volume_usd_24h'] = [ quote['USD']['volume_24h'] for quote in df.quote]
                df['percent_change_1h'] = [ quote['USD']['percent_change_1h'] for quote in df.quote]
                df['percent_change_24h'] = [ quote['USD']['percent_change_24h'] for quote in df.quote]
                df['percent_change_7d'] = [ quote['USD']['percent_change_7d'] for quote in df.quote]
                df['market_cap'] = [ quote['USD']['market_cap'] for quote in df.quote]
                
                df['created_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
                df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

                df = df.drop(columns=['slug','id','date_added','last_updated','num_market_pairs','tags','circulating_supply','max_supply','total_supply','platform','cmc_rank','quote'],axis=1)

                df = df.fillna(0)

                df.loc[(df.percent_change_7d>1000),'percent_change_7d']= 1000




                
                DatabaseUtils.bulk_upsert(CoinMarketCapModel,df)
        except Exception as e:
            capture_exception(e)
            #TODO: RAISE LOG HERE
            pass

    def market_listing(self):
                
        for broker in self.brokers:
            broker_instance = broker()            
            self._market_listing_by_broker(broker_instance.broker_id)

    def _market_listing_by_broker(self,broker_id):
        coinmarketcap = CoinMarketCap()
        listings = coinmarketcap.market_listing(broker_slug=broker_id)

        if listings and 'data' in listings:
            data = listings['data']
            if 'market_pairs' not in data:
                return 
            market_pairs = data['market_pairs']

            pairs = []
            for market_pair in market_pairs:                
                pairs.append({
                    'market_pair': market_pair['market_pair'],
                    'base_currency': market_pair['market_pair_quote']['exchange_symbol'],
                    'market_currency': market_pair['market_pair_base']['exchange_symbol'],
                    'market_currency_id': market_pair['market_pair_base']['currency_id']                    
                })

            df  = pd.DataFrame(pairs)
            df['broker_id'] = broker_id
            df['created_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())
            df['updated_at'] = DatetimeUtils.formatTime(DatetimeUtils.getCurrentTime())

            df = df.fillna(0)

            DatabaseUtils.bulk_upsert(CoinMarketCapPairModel,df)

        



            

