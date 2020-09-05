import datetime
import pytz


def convert_to_datetime(date):
    modified_time = datetime.datetime(date.year, date.month, date.day,
                                      datetime.datetime.now().hour, datetime.datetime.now().minute,
                                      datetime.datetime.now().second, datetime.datetime.now().microsecond)
    return zonify_date(modified_time)


def convert_to_start_datetime(date):
    modified_time = datetime.datetime(date.year, date.month, date.day,
                                      0, 0,
                                      0, 0)
    return zonify_date(modified_time)


def convert_to_end_datetime(date):
    modified_time = datetime.datetime(date.year, date.month, date.day,
                                      23, 59,
                                      59, 999999)
    return zonify_date(modified_time)


def zonify_date(date):
    local_time = pytz.timezone('US/Eastern')
    zonified_date = local_time.localize(date)
    return zonified_date
