from django.db import models


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=200)

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
    round_number = models.IntegerField(default=-1)
    already_read = models.BooleanField(default=False)
    file_content = models.FileField(blank=False)

    def __str__(self):
        return "{} (prebrano: {})".format(self.file_content.name, self.already_read)
