# Generated by Django 3.0.5 on 2020-06-27 04:11

import apiMobile.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiMobile', '0011_auto_20200626_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=apiMobile.models.upload_path),
        ),
    ]