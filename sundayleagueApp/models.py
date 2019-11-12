from django.db import models


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=200)
    league = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Round(models.Model):
    round_number = models.IntegerField(default=0)
    place = models.CharField(max_length=200)
    date = models.DateField()
    league_number = models.IntegerField(default=0)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return "KROG. {} - {} ({})".format(
            self.round_number, self.place, self.home_team.__str__())


class Match(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    first_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='first_team')
    second_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='second_team')
    time = models.TimeField()
    first_team_score = models.IntegerField(null=True, blank=True)
    second_team_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "{} ({}-{}) {}".format(self.first_team, self.first_team_score, self.second_team_score,  self.second_team)


class File(models.Model):
    is_fixture = models.BooleanField(default=False)
    already_read = models.BooleanField(default=False)
    file_content = models.FileField(blank=False)

    def __str__(self):
        return "{} (prebrano: {})".format(self.file_content.name, self.already_read)


class TableRow(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, unique=True)
    league = models.IntegerField(default=1)
    match_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return "{} (GD:{} PT:{})".format(self.team, (self.goals_for - self.goals_against), self.points)
