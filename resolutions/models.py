from django.db import models
import uuid
from django.template.defaultfilters import slugify
from django.urls import reverse
from users.models import Profile
from library.models import ProductModel
from library.datum import alphanumeric_generator


class Error(models.Model):
    error_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    error_name = models.CharField(max_length=100, editable=True, unique=True,
                                  help_text='A simple description of the issue. Should be simple to search for this.'
                                            'EX: H4-02 or black line')
    slug = models.SlugField(null=False, unique=True)
    created_on_date = models.DateTimeField(auto_now_add=True)
    error_title = models.CharField(max_length=200, editable=True, unique=False,
                                   help_text='A short description of the error')
    error_description = models.TextField(max_length=2000, editable=True, unique=False,
                                         help_text='A more detailed description of the issue: '
                                                   'Do not use for resolutions')

    class Meta:
        ordering = ['error_name']

    def __str__(self):
        return f'{self.error_name}'

    def get_absolute_url(self):
        return reverse('resolutions-error-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.error_name)
        return super().save(*args, **kwargs)


class TechTipFix(models.Model):
    tech_tip_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tech_tip_number = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(null=False, blank=True, unique=True)
    tech_tip_title = models.CharField(max_length=300, null=False, unique=False, editable=True)
    tech_tip_content = models.TextField(max_length=10000, editable=True)
    tech_tip_date = models.DateField()
    repairs_error = models.ManyToManyField(Error, editable=True, blank=False)
    model_id = models.ManyToManyField(ProductModel, editable=True, blank=False)

    def __str__(self):
        return f'{self.tech_tip_number}'

    def get_absolute_url(self):
        return reverse('resolutions-tech-tip-detail', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tech_tip_number)
        return super().save(*args, **kwargs)


class ManualFix(models.Model):
    manual_fix_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    steps_to_fix_error = models.TextField(max_length=3000, unique=False, editable=True)
    id = models.CharField(blank=False, max_length=8, default=alphanumeric_generator, editable=True, unique=True)
    slug = models.SlugField(null=False, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    model_id = models.ManyToManyField(ProductModel, editable=True, blank=False)
    repairs_error = models.ForeignKey(Error, on_delete=models.CASCADE, editable=True, blank=False)

    def __str__(self):
        return f'Manual fix for {self.repairs_error.error_name}'

    def get_absolute_url(self):
        return reverse('resolution-manual-detail', kwargs={"slug": self.slug})


class CustomFixes(models.Model):
    custom_fix_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_number = models.CharField(max_length=8, default=alphanumeric_generator, unique=True, blank=False)
    slug = models.SlugField(null=False, unique=True)
    symptoms = models.CharField(max_length=400, unique=False, editable=True, blank=False, help_text='Describe any symptoms that accompany error')
    steps_to_fix_error = models.TextField(unique=False, editable=True)
    created_on_date = models.DateTimeField(auto_now_add=True)
    modified_on_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    repairs_error = models.ManyToManyField(Error, editable=True, blank=False, help_text='Select one or multiple errors')
    model_id = models.ManyToManyField(ProductModel, editable=True, blank=False, help_text='select one or multiple models')

    def save(self, *args, **kwargs):
        if self.slug != self.id_number:
            self.slug = slugify(self.id_number)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.author}' + ' ' + f'{self.id_number}'

    def get_absolute_url(self):
        return reverse('user-fix-detail', kwargs={'slug': self.slug})
