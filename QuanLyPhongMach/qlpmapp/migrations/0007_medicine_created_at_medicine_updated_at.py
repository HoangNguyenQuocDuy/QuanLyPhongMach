# Generated by Django 4.2.9 on 2024-01-30 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qlpmapp', '0006_medicine_active_substances_medicine_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicine',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='medicine',
            name='updated_at',
            field=models.DateField(auto_now=True),
        ),
    ]