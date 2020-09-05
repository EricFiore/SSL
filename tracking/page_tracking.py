from collections import Counter
import datetime
import math
from .models import PageHit, PageView, PageDailyViews, PageRanking
from .time_modification import convert_to_start_datetime, convert_to_end_datetime
from django.db.models import Count, Avg, StdDev


class DataTracking:

    def __init__(self, url, start_date, end_date):
        self._type_url = url
        self._start_date = start_date
        self._end_date = end_date
        self._previous_end_date, self._previous_start_date = self._get_previous_time_period()
        self._page_hits = PageHit.objects.filter(page__page_category=self._type_url). \
            filter(date__range=[self.start_date, self.end_date])
        self._total_previous_page_views, self._previous_page_views = self._get_last_time_period_views_per_page()
        self._total_current_page_views, self._current_page_views = self._get_number_of_views_per_page()

    def _get_previous_time_period(self):
        end_date = self.start_date - datetime.timedelta(minutes=1)
        start_date = end_date - (self.end_date - self.start_date)
        return end_date, start_date

    def _get_number_of_views_per_page(self):
        pages = {}
        total_page_views = 0

        for page in self.page_hits:
            page_id = page.page.page_identifier
            if page_id not in pages:
                pages[page_id] = {
                    'item_number': page_id,
                    'number_of_views': 1,
                    'last_person_to_view': page.visitor,
                    'dates_viewed': [
                        page.date
                    ]
                }
                total_page_views += 1
            else:
                pages[page_id]['number_of_views'] += 1
                if pages[page_id]['dates_viewed'][len(pages[page_id]['dates_viewed']) - 1] < page.date:
                    pages[page_id]['last_person_to_view'] = page.visitor
                pages[page_id]['dates_viewed'].append(page.date)
                total_page_views += 1

        return total_page_views, {key: pages[key] for (key, pages[key]) in sorted(pages.items(),
                                                                                  key=lambda x: x[1]['number_of_views'],
                                                                                  reverse=True)}

    def _get_last_time_period_views_per_page(self):
        pages = {}
        total_page_views = 0
        page_hits = PageHit.objects.filter(page__page_category=self.type_url).filter(date__range=
                                                                                     [self.previous_start_date,
                                                                                      self.previous_end_date])

        for page in page_hits:
            page_id = page.page.page_identifier
            if page_id not in pages:
                pages[page_id] = {
                    'item_number': page_id,
                    'number_of_views': 1,
                }
                total_page_views += 1
            else:
                pages[page_id]['number_of_views'] += 1
                total_page_views += 1

        return total_page_views, {key: pages[key] for (key, pages[key]) in sorted(pages.items(),
                                                                                  key=lambda x: x[1]['number_of_views'],
                                                                                  reverse=True)}

    def get_comparison_views_per_page(self):
        this_period_views = self.current_page_views
        last_period_views = self.previous_page_views

        for page in this_period_views:
            if page not in last_period_views:
                this_period_views[page]['change'] = None
                this_period_views[page]['previous_views'] = 0
                this_period_views[page]['current_percentage_views'] = \
                    round((this_period_views[page]['number_of_views'] / self.total_current_page_views) * 100, 1)
                this_period_views[page]['previous_percentage_views'] = None
            else:
                this_period_views[page]['change'] = \
                    int(round(((this_period_views[page]['number_of_views'] / last_period_views[page]['number_of_views'])
                               ) * 100, 0))
                this_period_views[page]['previous_views'] = last_period_views[page]['number_of_views']
                this_period_views[page]['current_percentage_views'] = \
                    round((this_period_views[page]['number_of_views'] / self.total_current_page_views) * 100, 1)
                this_period_views[page]['previous_percentage_views'] = \
                    last_period_views[page]['number_of_views'] / self.total_previous_page_views

        return this_period_views

    def get_percentile_views(self, percentile):
        """will return a sorted dictionary removing any items below the passed in percentile threshold
        that is passed in.  If multiple, same value, items happen to fall next to each other
        those will be kept together and not cut off"""
        if type(percentile) is not int:
            raise TypeError('int must be passed in; {} has been passed in'.format(type(percentile)))
        elif percentile > 99 or percentile < 1:
            raise ValueError('value is not within correct range')
        views = self.get_comparison_views_per_page()
        remaining_items = []

        for page in views:
            remaining_items.append(page)

        position = math.ceil((percentile / 100) * len(remaining_items))
        if position > 0:
            position -= 1
            # if multiple items are same value move down list until different value is found
            while (views[remaining_items[(len(remaining_items) - 1) - position]]['current_percentage_views']
                   ==
                   views[remaining_items[(len(remaining_items) - 1) - (position - 1)]]['current_percentage_views']):
                position = position - 1
                if position == 0:
                    break

        if position >= len(remaining_items):
            position = position - 1
        del remaining_items[len(remaining_items) - position:len(remaining_items)]

        return {key: views[key] for (key, views[key]) in views.items() if key in remaining_items}

    @property
    def type_url(self):
        return self._type_url

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def page_hits(self):
        return self._page_hits

    @property
    def current_page_views(self):
        return self._current_page_views

    @property
    def previous_page_views(self):
        return self._previous_page_views

    @property
    def total_current_page_views(self):
        return self._total_current_page_views

    @property
    def total_previous_page_views(self):
        return self._total_previous_page_views

    @property
    def previous_start_date(self):
        return self._previous_start_date

    @property
    def previous_end_date(self):
        return self._previous_end_date

    @type_url.setter
    def type_url(self, type_url):
        if PageView.objects.filter(page__contains=type_url):
            self._type_url = type_url
            self._page_hits = PageHit.objects.filter(page__page_category=type_url) \
                .filter(date__range=[self.end_date, self.start_date])
            self._current_page_views = self._get_number_of_views_per_page()
            self._previous_page_views = self._get_last_time_period_views_per_page()
        else:
            raise TypeError('The chosen URL is not in the database')

    @start_date.setter
    def start_date(self, date):
        if type(date) is not datetime.datetime:
            raise TypeError('start date must be datetime object')
        self._start_date = date
        self._page_hits = PageHit.objects.filter(page__page_category=self.type_url) \
            .filter(date__range=[self.end_date, date])
        self._current_page_views = self._get_number_of_views_per_page()
        self._previous_page_views = self._get_last_time_period_views_per_page()

    @end_date.setter
    def end_date(self, date):
        if type(date) is not datetime.datetime:
            raise TypeError('end date must be datetime object')
        self._end_date = date
        self._page_hits = PageHit.objects.filter(page__page_category=self.type_url) \
            .filter(date__range=[date, self.start_date])
        self._current_page_views = self._get_number_of_views_per_page()
        self._previous_page_views = self._get_last_time_period_views_per_page()


