# Generated by Django 5.1 on 2024-08-25 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdf_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScenarioModel',
            fields=[
                ('scenario_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('upload_date', models.DateTimeField()),
                ('serialized_scenario', models.FileField(max_length=200, upload_to='internal/pickled_scenarios/%Y%m%d/')),
            ],
        ),
        migrations.DeleteModel(
            name='File',
        ),
    ]