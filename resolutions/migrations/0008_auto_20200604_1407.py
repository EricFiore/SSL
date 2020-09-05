# Generated by Django 3.0.5 on 2020-06-04 18:07

from django.db import migrations, models
import library.datum


class Migration(migrations.Migration):

    dependencies = [
        ('resolutions', '0007_auto_20200604_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualfix',
            name='slug',
            field=models.SlugField(default=library.datum.alphanumeric_generator, editable=False, max_length=8, unique=True),
        ),
    ]
