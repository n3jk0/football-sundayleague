# Generated by Django 2.2.6 on 2020-03-06 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0018_auto_20200306_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchgoals',
            name='assistant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assistant', to='sundayleagueApp.Player'),
        ),
    ]