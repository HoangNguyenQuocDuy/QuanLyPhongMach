# Generated by Django 4.2.9 on 2024-01-30 07:00

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qlpmapp', '0005_remove_administrator_role_remove_doctor_role_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicine',
            name='active_substances',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='medicine',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, null=True, verbose_name='medicine'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='medicine',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='medicine',
            name='unit',
            field=models.CharField(default=0, max_length=50),
        ),
        migrations.AlterField(
            model_name='medicine',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
