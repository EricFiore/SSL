from django.db import models
import uuid
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from PIL import Image
from .datum import alphanumeric_generator


class ProductType(models.Model):
    type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_type = models.CharField(max_length=50, editable=True, unique=True)
    is_active = models.BooleanField(default=True, editable=True)
    product_description = models.CharField(max_length=500, editable=True)

    def __str__(self):
        return f'{self.product_type}'

    def get_absolute_url(self):
        return reverse('library-type')


class ProductFamily(models.Model):
    family_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(null=False, unique=True)
    family_name = models.CharField(max_length=50, editable=True, unique=True)
    family_description = models.CharField(max_length=500, editable=True)
    is_active = models.BooleanField(default=True, editable=True)
    type_id = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING, editable=True, null=False, blank=False)

    class Meta:
        ordering = ('family_name',)

    def __str__(self):
        return f'{self.family_name}'


class ProductModel(models.Model):
    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_number = models.CharField(max_length=25, editable=True, unique=True)
    slug = models.SlugField(null=False, unique=True)
    model_image = models.ImageField(default='library_pics\\default.jpg', upload_to='library_pics')
    model_description = models.TextField(max_length=5000, editable=True)
    production_start_date = models.DateField(editable=True, blank=True, null=True)
    production_end_date = models.DateField(editable=True, blank=True, null=True)
    family_id = models.ForeignKey(ProductFamily, on_delete=models.DO_NOTHING, editable=True, null=False, blank=False)

    class Meta:
        ordering = ['model_number']

    def __str__(self):
        return f'{self.family_id} : {self.model_number}'

    def get_absolute_url(self):
        return reverse('library-model-detail', kwargs={"type_id": self.family_id.type_id,  "slug": self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify(self.model_number)

        img = Image.open(self.model_image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
        img.save(self.model_image.path)


class FirmwareType(models.Model):
    firmware_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, editable=True, null=False, blank=False)
    type_description = models.TextField(max_length=2000, editable=True, blank=False)

    def __str__(self):
        return f'{self.type}'


class Firmware(models.Model):
    firmware_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_number = models.CharField(max_length=8, unique=True, blank=False, default=alphanumeric_generator)
    slug = models.SlugField(null=False, unique=True)
    version = models.CharField(max_length=50, help_text='The \'version number\' of the firmware',
                               editable=True)
    description = models.CharField(max_length=500, editable=True, null=False, blank=False)
    changes = models.TextField(max_length=15000, editable=True, null=False, blank=False)
    release_date = models.DateField(editable=True, blank=True, null=True)
    model_id = models.ManyToManyField(ProductModel, editable=True)
    firmware_type = models.ForeignKey(FirmwareType, on_delete=models.CASCADE, editable=True, null=False, blank=False)

    class Meta:
        ordering = ['-release_date']

    def __str__(self):
        return f'{self.firmware_type} : {self.version}'

    def get_absolute_url(self):
        return reverse('library-firmware-detail')


class Manual(models.Model):
    SERVICE = 'Service'
    INSTALLATION = 'Installation'
    PARTS = 'Parts'
    CIRCUIT = 'Circuit'
    OPERATION = 'Operation'
    QUICK_START = 'Quick Start'
    SOFTWARE_SETUP = 'Software Setup'
    MANUAL_CHOICES = [
        (SERVICE, 'Service'),
        (INSTALLATION, 'Installation'),
        (PARTS, 'Parts'),
        (CIRCUIT, 'Circuit'),
        (OPERATION, 'Operation'),
        (QUICK_START, 'Quick Start'),
        (SOFTWARE_SETUP, 'Software Setup')
    ]

    manual_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manual_name = models.CharField(max_length=50, editable=True, unique=False)
    manual_type = models.CharField(max_length=30, choices=MANUAL_CHOICES, default=SERVICE)
    manual_part_num = models.CharField(max_length=50, editable=True, unique=True)
    manual_download_link = models.URLField(max_length=200, editable=True)
    model_id = models.ManyToManyField(ProductModel, editable=True)

    def __str__(self):
        return f'{self.manual_name} : manual'

    def get_absolute_url(self):
        return reverse('manual')


class SupplyType(models.Model):
    supply_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supply_type = models.CharField(max_length=50, editable=True, unique=True, null=False)
    supply_type_description = models.TextField(max_length=500, editable=True, unique=False, null=False)

    def __str__(self):
        return f'{self.supply_type}'


class Supply(models.Model):
    supply_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supply_number = models.CharField(max_length=30, editable=True, unique=True, null=False)
    slug = models.SlugField(null=False, unique=True)
    supply_life = models.CharField(max_length=30, editable=True, unique=False, help_text='How long the supply lasts')
    supply_content = models.CharField(max_length=50, editable=True, unique=False,
                                      help_text="what comes with supply ex: black toner")
    supply_quantity = models.PositiveSmallIntegerField(unique=False, editable=True,
                                                       help_text="How many of the supply item is received upon ordering")
    supply_comments = models.TextField(max_length=400, unique=False, editable=True)
    model_id = models.ManyToManyField(ProductModel, editable=True)
    supply_type = models.ForeignKey(SupplyType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.supply_number}'

    def get_absolute_url(self):
        return reverse('library-supply-detail', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.supply_number)
        return super().save(*args, **kwargs)


class OptionType(models.Model):
    type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, editable=True, unique=True,
                            help_text='The type of option it is. EX: Document Feeder, Base, etc')
    slug = models.SlugField(null=False, unique=True)
    type_description = models.TextField(max_length=1000, editable=True,
                                        help_text='A brief description of the type the its functionality')
    model_id = models.ManyToManyField(ProductModel, editable=True)

    class Meta:
        ordering = ['type']

    def __str__(self):
        return f'{self.type}'

    def get_absolute_url(self):
        return reverse('library-option-type-detail')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type)
        return super().save(*args, **kwargs)


class Option(models.Model):
    option_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option_model_number = models.CharField(max_length=50, verbose_name='model number', editable=True, unique=True)
    slug = models.SlugField(null=False, unique=True)
    option_description = models.TextField(max_length=500, editable=True,
                                          help_text='A description of what the function of the option')
    model_id = models.ManyToManyField(ProductModel, through='OptionBelongsToModel')
    option_type = models.ForeignKey(OptionType, null=False, on_delete=models.DO_NOTHING)
    parent_option = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return f'{self.option_model_number}'

    def get_absolute_url(self):
        return reverse('library-option-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.option_model_number)
        return super().save(*args, **kwargs)


class OptionBelongsToModel(models.Model):
    product_model = models.ForeignKey(ProductModel, on_delete=models.DO_NOTHING)
    product_option = models.ForeignKey(Option, on_delete=models.DO_NOTHING)
    is_standard = models.BooleanField()
