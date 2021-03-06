# Generated by Django 2.2.6 on 2019-10-08 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_number', models.IntegerField(default=0)),
                ('place', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('league_number', models.IntegerField(default=0)),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sundayleagueApp.Team')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('first_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='first_team', to='sundayleagueApp.Team')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sundayleagueApp.Round')),
                ('second_team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_team', to='sundayleagueApp.Team')),
            ],
        ),
    ]
