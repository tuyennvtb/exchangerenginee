from django.core.management.base import BaseCommand, CommandError

from ....BMExchanger.tasks_withdraw import update_withdraw_status

class Command(BaseCommand):

    def handle(self, *args, **options):
        update_withdraw_status()
