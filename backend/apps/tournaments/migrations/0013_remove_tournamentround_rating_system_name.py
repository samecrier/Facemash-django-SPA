# Generated by Django 4.2.16 on 2024-12-21 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0012_roundcompetitor_delta_tournament_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournamentround',
            name='rating_system_name',
        ),
    ]
