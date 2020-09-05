# Generated by Django 3.0.5 on 2020-05-16 17:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200328_1143'),
        ('library', '0006_auto_20200513_1754'),
        ('resolutions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFixes',
            fields=[
                ('custom_fix_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('id_number', models.CharField(max_length=8, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('steps_to_fix_error', models.TextField(max_length=3000)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Profile')),
                ('model_id', models.ManyToManyField(to='library.ProductModel')),
                ('repairs_error', models.ManyToManyField(to='resolutions.Error')),
            ],
        ),
    ]
