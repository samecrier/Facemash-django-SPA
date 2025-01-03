# Generated by Django 4.2.16 on 2024-12-18 09:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('competitors', '0002_alter_competitordetails_competitor'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoundCompetitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('qualified', 'qualified'), ('eliminated', 'eliminated'), ('not played', 'not played')], default='not played', max_length=255)),
                ('result', models.IntegerField(blank=True, choices=[(0, 'Lose'), (1, 'Win')], null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateTournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_name', models.CharField(max_length=255)),
                ('competitors_number', models.PositiveIntegerField()),
                ('rounds_number', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('available', 'available'), ('archieved', 'archieved')], default='available', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator_id', models.ForeignKey(db_column='creator_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='template_tournaments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TournamentBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('competitors_number', models.PositiveIntegerField()),
                ('rounds_number', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('not started', 'not started'), ('in progress', 'in progress'), ('completed', 'completed')], default='not started', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('profile_id', models.ForeignKey(db_column='profile_id', on_delete=django.db.models.deletion.CASCADE, related_name='tournaments', to=settings.AUTH_USER_MODEL)),
                ('template_tournament_id', models.ForeignKey(db_column='template_tournament_id', on_delete=django.db.models.deletion.PROTECT, related_name='tournaments', to='tournaments.templatetournament')),
                ('winner_id', models.ForeignKey(blank=True, db_column='winner_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tournaments_win', to='competitors.competitor')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentCompetitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'active'), ('eliminated', 'eliminated'), ('finished', 'finished')], max_length=255)),
                ('final_position', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competitor_id', models.ForeignKey(db_column='competitor_id', on_delete=django.db.models.deletion.CASCADE, related_name='tournaments_participation', to='competitors.competitor')),
                ('tournament_base_id', models.ForeignKey(db_column='tournament_base_id', on_delete=django.db.models.deletion.CASCADE, related_name='competitors', to='tournaments.tournamentbase')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentRatingSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_system_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TournamentSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TournamentRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.PositiveIntegerField()),
                ('competitors_in_matchup', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('not started', 'not started'), ('in progress', 'in progress'), ('completed', 'completed')], default='not started', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tournament_base_id', models.ForeignKey(db_column='tournament_base_id', on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='tournaments.tournamentbase')),
                ('winners', models.ManyToManyField(related_name='round_winners', to='tournaments.tournamentcompetitor')),
            ],
        ),
        migrations.CreateModel(
            name='TournamentMatchup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competitors_in_matchup', models.ManyToManyField(related_name='matchups', to='tournaments.roundcompetitor')),
                ('losers', models.ManyToManyField(related_name='matchup_losers', to='tournaments.roundcompetitor')),
                ('tournament_round_id', models.ForeignKey(db_column='tournament_round_id', on_delete=django.db.models.deletion.CASCADE, related_name='round_matchups', to='tournaments.tournamentround')),
                ('winner_id', models.ForeignKey(db_column='winner_id', on_delete=django.db.models.deletion.CASCADE, related_name='matchup_winner', to='tournaments.roundcompetitor')),
            ],
        ),
        migrations.CreateModel(
            name='TemplateRound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.PositiveIntegerField()),
                ('competitors_in_matchup', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('template_tournament_id', models.ForeignKey(db_column='template_round', on_delete=django.db.models.deletion.CASCADE, related_name='template_rounds', to='tournaments.templatetournament')),
                ('tournament_rating_system_id', models.ForeignKey(db_column='tournament_rating_system_id', on_delete=django.db.models.deletion.PROTECT, related_name='template_rounds', to='tournaments.tournamentratingsystem')),
            ],
        ),
        migrations.AddField(
            model_name='roundcompetitor',
            name='tournament_competitor_id',
            field=models.ForeignKey(db_column='tournament_competitor_id', on_delete=django.db.models.deletion.CASCADE, related_name='round_status', to='tournaments.tournamentcompetitor'),
        ),
        migrations.AddField(
            model_name='roundcompetitor',
            name='tournament_round_id',
            field=models.ForeignKey(db_column='tournament_round_id', on_delete=django.db.models.deletion.CASCADE, related_name='round_competitors', to='tournaments.tournamentround'),
        ),
    ]
