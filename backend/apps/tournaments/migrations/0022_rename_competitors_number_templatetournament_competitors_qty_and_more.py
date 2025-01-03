# Generated by Django 4.2.16 on 2024-12-27 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0021_alter_tournamentround_rating_system'),
    ]

    operations = [
        migrations.RenameField(
            model_name='templatetournament',
            old_name='competitors_number',
            new_name='competitors_qty',
        ),
        migrations.RenameField(
            model_name='templatetournament',
            old_name='rounds_number',
            new_name='rounds_qty',
        ),
        migrations.RenameField(
            model_name='tournamentbase',
            old_name='competitors_number',
            new_name='competitors_qty',
        ),
        migrations.RenameField(
            model_name='tournamentbase',
            old_name='rounds_number',
            new_name='rounds_qty',
        ),
        migrations.AddField(
            model_name='tournamentround',
            name='competitors_qty',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tournamentround',
            name='matchups_qty',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