def get_first_save_dates():
    last_day = convert_to_end_datetime(datetime.datetime.now() - datetime.timedelta(days=1))
    first_hit = PageView.objects.first()
    dates = [page for page in sorted(first_hit.pagehit_set.all(), key=lambda x: x.date)]
    first_day = convert_to_start_datetime(dates[0].date)
    return first_day, last_day


def get_end_of_yesterday():
    return convert_to_end_datetime(datetime.datetime.now() - datetime.timedelta(days=1))


def record_active_pages():
    last_item_saved = PageDailyViews.objects.last()

    if not last_item_saved:
        first_day, last_day = get_first_save_dates()
        save_active_pages(last_day, first_day)
    elif last_item_saved.date < get_end_of_yesterday():
        last_day = get_end_of_yesterday()
        first_day = convert_to_end_datetime(last_item_saved.date)
        save_active_pages(last_day, first_day)
    else:
        return


def save_active_pages(last_day, first_day):
    while last_day > first_day:
        pages = PageHit.objects.filter(date__range=[last_day - datetime.timedelta(days=1), last_day])
        counts = Counter(page.page for page in pages)
        for key, item in counts.items():
            page_count = PageDailyViews(page=key, date=last_day, total_page_views=item)
            page_count.save()
        last_day -= datetime.timedelta(days=1)


def record_active_page_ranking():
    last_ranking_saved = PageRanking.objects.last()

    if not last_ranking_saved:
        first_day, last_day = get_first_save_dates()
        save_active_page_rankings(last_day, first_day)
    elif last_ranking_saved.date < get_end_of_yesterday():
        last_day = get_end_of_yesterday()
        first_day = convert_to_end_datetime(last_ranking_saved.date)
        save_active_page_rankings(last_day, first_day)
    else:
        return


