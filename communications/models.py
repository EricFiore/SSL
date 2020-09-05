from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User


class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, null=False)
    reply_to = models.OneToOneField('self', on_delete=models.CASCADE, blank=True, null=True)
    body = models.TextField(max_length=4000)
    date = models.DateTimeField(auto_now_add=True)
    send_to = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='receiver')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    slug = models.SlugField(null=False, blank=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.author.first_name} {self.author.last_name} sent message to {self.send_to.id} on {self.date}'
