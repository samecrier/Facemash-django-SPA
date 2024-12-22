# Generated by Django 4.2.16 on 2024-12-22 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0015_remove_roundcompetitor_delta_tournament_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='roundcompetitor',
            name='delta_round',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='roundcompetitor',
            name='delta_round_profile',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tournamentcompetitor',
            name='delta_tournament',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tournamentcompetitor',
            name='delta_tournament_profile',
            field=models.IntegerField(default=0),
        ),
    ]
