# Generated by Django 3.0.5 on 2020-07-10 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0006_auto_20200710_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagedailyviews',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
