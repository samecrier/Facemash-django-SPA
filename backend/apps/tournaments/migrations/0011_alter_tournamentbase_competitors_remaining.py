# Generated by Django 4.2.16 on 2024-12-21 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0010_tournamentbase_competitors_remaining'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentbase',
            name='competitors_remaining',
            field=models.PositiveIntegerField(),
        ),
    ]