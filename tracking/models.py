import uuid
from django.utils.timezone import now
from django.db import models


class PageView(models.Model):
    page_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.URLField()
    page_category = models.CharField(max_length=300, blank=False, null=False)
    page_identifier = models.CharField(max_length=250, blank=False, null=False)
    num_page_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.page} , {self.num_page_views}'

    def increment_page_views(self):
        self.num_page_views += 1
        self.save()

    class Meta:
        ordering = ['pagehit__date']


class PageHit(models.Model):
    hit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(PageView, editable=False, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now, editable=False)
    ip = models.GenericIPAddressField()
    visitor = models.CharField(max_length=50)
    session = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.page.page} , {self.visitor}'

    class Meta:
        ordering = ['-date']


class PageDailyViews(models.Model):
    daily_view_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(PageView, editable=False, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_page_views = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.page.page}, {self.date}, {self.total_page_views}'

    class Meta:
        ordering = ['date']


class PageRanking(models.Model):
    page_ranking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(PageView, editable=False, on_delete=models.CASCADE)
    date = models.DateTimeField()
    ranking = models.PositiveSmallIntegerField(unique_for_date=date)

    def __str__(self):
        return f'{self.page.page} on {self.date} with ranking {self.ranking}'

    class Meta:
        ordering = ['date']
