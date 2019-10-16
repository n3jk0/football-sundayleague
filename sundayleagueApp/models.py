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

    def __str__(self):
        return "{} - {}".format(self.first_team.__str__(), self.second_team.__str__())


class Result(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    first_team_score = models.IntegerField(default=0)
    second_team_score = models.IntegerField(default=0)

    def __str__(self):
        return "{} : {}".format(self.first_team_score.__str__(), self.second_team_score.__str__())


class File(models.Model):
    file_name = models.CharField(max_length=200)
    file_content = models.FileField(blank=False)

    def __str__(self):
        return self.file_name

