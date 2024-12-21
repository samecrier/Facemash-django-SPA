# Generated by Django 4.2.16 on 2024-12-20 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0003_alter_tournamentcompetitor_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roundcompetitor',
            name='status',
            field=models.CharField(choices=[('qualified', 'qualified'), ('eliminated', 'eliminated'), ('in schedule', 'in schedule'), ('not played', 'not played')], default='not played', max_length=255),
        ),
    ]
