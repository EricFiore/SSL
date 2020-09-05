from django.db import models
import uuid
from resolutions.models import CustomFixes, TechTipFix, ManualFix
from users.models import Profile


class CustomFixComments(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(max_length=3000, unique=False, editable=True, blank=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_comment_made = models.DateTimeField(auto_now_add=True)
    fix = models.ForeignKey(CustomFixes, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} {self.fix.id_number}'


class TechTipComment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(max_length=3000, unique=False, editable=True, blank=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_comment_made = models.DateTimeField(auto_now_add=True)
    tech_tip = models.ForeignKey(TechTipFix, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} {self.tech_tip.tech_tip_number}'


class ManualFixComment(models.Model):
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.TextField(max_length=3000, unique=False, editable=True, blank=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date_comment_made = models.DateTimeField(auto_now_add=True)
    manual_fix = models.ForeignKey(ManualFix, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} {self.manual_fix.manual_fix_id}'
