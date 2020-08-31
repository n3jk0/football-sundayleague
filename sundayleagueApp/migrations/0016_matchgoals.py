# Generated by Django 2.2.6 on 2020-03-06 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0015_auto_20200306_2107'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchGoals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assistant', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assistant', to='sundayleagueApp.Player')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sundayleagueApp.Match')),
                ('scorer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scorer', to='sundayleagueApp.Player')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sundayleagueApp.Team')),
            ],
        ),
    ]