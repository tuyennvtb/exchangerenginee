from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class CoinMarketCap:
    def __init__(self):
        self.api_key="927d385a-3652-4e93-86c7-6eef3ca0a913"
        self.host = "https://pro-api.coinmarketcap.com"

    def coin_listing(self):
        url = '{0}/v1/cryptocurrency/listings/latest'.format(self.host)
        parameters = {
        'start':'1',
        'limit':'5000',
        #'matched_symbol':'USDT'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return None

    def market_listing(self,broker_slug):
        
        url ="{0}/v1/exchange/market-pairs/latest".format(self.host)
        parameters = {
        'slug':broker_slug,
        'start':'1',
        'limit':'5000',
        #'matched_symbol':'USDT'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            return None
