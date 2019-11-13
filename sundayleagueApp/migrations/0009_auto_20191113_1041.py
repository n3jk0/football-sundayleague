# Generated by Django 2.2.6 on 2019-10-28 20:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sundayleagueApp', '0008_auto_20191028_2127'),
    ]

    operations = [
        migrations.CreateModel(
            name='TableRow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.IntegerField()),
                ('match_played', models.IntegerField()),
                ('wins', models.IntegerField()),
                ('draws', models.IntegerField()),
                ('losses', models.IntegerField()),
                ('goals_for', models.IntegerField()),
                ('goals_against', models.IntegerField()),
                ('points', models.IntegerField()),
                ('team', models.ForeignKey(on_delete=models.deletion.CASCADE, to='sundayleagueApp.Team',
                                           unique=True)),
            ],
        ),
    ]
