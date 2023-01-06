import pytz
from datetime import datetime, timedelta
from dateutil import parser
from django.utils import timezone
import time




class DatetimeUtils:
    @classmethod
    def getCurrentTime(cls):
        return datetime.now(tz=timezone.utc)
    
    @classmethod
    def parseDate(cls,timestamp_str):
        return parser.parse(timestamp_str)
    
    @classmethod
    def formatTime(cls,timestamp):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def getUnixTime(cls):
        return time.time()