def save_active_page_rankings(last_day, first_day):
    while last_day >= first_day:
        current_page_views = PageDailyViews.objects.filter(date__range=[convert_to_start_datetime(last_day),
                                                                        last_day])

        categories = {page.page.page_category for page in current_page_views}
        counts = {}
        # sorted by category to make debugging easier
        for category in categories:
            counts[category] = [page.page.page for page in sorted(current_page_views,
                                                                  key=lambda x: x.total_page_views,
                                                                  reverse=False)
                                if page.page.page_category == category]

        pages = {page.page.page: page.total_page_views for page in current_page_views}

        for key, value in counts.items():
            ranking = 0
            count = 0
            for page in value:
                if count != pages[page]:
                    ranking += 1
                page_ranking = PageRanking(page=PageView.objects.get(page=page), date=last_day, ranking=ranking)
                page_ranking.save()
                count = pages[page]
        last_day -= datetime.timedelta(days=1)


def get_daily_views(doc_type, period_start, period_end):
    one_day = datetime.timedelta(days=1)
    daily_count = {}

    while period_end >= period_start:
        count = PageView.objects.filter(page_category=doc_type) \
            .filter(pagehit__date__range=[period_end - one_day, period_end]).aggregate(Count('pagehit'))
        daily_count[period_end] = count['pagehit__count']
        period_end = period_end - one_day

    return daily_count


def get_all_pages_movement(url):
    """takes in the currently visited url and outputs outputs a a dictionary with specifying the
    relative movement of viewed pages over the past 5 weeks.  when a page is viewed less the
    associated movement score becomes smaller and may even become negative.  As a page gains
    views the associated movement score becomes larger.  All calculations are done during the
    workweek; ie Mon -> Fri.  If method is called during workweek the previous weeks data is
    used (2 Mondays ago).  If called during the weekend the Monday immediately previous is used.
    all rankings are normalized by dividing raw ranking by max ranking"""

    previous_monday = (convert_to_start_datetime(datetime.datetime.now()) -
                       datetime.timedelta(convert_to_start_datetime(datetime.datetime.now()).weekday()))
    monday = previous_monday
    if convert_to_start_datetime(datetime.datetime.now()).weekday() < 5:
        monday -= datetime.timedelta(days=7)
    friday = convert_to_end_datetime(monday + datetime.timedelta(days=4))
    earliest_monday = monday - datetime.timedelta(weeks=4)
    all_average_ranking = {}
    weeks = []

    # grab 5 weeks of average daily rankings; each week is Monday -> Friday
    while monday >= earliest_monday:
        average_ranking = PageView.objects.filter(page_category='/'.join(url.split('/')[0:3]) + '/') \
            .filter(pageranking__date__range=[monday, friday]).annotate(Avg('pageranking__ranking'))
        all_average_ranking[monday] = {page.page_identifier: page.pageranking__ranking__avg for page in average_ranking}
        weeks.append(monday)
        monday -= datetime.timedelta(weeks=1)
        friday -= datetime.timedelta(weeks=1)

    # create data structure to record all pages captured with a default score of 0
    page_scores = {page: 0 for week, item in all_average_ranking.items() for page in item}

    # start at earliest week and compare each page between current and following week.
    # if views increased add next weeks ranking / current weeks ranking
    # if views decreased subtract current weeks ranking / next weeks ranking
    current_week = len(weeks) - 1
    while current_week >= 1:
        for page in page_scores:
            if page in all_average_ranking[weeks[current_week]] \
                    and page in all_average_ranking[weeks[current_week - 1]]:
                current_week_ranking = (all_average_ranking[weeks[current_week]][page] /
                                        max(all_average_ranking[weeks[current_week]].values()))
                next_week_ranking = (all_average_ranking[weeks[current_week - 1]][page] /
                                     max(all_average_ranking[weeks[current_week - 1]].values()))
                if current_week_ranking <= next_week_ranking:
                    page_scores[page] += next_week_ranking / current_week_ranking
                else:
                    page_scores[page] += -(current_week_ranking / next_week_ranking)
        current_week -= 1

    return page_scores


def get_median_views(doc_type):
    return PageDailyViews.objects.filter(page__page_category=doc_type).aggregate(Avg('total_page_views'))


def get_std_dev_views(doc_type):
    return PageDailyViews.objects.filter(page__page_category=doc_type).aggregate(StdDev('total_page_views'))


def get_doc_daily_page_views(doc_type, page_identifier, period_start, period_end):
    return PageDailyViews.objects.filter(page__page_category=doc_type).filter(page__page_identifier=page_identifier) \
        .filter(page__pagehit__date__range=[period_start, period_end]).aggregate(Avg('total_page_views'))
