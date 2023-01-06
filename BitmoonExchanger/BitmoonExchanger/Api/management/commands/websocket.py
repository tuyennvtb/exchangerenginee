from django.core.management.base import BaseCommand, CommandError

from ....BMBrokers.services.broker_service import BrokerService
from ...services.schedule_service import Schedule_Service as CentralScheduleService
from ....BMExchanger.services.publishing_service import PublishingService

import warnings
warnings.filterwarnings("ignore")


class Command(BaseCommand):

    def handle(self, *args, **options):

        self.setup_markets()
        self.publish_coins()
        self.websocket()

    def websocket(self):
        service = BrokerService()
        service.start_websocket()

    def setup_markets(self):
        CentralScheduleService().setup()

    def publish_coins(self):
        PublishingService().publish_coins()