# Generated by Django 4.2.9 on 2024-01-31 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qlpmapp', '0011_alter_appointment_nurse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescribedmedicine',
            name='instructions',
            field=models.CharField(default='Drink', max_length=50),
        ),
    ]
