# Generated by Django 4.2.16 on 2024-12-12 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competitors', '0001_initial'),
        ('matchups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='loser_id',
            field=models.ForeignKey(db_column='loser_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='losses', to='competitors.competitor'),
        ),
        migrations.AlterField(
            model_name='matchup',
            name='winner_id',
            field=models.ForeignKey(db_column='winner_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wins', to='competitors.competitor'),
        ),
    ]
