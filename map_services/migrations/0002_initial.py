# Generated by Django 5.1.7 on 2025-03-12 22:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('map_services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='routerequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='route',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='map_services.routerequest'),
        ),
    ]
