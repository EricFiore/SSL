from datetime import timedelta, date
from django import template

register = template.Library()


@register.inclusion_tag('tracking/calendar.html', name='cal_fill')
def cal_fill(days):
    """accepts a dictionary of datetime: count and returns a dictionary padded with days starting at the
    Sunday before the first datetime and ending on the Saturday after the last datetime.
    EX: days 7/1/20: 5, 7/2/20: 10, 7/3/30: 7 are passed in.  output is the three included days
    padded with 6/28/20, 6/29/20, 6/30/20, and 7/4/20"""
    calendar = {}
    week = 1
    weekday = [day for day in sorted(days)]
    calendar[week] = {}

    # insert blank days into calendar that occur before passed in days starting at Sunday
    for day in range(weekday[0].weekday() % 6):
        calendar[week][weekday[day] - timedelta(days=weekday[0].weekday() + 1)] = None
    # for extra day if days needed to be padded
    if calendar[week] or weekday[0].weekday() == 0:
        calendar[week][weekday[0] - timedelta(days=1)] = None

    # insert passed in days into calendar
    for day in weekday:
        calendar[week][day] = days[day]
        # if change to new week
        if (day + timedelta(days=1)).weekday() == 6:
            week += 1
            calendar[week] = {}

    # insert blank days into calendar that occur after passed in days ending on Saturday
    # if time requested ends on Sunday then skip
    if weekday[len(weekday) - 1].weekday() != 5:
        following_day = weekday[len(weekday) - 1] + timedelta(days=1)
        for day in range(7 - (following_day.weekday() + 1) % 7):
            calendar[week][weekday[len(weekday) - 1] + timedelta(days=day + 1)] = None

    return {'cal': calendar}
