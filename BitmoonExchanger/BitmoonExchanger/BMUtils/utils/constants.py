class CoinConstants: 
    BITCOIN = "BTC"
    USDT = "USDT"
    VND= "VND"
class CoinPairConstants:
    BTCUSDT="BTCUSDT"

class APIErrorCodeConstants:
    SUCCESS = "SUCCESS"
    INVALID_ACTION = "INVALID_ACTION"
    COIN_IS_NOT_SUPPORTED = "COIN_IS_NOT_SUPPORTED"
    COIN_IS_DISABLED = "COIN_IS_DISABLED"
    INVALID_BASE_CURRENCY = "INVALID_BASE_CURRENCY"
    AMOUNT_TOO_SMALL = "AMOUNT_TOO_SMALL"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_USER_ID = "INVALID_USER_ID"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_PRICE = "INVALID_PRICE"

    TRANSACTION_NOT_FOUND = "TRANSACTION_NOT_FOUND"
    TRANSACTION_IS_PROCESSING = "TRANSACTION_IS_PROCESSING"
    TRANSACTION_EXPIRED = "TRANSACTION_EXPIRED"


    INVALID_ADDRESS = "INVALID_ADDRESS"
    INVALID_UNIQUE_ID = "INVALID_UNIQUE_ID"

    PRICE_IS_NOT_UP_TO_DATE = "PRICE_IS_NOT_UP_TO_DATE"
    MAX_AMOUNT_REACHED = "MAX_AMOUNT_REACHED"

    INVALID_SIG = "INVALID_SIG"



class BrokerConstants: 
    BINANCE = "binance"

class AdminSettingConstants:
    USD_RATE_VND="USD_RATE_VND"
    USER_TRADING_FEE = "USER_TRADING_FEE"
    AUTO_CANCEL_VALUE = "AUTO_CANCEL_VALUE"
    ENABLE_WITHDRAW = "ENABLE_WITHDRAW"

class TransactionStatusConstants:
    NEW = "NEW"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    CANCELED = "CANCELED"
    OPEN = "OPEN"
    PROCESSING="PROCESSING"
    PARTIAL="PARTIAL"
    ERROR="ERROR"
    
    DONE="DONE"

class WithdrawRequestStatusConstants:

    OPEN = "OPEN"
    PROCESSING="PROCESSING"
    ERROR="ERROR"    
    SUBMITTED="SUBMITTED"
    DONE="DONE"


class BrokerOrderStatus:
    SUBMITTED = "SUBMITTED"
    FILLED="FILLED"
    MATCHED="MATCHED"
    FULFILL_MATCHED="FULFILL_MATCHED"
    CANCELED = "CANCELED"


class ExchangerModeConstants: 
    LIMIT="LIMIT"
    MARKET="MARKET"
    @classmethod
    def check_valid_mode(self,mode):
        return (mode in [ExchangerModeConstants.LIMIT,ExchangerModeConstants.MARKET])
             

class ExchangerTransactionType:
    BUY="BUY"
    SELL="SELL"

    @classmethod
    def check_valid_transaction_action(cls,action):
        return action.upper() in [cls.BUY,cls.SELL]

class CacheKey:
    COIN_STATUS_PREFIX="COIN_STATUS"
    BROKER_MARKET_PAIR_PREFIX="BROKER_MARKET_PAIR"
    BINANCE_PAIR_INFO_PREFIX="BINANCE_PAIR_INFO"
    HUOBI_PAIR_INFO_PREFIX="HUOBI_PAIR_INFO"
    TRANSACTION_SUBMIT_LOCKING="TRANSACTION_SUBMIT_LOCKING"
    TRANSACTION_LIMIT_PROCESS_LOCKING="TRANSACTION_LIMIT_PROCESS_LOCKING"
    TRANSACTION_MARKET_PROCESS_LOCKING="TRANSACTION_MARKET_PROCESS_LOCKING"
    TRANSACTION_WALLET_CALL_LOCKING = "TRANSACTION_WALLET_CALL_LOCKING"
    COIN_PRICE_SCHEDULE_PUBLISH_LOCKING = "COIN_PRICE_SCHEDULE_PUBLISH_LOCKING"
    CMC_INFO_CACHE_KEY = "CMC_INFO_CACHE_KEY"