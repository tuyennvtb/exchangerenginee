from ...BMBrokers.services.schedule_service import ScheduleService as BrokerScheduleService
from ...BMExchanger.services.schedule_service import ScheduleService as ExchangerScheduleService

class Schedule_Service:
    def __init__(self):
        pass

    def setup(self):
        BrokerScheduleService().setup_markets()
        ExchangerScheduleService().setup_coins()


