from django import forms
from . import models


class MatchForm(forms.ModelForm):
    class Meta:
        model = models.Match
        fields = {'status', 'first_team_score', 'second_team_score'}


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = {'file_content'}


class InformationForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = {'info'}