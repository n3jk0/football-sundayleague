from django import forms
from . import models


class MatchForm(forms.ModelForm):
    class Meta:
        model = models.Match
        fields = {'status', 'first_team_score', 'second_team_score'}

    def __init__(self, profile, disabled=False, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)
        if disabled:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True
        elif not profile.is_admin:
            self.fields['status'].choices = [(models.Match.MatchStatus.LIVE.name, models.Match.MatchStatus.LIVE.label), (models.Match.MatchStatus.COMPLETED.name, models.Match.MatchStatus.COMPLETED.label)]


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = {'file_content'}


class InformationForm(forms.ModelForm):
    class Meta:
        model = models.Information
        fields = {'info'}