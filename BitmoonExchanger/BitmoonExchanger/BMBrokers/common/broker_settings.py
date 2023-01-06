from ..brokers.broker_binance import BrokerBinance
from ..brokers.broker_huobi import BrokerHuobi
from ..brokers.broker_mxc import BrokerMXC

class Broker_Setting:
    BROKERS = [
            BrokerBinance,
            BrokerHuobi,
            BrokerMXC
        ]