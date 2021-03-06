# Generated by Django 2.2.6 on 2020-03-06 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0013_auto_20200306_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tablerow',
            name='draws',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='goals_against',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='goals_for',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='league',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='losses',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='match_played',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='team',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='sundayleagueApp.Team'),
        ),
        migrations.AlterField(
            model_name='tablerow',
            name='wins',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Result',
        ),
    ]
