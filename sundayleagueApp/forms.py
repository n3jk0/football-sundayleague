from django import forms
from . import models

class MatchForm(forms.ModelForm):
    class Meta:
        model = models.Match
        fields = {'first_team_score', 'second_team_score'}