# Generated by Django 3.0.5 on 2020-07-02 15:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('resolutions', '0015_delete_customfixcomments'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualfix',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
