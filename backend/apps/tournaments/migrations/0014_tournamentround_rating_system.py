# Generated by Django 4.2.16 on 2024-12-21 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0013_remove_tournamentround_rating_system_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentround',
            name='rating_system',
            field=models.CharField(default='elo_32', max_length=255),
        ),
    ]