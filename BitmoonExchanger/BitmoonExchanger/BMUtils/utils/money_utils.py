from .constants import CoinConstants
import math
class MoneyUtils:
    @classmethod
    def round_money(self,number,currency):
        #Default multiplier = 8
        decimals = 8
        if currency == CoinConstants.VND:
            decimals = 0
        
        if currency == CoinConstants.USDT:
            decimals = 5

        
        multiplier  = 10 ** decimals

        #Round anything to 8
        return math.ceil(number*multiplier)/multiplier