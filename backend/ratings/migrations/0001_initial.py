# Generated by Django 4.2.16 on 2024-12-12 03:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('competitors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(default=1200)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('matchups', models.IntegerField(default=0)),
                ('tournaments', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('competitor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='competitors.competitor')),
            ],
        ),
    ]
