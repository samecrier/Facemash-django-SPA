# Generated by Django 4.2.16 on 2024-12-16 04:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competitors', '0002_alter_competitordetails_competitor'),
        ('ratings', '0003_ratingprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='competitor_id',
            field=models.OneToOneField(db_column='competitor_id', on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='competitors.competitor'),
        ),
    ]
