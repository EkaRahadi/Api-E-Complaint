# Generated by Django 3.0.5 on 2020-05-20 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiMobile', '0007_complaint_tanggapan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='tanggapan',
            field=models.TextField(blank=True, null=True),
        ),
    ]
