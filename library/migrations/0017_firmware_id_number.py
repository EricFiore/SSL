# Generated by Django 3.0.5 on 2020-05-26 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0016_remove_firmware_id_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmware',
            name='id_number',
            field=models.CharField(default='4B08A482', max_length=8, unique=True),
        ),
    ]
