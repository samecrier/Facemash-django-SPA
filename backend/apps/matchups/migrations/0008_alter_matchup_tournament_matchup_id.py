# Generated by Django 4.2.16 on 2024-12-22 03:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0015_remove_roundcompetitor_delta_tournament_and_more'),
        ('matchups', '0007_matchup_tournament_matchup_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='tournament_matchup_id',
            field=models.ForeignKey(blank=True, db_column='tournament_matchup_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matchups', to='tournaments.tournamentmatchup'),
        ),
    ]
