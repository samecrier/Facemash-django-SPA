# Generated by Django 4.2.16 on 2024-12-23 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0020_alter_templatetournament_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentround',
            name='rating_system',
            field=models.CharField(default='elo_64', max_length=255),
        ),
    ]