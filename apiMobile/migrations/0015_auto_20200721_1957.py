# Generated by Django 3.0.5 on 2020-07-21 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiMobile', '0014_complaint_jurusan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='jurusan',
            field=models.CharField(choices=[('Teknik Informatika', 'Teknik Informatika'), ('Teknik Mesin', 'Teknik Mesin'), ('Teknik Pendingin dan Tata Udara', 'Teknik Pendingin dan Tata Udara'), ('Keperawatan', 'Keperawatan')], default=None, max_length=200),
        ),
    ]