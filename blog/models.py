from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured = models.BooleanField(default=True)
    article_image = models.ImageField(default='article_pics\\default.jpg', upload_to='article_pics')

    def __str__(self):
        return f'{self.title} Article'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.article_image.path)
        if img.height > 600 or img.width > 900:
            output_size = (600, 900)
            img.thumbnail(output_size)
        img.save(self.article_image.path)

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={"pk": self.pk})
