# Generated by Django 2.2.6 on 2020-03-06 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sundayleagueApp', '0014_auto_20200306_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.CharField(choices=[('GK', 'Vratar'), ('DEF', 'Branilec'), ('MID', 'Vezist'), ('FWD', 'Napadalec')], default='GK', max_length=3),
        ),
    ]
