from django.db import models
import uuid
from resolutions.models import TechTipFix
from PIL import Image


class TechTipPics(models.Model):
    tt_photo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo_caption = models.CharField(max_length=60, editable=True, unique=False)
    photo = models.ImageField(upload_to='tech_tip_pics')
    tech_tip_number = models.ForeignKey(TechTipFix, on_delete=models.CASCADE, editable=True,
                                        null=False, blank=False)

    def __str__(self):
        return f'{self.photo_caption} for {self.tech_tip_number.tech_tip_number}'

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.photo.path)
        if img.height >= 1000 or img.width >= 1000:
            output_size = (1000, 1000)
            img.thumbnail(output_size)
        elif img.height <= 800 or img.width <= 800:
            print(img.height)
            print(img.width)
            output_size = (800, 800)
            img.thumbnail(output_size)
            print(f'after {img.height} {img.width}')
        img.save(self.photo.path)
