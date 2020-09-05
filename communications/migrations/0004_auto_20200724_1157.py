# Generated by Django 3.0.5 on 2020-07-24 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0003_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='reply_to',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='communications.Message'),
        ),
    ]
