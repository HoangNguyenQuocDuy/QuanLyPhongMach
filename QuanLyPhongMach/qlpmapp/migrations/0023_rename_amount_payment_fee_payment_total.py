# Generated by Django 4.2.9 on 2024-02-28 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qlpmapp', '0022_rename_iscancel_appointment_examination'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='amount',
            new_name='fee',
        ),
        migrations.AddField(
            model_name='payment',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
