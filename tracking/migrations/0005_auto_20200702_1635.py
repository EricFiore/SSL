# Generated by Django 3.0.5 on 2020-07-02 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_pagedailyviews'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagedailyviews',
            options={'ordering': ['-total_page_views']},
        ),
    ]
