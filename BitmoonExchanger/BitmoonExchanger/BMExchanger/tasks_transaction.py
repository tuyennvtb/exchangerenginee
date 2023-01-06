import traceback
from celery import shared_task
import logging

from .business.fulfillment_business import Fulfillment




@shared_task
def fulfill_market_step(step_id):
    
    Fulfillment().process_market_step(step_id=step_id)

@shared_task
def fulfill_limit_step(step_id):
    Fulfillment().process_limit_step(step_id=step_id)

@shared_task
def fulfullment():
    Fulfillment().process_steps()

