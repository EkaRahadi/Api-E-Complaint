# Generated by Django 3.0.5 on 2020-04-21 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiMobile', '0003_auto_20200421_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='username',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
