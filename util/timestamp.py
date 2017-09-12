import time
from datetime import datetime, timedelta


def datetime_to_timestamp(date=None):
    if date is None:
        date = datetime.now()
    return int(time.mktime(date.timetuple()))


def timestamp_to_datetime(timestamp):
    if timestamp is None or timestamp == "":
        return None
    return datetime.fromtimestamp(int(timestamp))
